"""Indexed execution inside the existing private CUDA owner, without a signer."""
from fractions import Fraction as F
from dataclasses import replace

from .core import ContractError
from .resources import ResourceExceeded
from .semantics import ArithmeticUnresolved
from .float64_bridge import Float64Contract
from .indexed_count import CountState, commit, attach
from .indexed_execution import IndexedLearner, CategoricalPairDomain
from .cuda_prefix import IndexedCudaPhase
from . import cuda_learner as gpu, indexed_amp as indexed


def execute(prefix, object_id, kind, program, candidate, reference, *, rules, spec, bit_limit,
            ordinary_cursor, origin, observation_id, sources, reference_prediction, target,
            normalizer_cap, activation_cap, source_domain, readout_buffer):
    source = prefix.staged if origin == 'profile' or kind == 'commit' else prefix.current
    input_id = None if kind == 'initialize' else source[candidate]
    prediction_id = prefix.predicted.get(candidate) if kind == 'observe' else None
    state = None if input_id is None else prefix._values[input_id]
    prediction = None if prediction_id is None else prefix._values[prediction_id]
    result, actual_prediction, error, relation = state, None, None, None
    arithmetic, workspace, plan, checked = None, None, None, 0
    before_raw = before_prediction = None
    try:
        if (type(program) is not indexed.IndexedRelation or program.n != prefix.contract.n
                or type(spec) is not IndexedLearner or spec.n != program.n
                or type(source_domain) is not CategoricalPairDomain or source_domain.n != program.n):
            raise ContractError('indexed CUDA lost its complete G/U/domain registration')
        program.validate(rules)
        if state is not None:
            if type(state) is not indexed.ResidentState:
                raise ContractError('indexed CUDA predecessor has another physical representation')
            for _, tensor in state.tensors():
                prefix.arena.require_initialized(tensor)
            before_raw = state.raw()
            if before_raw != prefix.phases[input_id].raw_state:
                raise ContractError('indexed CUDA predecessor differs from its owned phase')
        if prediction is not None:
            if (type(prediction) is not indexed.ResidentPrediction
                    or prefix.phases[prediction_id].input_phase != input_id
                    or prefix.phases[prediction_id].observation_id != observation_id):
                raise ContractError('indexed observation lost its actual pre-target phase or event identity')
            prefix.arena.require_initialized(prediction.readout)
            before_prediction = prediction.raw()
            if before_prediction != prefix.phases[prediction_id].raw_prediction:
                raise ContractError('indexed CUDA prediction changed before target observation')
        if kind == 'predict':
            plan = indexed.prepare_prediction(program, before_raw, rules, sources,
                                              output_cap=prefix.contract.phase_output_cells)
        expected_cells = plan.output_cells if kind == 'predict' else 13 if kind == 'observe' else 0
        indexed.allowance(max(1, expected_cells), prefix.contract.phase_output_cells,
                          'indexed CUDA phase output allowance')
        with prefix.arena.phase(object_id) as workspace:
            arithmetic = gpu.CudaArithmetic(bit_limit, prefix.contract.storage.device, workspace=workspace,
                output_cell_limit=prefix.contract.phase_output_cells, readout_buffer=readout_buffer)
            scalar = indexed._Arithmetic(bit_limit, arithmetic)
            tolerance = Float64Contract(prefix.contract.state_atol, prefix.contract.probability_atol)
            if kind == 'initialize':
                # Gamma is derived independently from the registered family;
                # a trained reference endpoint is never an AMP initializer.
                result = indexed.ResidentState(CountState(program.n, (0,)*(program.n*(program.n-1)//2), None, reference.cursor, 0))
            elif kind == 'predict':
                prior_relation = indexed.check_state(reference, before_raw, tolerance, bit_limit=bit_limit)
                raw, actual_prediction = indexed.execute_prediction(plan, before_raw, scalar)
                if type(actual_prediction) is not indexed.ResidentPrediction:
                    raise ContractError('indexed CUDA helper returned another prediction representation')
                if raw != actual_prediction.raw():
                    raise ContractError('indexed prediction lost its actual output words')
            elif kind == 'observe':
                raw, result = indexed.execute_observation(before_raw, before_prediction, target, scalar,
                                                         resident_prediction=prediction)
                if type(result) is not indexed.ResidentState:
                    raise ContractError('indexed CUDA helper returned another state representation')
                if raw != result.raw() or raw.encoded.pending != prediction.query+(target,):
                    raise ContractError('indexed observation differs from the independently owned actual target')
            elif kind == 'commit':
                result = indexed.ResidentState(commit(before_raw.encoded))
            elif kind == 'attach':
                result = indexed.ResidentState(attach(before_raw.encoded, reference.cursor))
            else:
                raise ContractError('unregistered indexed CUDA phase')
            arithmetic.check()
            if arithmetic.output_cells != expected_cells:
                raise ContractError('indexed CUDA executed a different output extent schedule')
            if kind == 'predict':
                actual = indexed.IndexedAmpPrediction(actual_prediction.before, actual_prediction.query,
                    workspace.raw_words((actual_prediction.readout,), readout_buffer)[0])
                checked = indexed.check_prediction_execution(plan, before_raw, actual,
                    arithmetic.raw_trace(), bit_limit=bit_limit)
                relation = indexed.check_prediction(reference_prediction, actual, tolerance,
                    normalizer_cap=normalizer_cap, activation_cap=activation_cap, bit_limit=bit_limit)
                relation = replace(relation, state_error=prior_relation.state_error)
            elif kind == 'observe':
                actual = indexed.IndexedAmpState(result.encoded,
                    workspace.raw_words((result.gradient,), readout_buffer)[0])
                indexed.check_observation_execution(before_raw, before_prediction, target, actual,
                    arithmetic.raw_trace(), bit_limit=bit_limit)
            if kind != 'predict':
                relation = indexed.check_state(reference, result.raw(), tolerance, bit_limit=bit_limit)
            if state is not None and state.raw() != before_raw:
                raise ContractError('indexed CUDA mutated its owned predecessor')
            if prediction is not None and prediction.raw() != before_prediction:
                raise ContractError('indexed CUDA mutated its owned pre-target prediction')
    except MemoryError:
        raise
    except Exception as exc:
        error = exc
    record = IndexedCudaPhase(object_id, candidate, program.program_id, origin+':'+kind,
        ordinary_cursor, observation_id, input_id, prediction_id, reference, reference_prediction,
        None if result is None else result.raw(), None if actual_prediction is None else actual_prediction.raw(),
        () if arithmetic is None else arithmetic.raw_trace(), relation,
        0 if arithmetic is None else arithmetic.output_cells, None if workspace is None else workspace.index,
        'CHECKED_CUDA_PREFIX_PHASE' if error is None else
            'UNRESOLVED' if isinstance(error, (ResourceExceeded, ArithmeticUnresolved)) else 'EXECUTION_FAILED',
        '' if error is None else f'{type(error).__name__}: {error}', checked,
        execution_plan=plan)
    prefix._values[object_id] = actual_prediction if kind == 'predict' else result
    prefix.phases[object_id] = record
    return record, error
