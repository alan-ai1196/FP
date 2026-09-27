"""Closed array operations for token phases in the existing CUDA arena.

Every device output has a fresh admitted extent. No advanced-index temporary,
allocator reset or device-side allocation is hidden behind an expression.
CPUArrays is a diagnostic interpreter and grants no physical authority.
"""
from fractions import Fraction as F
import math

from .binary_arithmetic import BinaryFormat, round_binary
from .core import ContractError, natural
from .resources import ResourceExceeded
from .semantics import ArithmeticUnresolved
from .cuda_storage import CudaWorkspace

SINGLE = BinaryFormat(24, -126, 127)
DTYPES = ('float16', 'float32', 'int64')


class _Arrays:
    def _shape(self, shape):
        if type(shape) is not tuple or any(type(n) is not int or n < 0 for n in shape):
            raise ContractError('complete exact nonnegative array shape required')
        if math.prod(shape) > self.element_cap:
            raise ArithmeticUnresolved('token array element allowance exhausted')
        return shape

    def _input(self, value):
        if self.cuda:
            if (type(value) is not self.xp.Tensor or value.device != self.workspace.arena.device
                    or value.requires_grad or not value.is_contiguous() or value.dtype not in self._dtypes.values()):
                raise ContractError('complete matching contiguous owned token tensor required')
            self.workspace.require_initialized(value)
        elif type(value) is not self.xp.ndarray or value.dtype not in self._dtypes.values():
            raise ContractError('complete supported CPU audit array required')
        self._shape(tuple(value.shape))

    def _new(self, shape, dtype, tag):
        self._shape(shape)
        if dtype not in self._dtypes:
            raise ContractError('unregistered token array format')
        cells = max(1, math.prod(shape))
        if self.cells+cells > self.cell_cap:
            raise ResourceExceeded('token phase output-cell allowance exhausted before allocation')
        self.cells += cells
        self.bytes += math.prod(shape)*{'float16': 2, 'float32': 4, 'int64': 8}[dtype]
        return (self.workspace.empty(shape, self._dtypes[dtype], 'token-'+tag) if self.cuda
                else self.xp.empty(shape, dtype=self._dtypes[dtype]))

    @staticmethod
    def dtype(value):
        return str(value.dtype).split('.')[-1]

    def _done(self, tag, value, *inputs):
        if self.cuda:
            self.workspace.written(value)
        self.records.append((tag, value))
        if self.audit is not None and tag in ('cast', 'add', 'sub', 'mul', 'div', 'ceil') and self.dtype(value) != 'int64':
            self.audit(tag, value, *inputs)
        return value

    def ingress(self, values, dtype):
        """Fixed host ingress: integers are exact; float values are explicit words."""
        import numpy as np
        raw = np.asarray(values)
        if dtype == 'int64':
            if raw.dtype.kind not in 'iu' or np.any(raw < -(1 << 62)) or np.any(raw >= 1 << 62):
                raise ContractError('bounded exact integer ingress required')
        elif dtype not in ('float16', 'float32') or raw.dtype != np.dtype(dtype) or not np.all(np.isfinite(raw)):
            raise ContractError('complete explicit finite floating ingress words required')
        result = self._new(tuple(raw.shape), dtype, 'ingress')
        if self.cuda:
            result.copy_(self.xp.tensor(raw.copy(), dtype=self._dtypes[dtype], device='cpu'))
        else:
            result[...] = raw
        return self._done('ingress', result)

    def rational(self, values):
        import numpy as np
        if type(values) is not tuple or any(type(x) not in (F, int) for x in values):
            raise ContractError('complete exact rational constant tuple required')
        cache = {x: round_binary(F(x), SINGLE, bit_limit=4096) for x in set(values)}
        rounded = [cache[x] for x in values]
        return self.ingress(np.asarray([-0.0 if x.negative_zero else float(x.value) for x in rounded], dtype=np.float32), 'float32')

    def constant(self, value):
        return self.reshape(self.rational((F(value),)), ())

    def zeros(self, shape, dtype='float32'):
        result = self._new(shape, dtype, 'zeros')
        result.zero_() if self.cuda else result.fill(0)
        return self._done('zeros', result)

    def reshape(self, value, shape):
        self._input(value)
        self._shape(shape)
        if math.prod(shape) != math.prod(value.shape):
            raise ContractError('token reshape changed its initialized extent')
        result = value.reshape(shape)
        if self.cuda:
            from .token_reuse import TokenReuseArena
            if type(self.workspace.arena) is TokenReuseArena:
                self.workspace.arena.derive(value, result)
        return result

    def copy(self, value):
        self._input(value)
        result = self._new(tuple(value.shape), self.dtype(value), 'copy')
        result.copy_(value) if self.cuda else self.xp.copyto(result, value)
        return self._done('copy', result)

    def cast(self, value, dtype):
        self._input(value)
        if dtype not in ('float16', 'float32'):
            raise ContractError('token floating cast requires half or single output')
        result = self._new(tuple(value.shape), dtype, 'cast')
        result.copy_(value) if self.cuda else self.xp.copyto(result, value, casting='unsafe')
        return self._done('cast', result, value)

    def _binary(self, tag, left, right):
        self._input(left)
        self._input(right)
        if left.dtype != right.dtype or self.dtype(left) not in ('float16', 'float32'):
            raise ContractError('matching floating operands required')
        shape = tuple(self.xp.broadcast_shapes(left.shape, right.shape))
        result = self._new(shape, self.dtype(left), tag)
        operation = dict(add='add', sub='subtract', mul='multiply', div='divide')[tag]
        getattr(self.xp, tag if self.cuda else operation)(left, right, out=result)
        return self._done(tag, result, left, right)

    def add(self, left, right):
        return self._binary('add', left, right)

    def sub(self, left, right):
        return self._binary('sub', left, right)

    def mul(self, left, right):
        return self._binary('mul', left, right)

    def div(self, left, right):
        return self._binary('div', left, right)

    def _indices(self, indices, count, *, distinct=False):
        import numpy as np
        if type(indices) is not tuple or any(type(i) is not int or not 0 <= i < count for i in indices):
            raise ContractError('complete declared row indices required')
        if distinct and len(set(indices)) != len(indices):
            raise ContractError('overlapping row writes have no deterministic token schedule')
        return self.ingress(np.asarray(indices, dtype=np.int64), 'int64')

    def take(self, value, indices):
        self._input(value)
        if not value.ndim:
            raise ContractError('token row read requires a row axis')
        index = self._indices(indices, value.shape[0])
        result = self._new((len(indices),)+tuple(value.shape[1:]), self.dtype(value), 'take')
        if self.cuda:
            self.xp.index_select(value, 0, index, out=result)
        else:
            self.xp.take(value, index, axis=0, out=result)
        return self._done('take', result)

    def replace_rows(self, value, indices, rows):
        self._input(value)
        self._input(rows)
        if not value.ndim or rows.dtype != value.dtype or tuple(rows.shape) != (len(indices),)+tuple(value.shape[1:]):
            raise ContractError('complete matching replacement rows required')
        index = self._indices(indices, value.shape[0], distinct=True)
        result = self._new(tuple(value.shape), self.dtype(value), 'replace-rows')
        if self.cuda:
            result.copy_(value)
            result.index_copy_(0, index, rows)
        else:
            result[...] = value
            result[index] = rows
        return self._done('replace-rows', result)

    def cat(self, values):
        if type(values) is not tuple or not values:
            raise ContractError('nonempty complete concatenation operands required')
        for value in values:
            self._input(value)
            if not value.ndim or value.dtype != values[0].dtype or value.shape[1:] != values[0].shape[1:]:
                raise ContractError('concatenation requires matching complete trailing axes')
        shape = (sum(v.shape[0] for v in values),)+tuple(values[0].shape[1:])
        result = self._new(shape, self.dtype(values[0]), 'cat')
        if self.cuda:
            self.xp.cat(values, dim=0, out=result)
        else:
            self.xp.concatenate(values, axis=0, out=result)
        return self._done('cat', result)

    def reduce(self, values):
        self._input(values)
        if not len(values):
            return self.zeros(tuple(values.shape[1:]), self.dtype(values))
        while len(values) > 1:
            pairs = len(values)//2
            left = self.take(values, tuple(range(0, 2*pairs, 2)))
            right = self.take(values, tuple(range(1, 2*pairs, 2)))
            following = self.add(left, right)
            values = self.cat((following, self.take(values, (len(values)-1,)))) if len(values) % 2 else following
        return self.reshape(values, tuple(values.shape[1:]))

    def segments(self, keys, values):
        """Stable grouped balanced sums; every write index is unique."""
        import numpy as np
        self._input(values)
        if type(keys) is not tuple or len(keys) != len(values) or any(type(k) is not int or k < 0 for k in keys):
            raise ContractError('one exact nonnegative segment key per input row required')
        order = tuple(sorted(range(len(keys)), key=keys.__getitem__))
        keys, values = np.asarray([keys[i] for i in order], dtype=np.int64), self.take(values, order)
        while np.any(keys[1:] == keys[:-1]):
            indices = np.arange(len(keys), dtype=np.int64)
            starts = np.r_[True, keys[1:] != keys[:-1]]
            within = indices-np.maximum.accumulate(np.where(starts, indices, 0))
            take = indices[within % 2 == 0]
            has_pair = (take+1 < len(keys)) & (keys[np.minimum(take+1, len(keys)-1)] == keys[take])
            tuple_of = lambda x: tuple(map(int, x))
            result = self.take(values, tuple_of(take))
            paired = self.add(self.take(values, tuple_of(take[has_pair])), self.take(values, tuple_of(take[has_pair]+1)))
            values = self.replace_rows(result, tuple_of(np.flatnonzero(has_pair)), paired)
            keys = keys[take]
        return tuple(map(int, keys)), values

    def scaled_master(self, value, bits):
        natural(bits, 'token master grid bits')
        if bits > 32:
            raise ArithmeticUnresolved('token grid realization exceeded')
        return self.mul(self.cast(value, 'float32'), self.constant(F(1, 1 << bits)))

    def columns(self, value):
        import numpy as np
        self._input(value)
        if self.dtype(value) != 'int64' or value.ndim != 2 or not 1 <= value.shape[0] <= 1 << 20:
            raise ContractError('bounded complete integer readout matrix required')
        actual = self.raw(value)
        if np.any(actual < 0) or np.any(actual >= 1 << 32):
            raise ArithmeticUnresolved('readout masters exceed exact column-total domain')
        result = self._new((value.shape[1],), 'int64', 'integer-columns')
        # A library CUDA reduction can allocate a private multi-block scratch
        # tensor even with out=. These explicit pair levels need no such
        # workspace. All partial sums are nonnegative and < 2**52, so every
        # int64 addition is exact; this does not change floating association.
        while len(value) > 1:
            pairs = len(value)//2
            left = self.take(value, tuple(range(0, 2*pairs, 2)))
            right = self.take(value, tuple(range(1, 2*pairs, 2)))
            following = self._new(tuple(left.shape), 'int64', 'integer-add')
            self.xp.add(left, right, out=following)
            self._done('integer-add', following)
            value = self.cat((following, self.take(value, (len(value)-1,)))) if len(value) % 2 else following
        source = self.reshape(value, tuple(value.shape[1:]))
        result.copy_(source) if self.cuda else np.copyto(result, source)
        return self._done('integer-columns', result)

    def project(self, q, gradient, scale):
        import numpy as np
        self._input(q)
        if self.dtype(q) != 'int64' or np.any(self.raw(q) < 0) or np.any(self.raw(q) >= 1 << 32):
            raise ContractError('complete uint32-valued int64 grid masters required')
        step = self.mul(gradient, scale)
        raw = self.raw(step)
        if not np.all(np.isfinite(raw)) or np.any(np.abs(raw) >= 1 << 62):
            raise ArithmeticUnresolved('token integer update shift envelope exhausted')
        rounded = self._new(tuple(step.shape), 'float32', 'ceil')
        self.xp.ceil(step, out=rounded)
        self._done('ceil', rounded, step)
        shift = self._new(tuple(step.shape), 'int64', 'integer-shift')
        shift.copy_(rounded) if self.cuda else np.copyto(shift, rounded, casting='unsafe')
        self._done('integer-shift', shift)
        result = self._new(tuple(self.xp.broadcast_shapes(q.shape, shift.shape)), 'int64', 'integer-project')
        if self.cuda:
            self.xp.sub(q, shift, out=result)
            self.xp.clamp(result, min=0, out=result)
        else:
            np.subtract(q, shift, out=result)
            np.maximum(result, 0, out=result)
        self._done('integer-project', result)
        if np.any(self.raw(result) >= 1 << 32):
            raise ArithmeticUnresolved('physical uint32 master envelope exhausted')
        return result

    def check(self):
        import numpy as np
        for _, value in self.records:
            if self.dtype(value) != 'int64' and not np.all(np.isfinite(self.raw(value))):
                raise ArithmeticUnresolved('nonfinite token array intermediate retained')
        if self.cuda:
            self.workspace.arena.check()


class CPUArrays(_Arrays):
    """Diagnostic interpreter; no owned physical or Runtime execution claim."""
    def __init__(self, *, element_cap, cell_cap, audit=None, grouped_reads=False, capture_view_cap=0):
        import numpy as np
        natural(element_cap, 'token array element cap', positive=True)
        natural(cell_cap, 'token phase output cell cap', positive=True)
        self.cuda, self.xp, self.audit = False, np, audit
        if type(grouped_reads) is not bool:
            raise ContractError('exact grouped-read registration required')
        self.grouped_reads = grouped_reads
        self.capture_view_cap = natural(capture_view_cap, 'capture view allowance', positive=grouped_reads)
        self.element_cap, self.cell_cap = element_cap, cell_cap
        self._dtypes = {name: getattr(np, name) for name in DTYPES}
        self.records, self.cells, self.bytes = [], 0, 0

    def raw(self, value):
        self._input(value)
        return value.copy()

    def capture(self, values):
        if type(values) is not tuple or len(values) > self.capture_view_cap:
            raise ResourceExceeded('complete resident view allowance exhausted')
        return _CapturedArrays(values, tuple(self.raw(value) for value in values))


class CudaArrays(_Arrays):
    """Actual fixed-arena executor. There is no unowned or CPU fallback path."""
    def __init__(self, workspace, readout_buffer, *, element_cap, cell_cap, grouped_reads=False, capture_view_cap=0):
        import torch
        from .token_reuse import TokenReuseWorkspace
        if type(workspace) not in (CudaWorkspace, TokenReuseWorkspace) or type(readout_buffer) is not bytearray:
            raise ContractError('actual owned arena phase and admitted readout bytes required')
        workspace._open()
        natural(element_cap, 'token array element cap', positive=True)
        natural(cell_cap, 'token phase output cell cap', positive=True)
        self.workspace, self.readout_buffer = workspace, readout_buffer
        if type(grouped_reads) is not bool:
            raise ContractError('exact grouped-read registration required')
        self.grouped_reads = grouped_reads
        self.capture_view_cap = natural(capture_view_cap, 'capture view allowance', positive=grouped_reads)
        self.cuda, self.xp, self.audit = True, torch, None
        self.element_cap, self.cell_cap = element_cap, cell_cap
        self._dtypes = {name: getattr(torch, name) for name in DTYPES}
        self.records, self.cells, self.bytes = [], 0, 0

    def raw(self, value):
        import numpy as np
        if self.dtype(value) not in self._dtypes:
            raise ContractError('registered token raw dtype required')
        self._shape(tuple(value.shape))
        payload = self.workspace.raw_bytes((value,), self.readout_buffer)[0]
        return np.frombuffer(payload, dtype=np.dtype(self.dtype(value))).reshape(tuple(value.shape))

    def capture(self, values):
        """All fresh named inputs of ONE read-only Resident.raw call."""
        import numpy as np
        if type(values) is not tuple:
            raise ContractError('complete immutable readback view tuple required')
        if len(values) > self.capture_view_cap:
            raise ResourceExceeded('complete resident view allowance exhausted')
        for value in values:
            if self.dtype(value) not in self._dtypes:
                raise ContractError('registered token raw dtype required')
            self._shape(tuple(value.shape))
        payloads = self.workspace.grouped_raw_bytes(values, self.readout_buffer)
        raw = tuple(np.frombuffer(data, dtype=np.dtype(self.dtype(value))).reshape(tuple(value.shape))
                    for value, data in zip(values, payloads, strict=True))
        return _CapturedArrays(values, raw)


class _CapturedArrays:
    """Local immutable images; expires with the enclosing single raw capture.

    No arithmetic, fallback, persistent memoization or snapshot issuance port.
    Inputs remain strongly bound by actual object identity throughout the call.
    """
    def __init__(self, values, raw):
        self._entries = {id(value): (value, data) for value, data in zip(values, raw, strict=True)}

    def raw(self, value):
        entry = self._entries.get(id(value))
        if entry is None or entry[0] is not value:
            raise ContractError('resident capture attempted an undeclared physical read')
        return entry[1]
