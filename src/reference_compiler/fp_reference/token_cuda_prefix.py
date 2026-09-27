"""Complete token phases inside the existing Runtime CUDA owner; no signer."""
from dataclasses import replace
from fractions import Fraction as F
import numpy as np

from .core import ContractError
from .resources import ResourceExceeded
from .semantics import ArithmeticUnresolved
from .token_execution import (TokenProgram, TokenInitializer, TokenLearner, TokenState,
                              TokenEvaluation, TokenReferenceMachine, closed)
from .token_sources import TokenValues
from .token_causal import TokenWindow
from .token_arrays import CPUArrays, CudaArrays
from .token_array_check import CheckedPrimitives
from .token_array_events import Kernel, Prepared
from .token_cuda_state import ArrayWords, Resident, PredictionResident, StateWords
from .token_enclosures import EnclosureUnresolved
from . import token_batch as ref, token_amp as amp, token_streaming as stream
from . import token_state_relation as states, token_readout_relation as readout, token_readout_envelope as envelope


def exact_diagnostics(value):
    """Preserve actual finite binary64 bound values in canonical exact frames.

    Numeric bound endpoints are rationals, not native floating state. Actual
    physical words (including signed zeros) remain in ArrayWords unchanged.
    """
    if type(value) is float:
        return F(value)
    if type(value) is dict:
        return {key: exact_diagnostics(child) for key, child in value.items()}
    if type(value) is tuple:
        return tuple(exact_diagnostics(child) for child in value)
    return value


def relation_work(program, cfg):
    d = program.definition
    edges = sum(len(n.terms) if hasattr(n, 'terms') else 2 for n in d.nodes)
    n = d.output.update_unit
    # Explicit primitive tariff, not a bit-time or complete Python-heap bound.
    # Covers full pending records/arrays, enclosure evaluation, raw reads and
    # finite exact-rounding fallbacks; physical host commitment stays binding.
    return 1024*(d.slot_count+n*(d.input_nodes+edges+len(d.nodes)+d.output.features+1)*
                 (n*d.sources.context+1).bit_length()+cfg.exact_cell_cap*4096+1)


def native_state(reference, cfg):
    closed(reference, TokenState)
    return (ref.Kernel(reference.origin.definition, element_cap=cfg.initializer.element_cap).prefix(
        reference.origin, reference.windows, reference.targets) if reference.unit_count else reference.origin)


def check_state(reference, raw, cfg):
    closed(raw, StateWords)
    d = reference.origin.definition
    if (raw.origin.definition != d or raw.cursor != reference.cursor or raw.unit_count != reference.unit_count
            or raw.source != reference.source or tuple(x.window for x in raw.leaves) != reference.windows
            or tuple(x.target for x in raw.leaves) != reference.targets):
        raise ContractError('token CUDA state lost its complete native records or clocks')
    return states.check(native_state(reference, cfg), raw.diagnostic(), amp.Arithmetic(),
                        states.Contract(cfg.state_atol, cfg.initializer.element_cap, cfg.exact_cell_cap))


def check_prediction(reference, native_prediction, resident, prediction, cfg, normalizer_cap, activation_cap):
    closed(native_prediction, TokenEvaluation)
    if native_prediction.before is not reference or native_prediction.window != prediction.window:
        raise ContractError('token CUDA relation lost the actual owned pre-target reference forecast')
    before = resident.diagnostic()
    bounds = ref.Kernel(reference.origin.definition, element_cap=cfg.initializer.element_cap).predict(
        native_state(reference, cfg), prediction.window)
    # Bind to the actual exact Runtime forecast, in addition to model/records.
    if (len(native_prediction.values) != len(bounds.values.lower)
            or any(not bounds.values.scalar((i, 0)).contains(value) for i, value in enumerate(native_prediction.values))
            or not bounds.normalizer.scalar(0).contains(native_prediction.normalizer)):
        raise ContractError('token prediction enclosure differs from the owned exact forecast')
    values = prediction.values.array().reshape((-1, 1))
    z = prediction.normalizer.array().reshape((1,))
    physical = amp.Prediction(before, prediction.window, values, z)
    numerical = amp.Kernel(reference.origin.definition, amp.Arithmetic(), element_cap=cfg.initializer.element_cap)
    # The prepared values have already passed their own executed-phase check.
    # The envelope independently binds the complete base operands again.
    numerical.base = resident.prepared[2].array()
    return exact_diagnostics(envelope.bound(bounds, physical, numerical, readout.PredictionContract(
        activation_cap, normalizer_cap, cfg.state_atol, cfg.probability_atol,
        cfg.probability_atol, 1, cfg.initializer.element_cap, cfg.exact_cell_cap)))


def window_from(sources, program, initializer):
    if type(sources) is not TokenValues or sources.context.family != initializer.sources:
        raise ContractError('token CUDA requires the actual owned indexed source interface')
    sources.context.__post_init__()
    return TokenWindow(program.definition.sources, sources.context.position, sources.context.past)


def fresh_origin(program, cfg, cursor, spec, rules, bit_limit):
    # Independently execute registered Gamma. A trained reference endpoint is
    # neither an argument nor an ingress to the physical learner.
    machine = TokenReferenceMachine(cfg.initializer)
    machine.require_program(program)
    theta = machine.initializer(program.slot_count, cfg.initializer)
    return machine.initial_state(program, rules, theta, cursor, spec=spec, bit_limit=bit_limit).origin


def transition(kind, program, cfg, before, prediction, window, target, cursor, origin, a):
    k = Kernel(program.definition, element_cap=cfg.initializer.element_cap)
    if kind == 'initialize':
        value = k.upload(origin, a)
        return Resident(value, k.prepare(value, a), None, a)
    if kind == 'predict':
        if before.state.cursor != cursor or (type(before.state) is stream.Pending
                and before.state.unit_count >= program.definition.output.update_unit):
            raise ContractError('token CUDA prediction requires its current eligible predecessor')
        return PredictionResident(before, k.predict(before.prepared, window, a), a)
    if kind == 'observe':
        if prediction.predecessor is not before or prediction.forecast.window != window:
            raise ContractError('token CUDA observation lost its actual physical predecessor/source')
        leaf = k.observe(before.prepared, prediction.forecast, window, target, a)
        pending = k.append(before.state if type(before.state) is stream.Pending else None, leaf, a)
        return Resident(pending, before.prepared, k.basis(pending, a), a)
    if kind == 'commit':
        value = k.commit(before.state, a)
        return Resident(value, k.prepare(value, a), None, a)
    if kind == 'attach':
        if type(before.state) is not amp.State or cursor % program.definition.output.update_unit:
            raise ContractError('token CUDA attachment requires a complete unit boundary')
        value = replace(before.state, cursor=cursor)
        return Resident(value, replace(before.prepared, origin=value), None, a)
    raise ContractError('unregistered owned token CUDA phase')


def execute(prefix, object_id, kind, program, candidate, reference, *, rules, spec, bit_limit,
            ordinary_cursor, origin, observation_id, sources, reference_prediction, target,
            normalizer_cap, activation_cap, source_domain, readout_buffer):
    from .cuda_prefix import IndexedCudaPhase
    cfg = prefix.contract
    source = prefix.staged if origin == 'profile' or kind == 'commit' else prefix.current
    input_id = None if kind == 'initialize' else source[candidate]
    prediction_id = prefix.predicted.get(candidate) if kind == 'observe' else None
    before = None if input_id is None else prefix._values[input_id]
    prediction = None if prediction_id is None else prefix._values[prediction_id]
    result, actual_prediction, error, relation = before, None, None, None
    a, workspace, window, before_raw, prediction_raw, actual_raw = None, None, None, None, None, None
    checker, checked, raw_operations = None, 0, ()
    try:
        closed(program, TokenProgram)
        program.validate(rules)
        closed(spec, TokenLearner)
        spec.__post_init__()
        closed(reference, TokenState)
        if (source_domain is not None or reference.origin.definition != program.definition
                or spec.output != cfg.initializer.output or program.definition.output != spec.output):
            raise ContractError('token CUDA lost its registered complete program/Gamma/U/source domain')
        TokenReferenceMachine(cfg.initializer).require_program(program)
        if before is not None:
            closed(before, Resident)
            for _, tensor in before.tensors():
                prefix.arena.require_initialized(tensor)
            before_raw = before.raw()
            if before_raw != prefix.phases[input_id].raw_state:
                raise ContractError('token CUDA predecessor or continuation cache changed after its owned phase')
        if prediction is not None:
            closed(prediction, PredictionResident)
            if (prediction.predecessor is not before or prefix.phases[prediction_id].input_phase != input_id
                    or prefix.phases[prediction_id].observation_id != observation_id):
                raise ContractError('token CUDA target lost its owned pre-target phase identity')
            prediction_raw = prediction.raw()
            if prediction_raw != prefix.phases[prediction_id].raw_prediction:
                raise ContractError('token CUDA pre-target words changed before observation')
        if kind in ('predict', 'observe'):
            window = window_from(sources, program, cfg.initializer)
        if kind == 'predict':
            check_state(reference, before_raw, cfg)
        if kind == 'observe' and (not reference.targets or reference.targets[-1] != target or reference.windows[-1] != window):
            raise ContractError('token CUDA observation differs from the owned revealed target/context')
        birth = fresh_origin(program, cfg, reference.cursor, spec, rules, bit_limit) if kind == 'initialize' else None
        # Check only the new operation graph. All earlier leaf/carry values come
        # from the immutable checked predecessor, rather than event replay.
        checker = CheckedPrimitives(cfg.exact_cell_cap)
        control = CPUArrays(element_cap=cfg.initializer.element_cap, cell_cap=cfg.phase_output_cells, audit=checker)
        cpu_before = None if before_raw is None else before_raw.cpu()
        cpu_prediction = (None if prediction_raw is None else
            PredictionResident(cpu_before, prediction_raw.cpu(cpu_before.prepared), control))
        expected = transition(kind, program, cfg, cpu_before, cpu_prediction, window, target,
                              reference.cursor, birth, control)
        control.check()
        with prefix.arena.phase(object_id) as workspace:
            a = CudaArrays(workspace, readout_buffer, element_cap=cfg.initializer.element_cap, cell_cap=cfg.phase_output_cells)
            actual = transition(kind, program, cfg, before, prediction, window, target, reference.cursor, birth, a)
            if kind == 'predict':
                actual_prediction = actual
            else:
                result = actual
            if (len(control.records), control.cells) != (len(a.records), a.cells):
                raise ContractError('token CUDA changed the complete registered output schedule')
            for (ctag, wanted), (tag, value) in zip(control.records, a.records):
                raw = a.raw(value)
                if (ctag, wanted.shape, wanted.dtype, wanted.tobytes()) != (tag, raw.shape, raw.dtype, raw.tobytes()):
                    raise ArithmeticUnresolved('token CUDA output differs from its guarded half/single decision')
                checked += raw.size
            a.check()
            actual_raw = actual.raw(a)
            if actual_raw != expected.raw(control):
                raise ContractError('token CUDA complete caches/state differ from the new checked transition')
            if kind == 'predict':
                relation = check_prediction(reference, reference_prediction, before_raw, actual_raw, cfg,
                                            normalizer_cap, activation_cap)
            else:
                relation = check_state(reference, actual_raw, cfg)
            if before is not None and before.raw(a) != before_raw:
                raise ContractError('token CUDA mutated a complete owned predecessor')
            if prediction is not None and prediction.raw(a) != prediction_raw:
                raise ContractError('token CUDA mutated its owned pre-target forecast')
    except MemoryError:
        raise
    except EnclosureUnresolved as exc:
        error = ArithmeticUnresolved(str(exc))
    except Exception as exc:
        error = exc
    if a is not None:
        raw_operations = tuple((tag, ArrayWords.capture(value, a)) for tag, value in a.records)
    record = IndexedCudaPhase(object_id, candidate, program.program_id, origin+':'+kind,
        ordinary_cursor, observation_id, input_id, prediction_id, reference, reference_prediction,
        None if result is None else result.raw(), None if actual_prediction is None else actual_prediction.raw(),
        raw_operations, relation, 0 if a is None else a.cells, None if workspace is None else workspace.index,
        'CHECKED_CUDA_PREFIX_PHASE' if error is None else
            'UNRESOLVED' if isinstance(error, (ResourceExceeded, ArithmeticUnresolved)) else 'EXECUTION_FAILED',
        '' if error is None else f'{type(error).__name__}: {error}', checked,
        execution_plan=dict(window=window, target=target, schedule=Kernel.schedule_id,
            readout_recipe=Kernel.readout_id,
            primitive_words=0 if checker is None else checker.words,
            exact_rounding_cells=0 if checker is None else checker.decoder.exact_cells))
    prefix._values[object_id] = actual_prediction if kind == 'predict' else result
    prefix.phases[object_id] = record
    return record, error
