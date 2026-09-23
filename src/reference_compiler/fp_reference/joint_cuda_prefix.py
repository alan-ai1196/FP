"""Joint-noise phases inside the existing private CUDA owner; no signer."""
from dataclasses import replace

from .core import ContractError
from .resources import ResourceExceeded
from .semantics import ArithmeticUnresolved
from .float64_bridge import Float64Contract
from .indexed_execution import CategoricalPairDomain
from .joint_relation import JointRelation, initialize, commit, attach
from .joint_execution import JointLearner, closed
from .cuda_prefix import IndexedCudaPhase
from . import cuda_learner as gpu, joint_amp as joint


def execute(prefix, object_id, kind, program, candidate, reference, *, rules, spec, bit_limit,
            ordinary_cursor, origin, observation_id, sources, reference_prediction, target,
            normalizer_cap, activation_cap, source_domain, readout_buffer, workspace):
    source = prefix.staged if origin == 'profile' or kind == 'commit' else prefix.current
    input_id = None if kind == 'initialize' else source[candidate]
    prediction_id = prefix.predicted.get(candidate) if kind == 'observe' else None
    state = None if input_id is None else prefix._values[input_id]
    prediction = None if prediction_id is None else prefix._values[prediction_id]
    result, actual_prediction, error, relation = state, None, None, None
    arithmetic, arena_phase, plan, checked = None, None, None, 0
    before_raw = before_prediction = None
    try:
        closed(program, JointRelation)
        closed(spec, JointLearner)
        closed(source_domain, CategoricalPairDomain)
        spec.__post_init__()
        source_domain.__post_init__()
        if (program != prefix.contract.schema or spec.schema != program or source_domain.n != program.n):
            raise ContractError('joint CUDA lost its complete model/Gamma/U/domain registration')
        program.validate(rules)
        if state is not None:
            closed(state, joint.ResidentState)
            for _, tensor in state.tensors():
                prefix.arena.require_initialized(tensor)
            before_raw = state.raw()
            if before_raw != prefix.phases[input_id].raw_state:
                raise ContractError('joint CUDA predecessor differs from its owned phase')
        if prediction is not None:
            closed(prediction, joint.ResidentPrediction)
            if (prefix.phases[prediction_id].input_phase != input_id
                    or prefix.phases[prediction_id].observation_id != observation_id):
                raise ContractError('joint observation lost its actual pre-target phase or event identity')
            prefix.arena.require_initialized(prediction.readout)
            before_prediction = prediction.raw()
            if before_prediction != prefix.phases[prediction_id].raw_prediction:
                raise ContractError('joint CUDA prediction changed before actual target observation')
        if kind == 'predict':
            if workspace is None:
                raise ContractError('joint CUDA construction lost its prepaid integer extent')
            plan = joint._prepare_prediction(program, before_raw, rules, sources,
                output_cap=prefix.contract.phase_output_cells, budget=prefix.contract.partitions,
                workspace=workspace, bit_limit=bit_limit)
        expected_cells = plan.output_cells if kind == 'predict' else 6+8*len(program.rates) if kind == 'observe' else 0
        joint.allowance(max(1, expected_cells), prefix.contract.phase_output_cells, 'joint CUDA phase output allowance')
        scalar_bits = min(bit_limit, prefix.contract.partitions.integer_bits)
        with prefix.arena.phase(object_id) as arena_phase:
            arithmetic = gpu.CudaArithmetic(scalar_bits, prefix.contract.storage.device, workspace=arena_phase,
                output_cell_limit=prefix.contract.phase_output_cells, readout_buffer=readout_buffer)
            scalar = joint._Arithmetic(scalar_bits, arithmetic)
            tolerance = Float64Contract(prefix.contract.state_atol, prefix.contract.probability_atol)
            if kind == 'initialize':
                # Derive Gamma independently; only the shared ordinary birth
                # cursor is supplied by the owner, never trained parameters.
                result = joint.ResidentState(initialize(program, reference.cursor))
            elif kind == 'predict':
                prior = joint.check_state(reference, before_raw, tolerance, bit_limit=bit_limit)
                raw, actual_prediction = joint._prediction_schedule(plan, before_raw, scalar)
                closed(actual_prediction, joint.ResidentPrediction)
                if raw != actual_prediction.raw():
                    raise ContractError('joint prediction lost its actual output words')
            elif kind == 'observe':
                raw, result = joint._observation_schedule(before_raw, before_prediction, target, scalar,
                                                         resident_prediction=prediction)
                closed(result, joint.ResidentState)
                if raw != result.raw() or raw.encoded.pending != prediction.query+(target,):
                    raise ContractError('joint observation differs from its independently owned actual target')
            elif kind == 'commit':
                result = joint.ResidentState(commit(before_raw.encoded))
            elif kind == 'attach':
                result = joint.ResidentState(attach(before_raw.encoded, reference.cursor))
            else:
                raise ContractError('unregistered joint CUDA phase')
            arithmetic.check()
            if arithmetic.output_cells != expected_cells:
                raise ContractError('joint CUDA executed a different complete output schedule')
            if kind == 'predict':
                joint.check_prediction_plan(plan, program, before_raw, rules, sources,
                    output_cap=prefix.contract.phase_output_cells, budget=prefix.contract.partitions,
                    workspace=workspace, bit_limit=bit_limit)
                actual = joint.JointAmpPrediction(actual_prediction.before, actual_prediction.query,
                    arena_phase.raw_words((actual_prediction.readout,), readout_buffer)[0])
                checked = joint.check_prediction_execution(plan, before_raw, actual, arithmetic.raw_trace(), bit_limit=scalar_bits)
                relation = joint.check_prediction(reference_prediction, actual, tolerance,
                    normalizer_cap=normalizer_cap, activation_cap=activation_cap, bit_limit=bit_limit)
                relation = replace(relation, state_error=prior.state_error)
            elif kind == 'observe':
                actual = joint.JointAmpState(result.encoded, arena_phase.raw_words((result.gradient,), readout_buffer)[0])
                joint.check_observation_execution(before_raw, before_prediction, target, actual,
                                                  arithmetic.raw_trace(), bit_limit=scalar_bits)
            if kind != 'predict':
                relation = joint.check_state(reference, result.raw(), tolerance, bit_limit=bit_limit)
            if state is not None and state.raw() != before_raw:
                raise ContractError('joint CUDA mutated its owned predecessor')
            if prediction is not None and prediction.raw() != before_prediction:
                raise ContractError('joint CUDA mutated its owned pre-target prediction')
    except MemoryError:
        raise
    except Exception as exc:
        error = exc
    record = IndexedCudaPhase(object_id, candidate, program.program_id, origin+':'+kind,
        ordinary_cursor, observation_id, input_id, prediction_id, reference, reference_prediction,
        None if result is None else result.raw(), None if actual_prediction is None else actual_prediction.raw(),
        () if arithmetic is None else arithmetic.raw_trace(), relation,
        0 if arithmetic is None else arithmetic.output_cells, None if arena_phase is None else arena_phase.index,
        'CHECKED_CUDA_PREFIX_PHASE' if error is None else
            'UNRESOLVED' if isinstance(error, (ResourceExceeded, ArithmeticUnresolved)) else 'EXECUTION_FAILED',
        '' if error is None else f'{type(error).__name__}: {error}', checked, execution_plan=plan)
    prefix._values[object_id] = actual_prediction if kind == 'predict' else result
    prefix.phases[object_id] = record
    return record, error
