"""Terminal, owned reporting of a trained token incumbent.

Pure numerical helpers and passive records grant no Runtime, freshness or
installation authority. Only the Runtime's guarded ports call the private
report transitions. Reporting never applies the learner's observation/U.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F

from .core import ContractError, natural
from .data_usage import ObservationRecord, read_sources, source_mapping, indexed_source_read_work
from .encoding import write_packed
from .host_resources import HostExecutionUnresolved
from .numerics import LogInterval, log_enclosure, log_enclosure_work, compare_exact
from .program import name
from .resources import ResourceExceeded
from .semantics import ArithmeticUnresolved, _guard, _operation
from .token_execution import TokenReferenceMachine, closed
from .token_sources import TokenSourceReads

REPORT_PORTS = frozenset(('predict_report', 'observe_report', 'report_result'))


@dataclass(frozen=True)
class TokenReportingContract:
    stream_id: str
    log_terms: int
    accumulator_bits: int

    def __post_init__(self):
        closed(self, TokenReportingContract)
        name(self.stream_id, 'fixed reporting stream')
        natural(self.log_terms, 'report logarithm terms', positive=True)
        natural(self.accumulator_bits, 'report accumulator fractional bits')

    def validate(self, online):
        self.__post_init__()
        if type(online.data.source_reads) is not TokenSourceReads or online.data.input_upper:
            raise ContractError('reporting requires the complete past-token source interface')
        matches = tuple(s for s in online.data.streams if s.stream_id == self.stream_id)
        if len(matches) != 1 or matches[0].role not in ('validation', 'test'):
            raise ContractError('one declared read-only reporting stream required')
        if len(online.data.active.observation_ids) % online.learner.update_unit:
            raise ContractError('reporting requires a whole-unit training horizon')
        return matches[0]


@dataclass(frozen=True)
class TokenReportingManifest:
    reference: object
    reporting: TokenReportingContract


@dataclass(frozen=True)
class ReportPending:
    record: ObservationRecord
    prediction: object
    target_object_id: str
    cuda_prediction: str | None


@dataclass(frozen=True)
class ReportEvent:
    record: ObservationRecord
    prediction: object
    native_probability: F
    native_loss: LogInterval
    cuda_prediction: str | None
    cuda_readout: str | None
    physical_mass: F | None
    physical_sum: tuple[F, F] | None
    physical_loss: LogInterval | None


@dataclass(frozen=True)
class TokenReport:
    candidate_id: str
    program_id: str
    learner: object
    cuda_state: str | None
    status: str = 'REPORTING'
    records: tuple[ObservationRecord, ...] = ()
    events: tuple[ReportEvent, ...] = ()
    pending: ReportPending | None = None
    native_total: tuple[int, int] = (0, 0)
    physical_total: tuple[int, int] | None = None
    reason: str = ''


@dataclass(frozen=True)
class ReportingResult:
    status: str
    completed: int
    declared: int
    native_mean: LogInterval | None = None
    physical_mean: LogInterval | None = None
    reason: str = ''


def mass_loss(mass, lower_sum, upper_sum, *, terms, bit_limit):
    """Conditional -log(mass / true stored-mass sum); no scoring authority."""
    if any(type(x) is not F or x <= 0 for x in (mass, lower_sum, upper_sum)):
        raise ContractError('positive exact mass and sum bounds required')
    if compare_exact(lower_sum, upper_sum, bit_limit=bit_limit) > 0:
        raise ContractError('reversed stored-mass sum enclosure')
    if compare_exact(mass, upper_sum, bit_limit=bit_limit) > 0:
        raise ContractError('target mass exceeds every possible complete sum')
    inverse = F(mass.denominator, mass.numerator)
    low = _operation(lower_sum, inverse, multiply=True, bit_limit=bit_limit)
    high = _operation(upper_sum, inverse, multiply=True, bit_limit=bit_limit)
    left = log_enclosure(low, terms=terms, bit_limit=bit_limit)
    right = left if low == high else log_enclosure(high, terms=terms, bit_limit=bit_limit)
    lo, hi = max(F(0), left.lower), right.upper
    compare_exact(lo, hi, bit_limit=bit_limit)
    return LogInterval(lo, hi)


def add_loss(total, loss, *, fractional_bits, bit_limit):
    """Directed fixed-dyadic accumulation; at most 2^-p added width per side."""
    if (type(total) is not tuple or len(total) != 2 or any(type(n) is not int or n < 0 for n in total)
            or type(loss) is not LogInterval):
        raise ContractError('complete nonnegative loss accumulator required')
    if total[0] > total[1] or loss.lower < 0:
        raise ContractError('ordered nonnegative loss accumulator required')
    natural(fractional_bits, 'loss fractional bits')
    if fractional_bits+1 > bit_limit:
        raise ArithmeticUnresolved('report accumulator scale exceeds its integer allowance')
    scale = F(1 << fractional_bits)
    a = _operation(loss.lower, scale, multiply=True, bit_limit=bit_limit)
    b = _operation(loss.upper, scale, multiply=True, bit_limit=bit_limit)
    lo, hi = a.numerator//a.denominator, -(-b.numerator//b.denominator)
    values = tuple(_operation(F(old), F(new), multiply=False, bit_limit=bit_limit).numerator
                   for old, new in zip(total, (lo, hi)))
    return values


def _registered(rt):
    cfg = rt._token_report_contract
    if type(cfg) is not TokenReportingContract or type(rt._machine) is not TokenReferenceMachine:
        raise ContractError('owned token reporting registration required')
    # Constructor-validated immutable registration, never a caller-supplied
    # certificate. Its bounded metadata lookup is included in each port's
    # control tariff; target ingress is prepaid by the preceding prediction.
    return cfg, next(s for s in rt._online.data.streams if s.stream_id == cfg.stream_id)


def _binding(rt):
    r = rt._token_report
    if type(r) is not TokenReport or r.candidate_id != rt._deployed_id:
        raise ContractError('owned frozen incumbent reporting identity required')
    current = rt._candidates[r.candidate_id]
    if current.program_id != r.program_id or current.learner is not r.learner or current.learner.unit_count:
        raise ContractError('reporting lost its complete frozen learner')
    if rt._cuda is not None and rt._cuda.current[r.candidate_id] != r.cuda_state:
        raise ContractError('reporting changed its frozen physical lineage')
    return r, current, rt._programs[r.program_id]


def _pay(rt, label, work):
    rt._event_router.charge_work('deployment_event', {'work': work}, 'token-report:'+label)


def _retain(rt, label, value):
    obj = rt._machine.realize(rt._runtime_id+':report:'+label, 'token_reporting_record', value, rt._chi)
    rt._allocate(rt._data_owner, (obj,))


def _failure(rt, stage, error):
    expected = isinstance(error, (ResourceExceeded, ArithmeticUnresolved))
    rt._token_report = replace(rt._token_report, status='UNRESOLVED' if expected else 'EXECUTION_FAILED',
                               reason=type(error).__name__+': '+str(error))
    rt._halt('token-report:'+stage, error)
    if not expected:
        raise error
    _, stream = _registered(rt)
    return ReportingResult('UNRESOLVED', len(rt._token_report.events), len(stream.observation_ids), reason=str(error))


def _begin(rt):
    rt._require_online()
    rt._require_idle()
    _pay(rt, 'begin-control', rt._machine.control_admission_work+32*(len(rt._online.data.streams)+1))
    cfg, stream = _registered(rt)
    if rt._token_report is not None or rt._cursor != len(rt._online.data.active.observation_ids):
        raise ContractError('reporting begins once, after the complete declared training horizon')
    state = rt._candidates[rt._deployed_id]
    if not state.range_safe or state.learner.unit_count:
        raise ContractError('range-safe committed incumbent required for frozen reporting')
    _pay(rt, 'begin', rt._machine.control_admission_work+len(stream.observation_ids)+1)
    if set(rt.__dict__) != rt._root_fields:
        raise ContractError('frozen reporting has no frame proof for an unknown Runtime coordinate')
    r = TokenReport(state.candidate_id, state.program_id, state.learner,
        None if rt._cuda is None else rt._cuda.current[state.candidate_id],
        physical_total=None if rt._cuda is None else (0, 0))
    rt._token_report = r
    rt._event_phase = 'report-freezing'
    rt._revision += 1
    try:
        _retain(rt, 'frozen', r)
        result = ReportingResult('REPORTING', 0, len(stream.observation_ids))
        rt._event_phase = 'report-ready'
        return result
    except (MemoryError, HostExecutionUnresolved):
        raise
    except Exception as error:
        return _failure(rt, 'begin', error)


def _predict(rt, observation_id):
    name(observation_id, 'report observation ID')
    cfg, stream = _registered(rt)
    r, state, program = _binding(rt)
    if rt._event_phase != 'report-ready' or r.status != 'REPORTING' or r.pending is not None:
        raise ContractError('report prediction requires its current unfired reporting event')
    cursor = len(r.records)
    if cursor >= len(stream.observation_ids) or observation_id != stream.observation_ids[cursor]:
        raise ContractError('reporting cannot skip, reuse or relabel its declared observation IDs')
    try:
        # There are no external context inputs in this registration. Every
        # atom comes from the complete owned reporting prefix, with fresh PAD
        # at this declared file/stream boundary and no special EOT reset.
        _pay(rt, 'predict', indexed_source_read_work(rt._online.data, cursor)
             +rt._machine.evaluation_work(program, rt._contract.semantics)+8*(cursor+1)
             +128*(len(rt._online.data.streams)+1)+1024)
        sources = read_sources(rt._online.data, cursor, (), r.records)
        record = ObservationRecord(observation_id, stream.stream_id, stream.role, cursor, (), sources, None)
        target_id = rt._runtime_id+f':report:{cursor}:target'
        slot = rt._machine.realize(target_id, 'reserved_target', rt._target_slot(None), rt._chi)
        rt._allocate(rt._data_owner, (slot,))
        pending = ReportPending(record, None, target_id, None)
        rt._token_report = replace(r, pending=pending)
        rt._event_phase = 'report-predicting'
        rt._revision += 1
        _retain(rt, f'{cursor}:context', record)
        prediction = rt._reference_predict(program, rt._contract.semantics, r.learner, source_mapping(sources),
            bit_limit=rt._contract.reference_integer_bits,
            execution_debit=lambda n: _pay(rt, 'predict-execution', n),
            search_debit=lambda n: _pay(rt, 'predict-search', n))
        if (prediction.normalizer > rt._contract.normalizer_cap
                or any(v > rt._contract.activation_cap for v in rt._machine.activation_values(prediction))):
            raise ContractError('frozen reporting contradicts its retained full-domain range proof')
        pending = replace(pending, prediction=prediction)
        rt._token_report = replace(r, pending=pending)
        if rt._cuda is not None:
            rt._cuda_execute('predict', program, r.candidate_id, r.learner, origin='report',
                observation_id=observation_id, sources=sources, reference_prediction=prediction, target=None)
            pending = replace(pending, cuda_prediction=rt._cuda.predicted[r.candidate_id])
            rt._token_report = replace(r, pending=pending)
        _retain(rt, f'{cursor}:predicted', pending)
        rt._event_phase = 'report-awaiting-target'
        return ReportingResult('PREDICTED_REPORT', len(r.events), len(stream.observation_ids))
    except (MemoryError, HostExecutionUnresolved):
        raise
    except Exception as error:
        return _failure(rt, 'predict', error)


def _observe(rt, target):
    cfg, stream = _registered(rt)
    r, state, program = _binding(rt)
    if rt._event_phase != 'report-awaiting-target' or r.pending is None:
        raise ContractError('report target requires its owned pre-target forecast')
    natural(target, 'report target')
    if target >= program.definition.output.labels:
        raise ContractError('report target outside the complete vocabulary')
    pending = replace(r.pending, record=replace(r.pending.record, target=target))
    rt._token_report = replace(r, records=r.records+(pending.record,), pending=pending)
    rt._event_phase = 'report-scoring'
    rt._revision += 1
    try:
        rt._data_usage.record((pending.record,), 'report', rt._runtime_id, rt._cursor)
        filled = rt._machine.realize(pending.target_object_id, 'reserved_target', rt._target_slot(target), rt._chi)
        slot = rt._buffers[pending.target_object_id]
        if type(slot) is not bytearray or len(slot) != filled.spec.residency['reference_payload_bytes']:
            raise ContractError('report target lost its prepaid complete mutable ingress slot')
        write_packed(filled.value, slot)
        bits = rt._contract.reference_integer_bits
        _pay(rt, 'score', rt._machine.evaluation_work(program, rt._contract.semantics)
             +6*log_enclosure_work(cfg.log_terms)+1024+16*(len(r.records)+1))
        expected = rt._reference_predict(program, rt._contract.semantics, r.learner,
            source_mapping(pending.record.sources), bit_limit=bits,
            execution_debit=lambda n: _pay(rt, 'score-execution', n),
            search_debit=lambda n: _pay(rt, 'score-search', n))
        if pending.prediction != expected:
            raise ContractError('reporting forecast changed after its actual source point')
        probability = pending.prediction.probabilities[target]
        native_loss = mass_loss(probability, F(1), F(1), terms=cfg.log_terms, bit_limit=bits)
        physical_mass = physical_sum = physical_loss = readout_id = None
        if rt._cuda is not None:
            if rt._cuda.predicted[r.candidate_id] != pending.cuda_prediction:
                raise ContractError('report target lost its actual owned physical forecast')
            rt._cuda_execute('readout', program, r.candidate_id, r.learner, origin='report',
                observation_id=pending.record.observation_id, sources=pending.record.sources,
                reference_prediction=pending.prediction, target=target)
            readout_id = next(reversed(rt._cuda.phases))
            physical = rt._cuda.phases[readout_id]
            physical_mass = F(float(physical.raw_prediction.mass.array()))
            forecast = rt._cuda.phases[pending.cuda_prediction]
            physical_sum = (forecast.relation['stored_sum_lower'][0], forecast.relation['stored_sum_upper'][0])
            physical_loss = mass_loss(physical_mass, *physical_sum, terms=cfg.log_terms, bit_limit=bits)
        event = ReportEvent(pending.record, pending.prediction, probability, native_loss,
            pending.cuda_prediction, readout_id, physical_mass, physical_sum, physical_loss)
        native_total = add_loss(r.native_total, native_loss, fractional_bits=cfg.accumulator_bits, bit_limit=bits)
        physical_total = (None if physical_loss is None else
            add_loss(r.physical_total, physical_loss, fractional_bits=cfg.accumulator_bits, bit_limit=bits))
        complete = len(r.events)+1 == len(stream.observation_ids)
        following = replace(rt._token_report, events=r.events+(event,), pending=None,
            native_total=native_total, physical_total=physical_total,
            status='COMPLETE_REPORT' if complete else 'REPORTING')
        _retain(rt, f'{len(r.events)}:scored', event)
        _retain(rt, f'{len(r.events)}:accumulator', (following.native_total, following.physical_total))
        _binding(rt)
        result = ReportingResult('COMPLETE_REPORT' if complete else 'SCORED_REPORT', len(following.events), len(stream.observation_ids))
        rt._token_report = following
        rt._event_phase = 'reported' if complete else 'report-ready'
        return result
    except (MemoryError, HostExecutionUnresolved):
        raise
    except Exception as error:
        return _failure(rt, 'score', error)


def _result(rt):
    _pay(rt, 'result-control', rt._machine.control_admission_work+32*(len(rt._online.data.streams)+1))
    cfg, stream = _registered(rt)
    r, _, _ = _binding(rt)
    if r.status != 'COMPLETE_REPORT':
        return ReportingResult(r.status, len(r.events), len(stream.observation_ids), reason=r.reason)
    _pay(rt, 'result', 256)
    try:
        bits = rt._contract.reference_integer_bits
        if cfg.accumulator_bits+1 > bits:
            raise ArithmeticUnresolved('report accumulator scale exceeds its integer allowance')
        denominator = _operation(F(len(r.events)), F(1 << cfg.accumulator_bits), multiply=True, bit_limit=bits).numerator
        def mean(total):
            if total is None:
                return None
            values = tuple(F(x, denominator) for x in total)
            _guard(*values, bit_limit=bits)
            compare_exact(*values, bit_limit=bits)
            return LogInterval(*values)
        return ReportingResult(r.status, len(r.events), len(stream.observation_ids), mean(r.native_total), mean(r.physical_total))
    except (MemoryError, HostExecutionUnresolved):
        raise
    except Exception as error:
        return _failure(rt, 'result', error)
