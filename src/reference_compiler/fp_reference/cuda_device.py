"""Actual Windows CUDA identity and a conservative physical-board VRAM bound.

This charges the entire identified board to both roles, once globally. It
neither reserves exclusive memory nor estimates a process's allocation peak.
Native tensor history and process commitment retain their separate measures.
No caller observation, device handle or transport certificate is accepted.
"""
import ctypes as C
from dataclasses import dataclass, field
from pathlib import Path
import sys
from typing import Mapping

from .core import ContractError, freeze_data, natural
from .cuda_storage import CudaStorageUnresolved


@dataclass(frozen=True)
class CudaDeviceContract:
    vram_cap: int
    role_vram_caps: Mapping[str, int]
    runtime_version: int = 13040
    driver_api_version: int = 13040
    driver_version: str = '616.92'
    backend: str = field(default='windows-x64-CUDA-runtime-and-NVML-board-v1', init=False)
    ownership: str = field(default='whole-physical-board-VRAM-upper-shared-by-both-roles-v1', init=False)

    def __post_init__(self):
        natural(self.vram_cap, 'physical board VRAM cap', positive=True)
        if not isinstance(self.role_vram_caps, Mapping) or set(self.role_vram_caps) != {'deployment', 'compiler'}:
            raise ContractError('whole-board VRAM requires both preregistered roles')
        caps = {key: natural(value, 'role VRAM cap', positive=True) for key, value in self.role_vram_caps.items()}
        if max(self.vram_cap, *caps.values()) >= 1 << 63:
            raise ContractError('VRAM budget exceeds the registered integer domain')
        object.__setattr__(self, 'role_vram_caps', freeze_data(caps))
        for key in ('runtime_version', 'driver_api_version'):
            natural(getattr(self, key), 'actual CUDA '+key, positive=True)
        if type(self.driver_version) is not str or not 0 < len(self.driver_version) < 80:
            raise ContractError('bounded actual display-driver version required')
        if (self.backend != 'windows-x64-CUDA-runtime-and-NVML-board-v1'
                or self.ownership != 'whole-physical-board-VRAM-upper-shared-by-both-roles-v1'):
            raise ContractError('unimplemented CUDA device binding or resource interpretation')


@dataclass(frozen=True)
class CudaDeviceIdentity:
    runtime_version: int
    driver_api_version: int
    driver_version: str
    pci_bus_id: str
    uuid: str
    physical_vram_bytes: int


@dataclass(frozen=True)
class CudaDeviceSnapshot:
    contract: CudaDeviceContract
    identity: CudaDeviceIdentity
    physical_vram_upper: int
    role_physical_vram_upper: Mapping[str, int]
    scope: str = field(default='uniform physical-board VRAM residency upper; not measured process usage, exclusive availability, host backing or cumulative allocation volume', init=False)


class _Memory(C.Structure):
    # NVML v1 total explicitly denotes physical memory and includes the
    # driver/firmware reservation. Do not derive capacity from free/used.
    _fields_ = [('total', C.c_uint64), ('free', C.c_uint64), ('used', C.c_uint64)]


DEVICE_FIELDS = frozenset(('contract', 'ordinal', '_cudart', '_nvml', '_functions', 'initial'))


class _CudaDevice:
    def __init__(self, contract, ordinal):
        if type(contract) is not CudaDeviceContract:
            raise ContractError('immutable CUDA device registration required')
        contract.__post_init__()
        natural(ordinal, 'CUDA ordinal')
        if sys.platform != 'win32' or C.sizeof(C.c_void_p) != 8:
            raise CudaStorageUnresolved('registered device binding requires 64-bit Windows')
        import torch
        self.contract, self.ordinal = contract, ordinal
        try:
            self._cudart = C.CDLL(str(Path(torch.__file__).parent/'lib/cudart64_13.dll'))
            self._nvml = C.CDLL('nvml.dll', winmode=0x800)  # System32 only.
            specifications = (
                (self._cudart, 'cudaRuntimeGetVersion', [C.POINTER(C.c_int)]),
                (self._cudart, 'cudaDriverGetVersion', [C.POINTER(C.c_int)]),
                (self._cudart, 'cudaDeviceGetPCIBusId', [C.c_char_p, C.c_int, C.c_int]),
                (self._nvml, 'nvmlInit_v2', []), (self._nvml, 'nvmlShutdown', []),
                (self._nvml, 'nvmlDeviceGetHandleByPciBusId_v2', [C.c_char_p, C.POINTER(C.c_void_p)]),
                (self._nvml, 'nvmlDeviceGetMemoryInfo', [C.c_void_p, C.POINTER(_Memory)]),
                (self._nvml, 'nvmlDeviceGetUUID', [C.c_void_p, C.c_char_p, C.c_uint]),
                (self._nvml, 'nvmlSystemGetDriverVersion', [C.c_char_p, C.c_uint]),
            )
            self._functions = {}
            for library, key, arguments in specifications:
                function = getattr(library, key)
                function.argtypes, function.restype = arguments, C.c_int
                self._functions[key] = function
        except (OSError, AttributeError) as exc:
            raise CudaStorageUnresolved('registered native CUDA/NVML API unavailable') from exc
        self.initial = self._read()
        expected = (contract.runtime_version, contract.driver_api_version, contract.driver_version)
        if (self.initial.runtime_version, self.initial.driver_api_version, self.initial.driver_version) != expected:
            raise CudaStorageUnresolved('actual runtime/driver version differs from immutable registration')
        if self.initial.physical_vram_bytes > min(contract.vram_cap, *contract.role_vram_caps.values()):
            raise CudaStorageUnresolved('whole physical CUDA board exceeds a registered VRAM cap before tensor allocation')

    def _call(self, key, *arguments):
        result = self._functions[key](*arguments)
        if result != 0:
            raise CudaStorageUnresolved(f'{key} cannot establish its native premise (status {result})')

    def _read(self):
        runtime, driver_api = C.c_int(), C.c_int()
        bus, uuid, driver = C.create_string_buffer(32), C.create_string_buffer(96), C.create_string_buffer(80)
        self._call('cudaRuntimeGetVersion', C.byref(runtime))
        self._call('cudaDriverGetVersion', C.byref(driver_api))
        self._call('cudaDeviceGetPCIBusId', bus, len(bus), self.ordinal)
        self._call('nvmlInit_v2')
        try:
            handle, memory = C.c_void_p(), _Memory()
            self._call('nvmlDeviceGetHandleByPciBusId_v2', bus, C.byref(handle))
            if not handle.value:
                raise CudaStorageUnresolved('native CUDA-to-NVML device binding is empty')
            self._call('nvmlDeviceGetMemoryInfo', handle, C.byref(memory))
            self._call('nvmlDeviceGetUUID', handle, uuid, len(uuid))
            self._call('nvmlSystemGetDriverVersion', driver, len(driver))
        except BaseException:
            # Try to balance native observation lifetime, while preserving
            # an original executor/MemoryError even if cleanup also fails.
            try:
                self._call('nvmlShutdown')
            except BaseException:
                pass
            raise
        else:
            # No accumulated NVML initialization references or supplied
            # native handle survive a successful observation.
            self._call('nvmlShutdown')
        if not (runtime.value > 0 and driver_api.value > 0 and memory.total > 0 and bus.value and uuid.value and driver.value):
            raise CudaStorageUnresolved('native device identity or physical capacity is unavailable')
        return CudaDeviceIdentity(runtime.value, driver_api.value, driver.value.decode('ascii'),
                                  bus.value.decode('ascii'), uuid.value.decode('ascii'), memory.total)

    def check(self):
        current = self._read()
        if current != self.initial:
            raise CudaStorageUnresolved('the bound physical CUDA device, runtime, driver or capacity changed')
        return current

    def snapshot(self):
        value = self.check()
        return CudaDeviceSnapshot(self.contract, value, value.physical_vram_bytes,
            freeze_data({key: value.physical_vram_bytes for key in self.contract.role_vram_caps}))
