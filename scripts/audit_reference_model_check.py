"""Random complete native classes against an independent exact learner model.

Only ordinary bytes/labels drive the owned Runtime. The external oracle
enumerates every native member independently and uses forward differentials,
not production evaluation, reverse differentiation, search or range helpers.
This is a correctness audit, not a population or model-science experiment.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime, CompilerPolicy, CompilationStep
from fp_reference.data_usage import StochasticStreamLaw
from fp_reference.float64_bridge import Float64Contract
from fp_reference.installation import CpuInstallContract
from fp_reference.native_search import GrammarLimits
from fp_reference.profile import ProfileSpec
from fp_reference.program import Program, Source, Sum, Term, Binding, DelayedStateSpec
from fp_reference.search import ReferenceSearchSpec
from audit_reference_construction import contract, limits, validate_residency
from audit_reference_events import online, forward_oracle
from audit_reference_search import brute_grammar
from audit_paired_cpu_persistence import registration
from audit_float64_runtime import replay
from ingress_audit_support import deliver_context


@dataclass(frozen=True)
class ModelState:
    theta: tuple
    delayed: tuple
    gradient: tuple
    unit: int = 0
    cursor: int = 0
    steps: int = 0


class InfeasibleRange(Exception):
    pass


def initial(graph, cfg, cursor=0):
    return ModelState(tuple(cfg.initializer_pattern[i % len(cfg.initializer_pattern)] for i in range(graph.slot_count)),
        tuple(sorted((s.state_id, (F(0),)*s.delay) for s in cfg.semantics.states)),
        (F(0),)*graph.slot_count, cursor=cursor)


def forward(graph, cfg, state, inputs):
    return forward_oracle(graph, cfg.semantics, state.theta,
        dict(zip((s.source_id for s in cfg.semantics.sources), inputs)), state.delayed, return_values=True)


def safe(graph, cfg, state):
    # Positive arithmetic is monotone. Enumerate the actual declared source
    # domain and evaluate every delayed upper endpoint, retaining the body
    # invariance obligation as well as the output/activation bounds.
    upper = replace(state, delayed=tuple(sorted((s.state_id, (s.upper,)*s.delay) for s in cfg.semantics.states)))
    state_caps = {s.state_id: s.upper for s in cfg.semantics.states}
    for inputs in cfg.source_domain:
        _, _, values = forward(graph, cfg, upper, inputs)
        if any(value > cfg.activation_cap for value in values):
            return False
        if sum(cfg.semantics.base)+sum(values[h] for h in graph.heads) > cfg.normalizer_cap:
            return False
        if any(values[b.body] > state_caps[b.state_id] for b in graph.bindings):
            return False
    return True


def step(graph, cfg, learner, state, inputs, target):
    _, gradients, values = forward(graph, cfg, state, inputs)
    bodies = {b.state_id: b.body for b in graph.bindings}
    queues = tuple((key, old[1:]+(values[bodies[key]],)) for key, old in state.delayed)
    gradient = tuple(a+b for a, b in zip(state.gradient, gradients[target]))
    state = replace(state, delayed=queues, gradient=gradient, unit=state.unit+1, cursor=state.cursor+1)
    if state.unit == learner.update_unit:
        assert learner.commit_grid_bits is None
        theta = tuple(max(F(0), t-learner.learning_rate*g/state.unit) for t, g in zip(state.theta, state.gradient))
        state = replace(state, theta=theta, gradient=(F(0),)*len(theta), unit=0, steps=state.steps+1)
        if not safe(graph, cfg, state):
            raise InfeasibleRange
    return state


def same(actual, expected):
    assert actual.theta == expected.theta and actual.delayed == expected.delayed
    assert actual.gradient_sum == expected.gradient
    assert (actual.unit_count, actual.cursor, actual.optimizer_steps) == (expected.unit, expected.cursor, expected.steps)


def endpoint(graph, cfg, run, profile, training):
    state = initial(graph, cfg)
    if not safe(graph, cfg, state):
        return None
    if profile is not None:
        by_id = dict(zip((f'observation-{i}' for i in range(len(training))), training))
        try:
            for obs in profile.observation_ids*profile.passes:
                inputs, target = by_id[obs]
                state = step(graph, cfg, run.learner, state, inputs, target)
        except InfeasibleRange:
            return None
    return replace(state, cursor=len(training))


def likelihood(graph, cfg, state, tape):
    score = F(1)
    for inputs, target in tape:
        score *= forward(graph, cfg, state, inputs)[0][target]
    return score


def fixture(rng, index):
    cfg = contract(k=2+index % 2, cap=20, peak=10,
        pattern=tuple(rng.choice((F(0), F(1, 2), F(1))) for _ in range(2)))
    if index % 4 == 1:
        cfg = replace(cfg, semantics=replace(cfg.semantics,
            sources=(cfg.semantics.sources[0], replace(cfg.semantics.sources[1], type_id='flag')),
            sum_types=('mass', 'flag'),
            product_rules=(('mass', 'mass', 'mass'), ('mass', 'flag', 'mass'),
                           ('flag', 'mass', 'flag'), ('flag', 'flag', 'flag'))))
    if index % 3 == 0:
        cfg = replace(cfg, semantics=replace(cfg.semantics,
            states=(DelayedStateSpec('lag', 'mass', 1+index % 2, F(1)),)))
    cfg = replace(cfg, reference_integer_bits=32768, limits=limits(200_000_000, 2_000_000_000))
    caps = GrammarLimits(rng.randrange(3), rng.randrange(2), rng.randrange(2), rng.randrange(3), rng.randrange(2))
    if index in (4, 20):
        caps = GrammarLimits(3, 1, 1, 2, 0)  # compounds of distinct sources, with every shorter/P0 alternative
    if index >= 32:
        # Deliberately active constraints: an initializer can fail a global
        # normalizer bound, a replay can leave the activation/state invariant,
        # and a later ordinary commit can fail after its target was revealed.
        cfg = contract(k=2, cap=3 if index == 32 else 20,
                       peak=10 if index == 34 else 1, pattern=(F(1),))
        if index == 34:
            cfg = replace(cfg, semantics=replace(cfg.semantics,
                states=(DelayedStateSpec('lag', 'mass', 2, F(1)),)))
        cfg = replace(cfg, reference_integer_bits=32768, limits=limits(200_000_000, 2_000_000_000))
        caps = GrammarLimits(0, 0, 0, 0, 0) if index == 35 else GrammarLimits(2, 1, 0, 1, 1)
    initial_graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())),
        1, (1,)+(2,)*(len(cfg.semantics.base)-1), tuple(Binding(s.state_id, 0) for s in cfg.semantics.states))
    spec = ReferenceSearchSpec('native', caps, tuple(f'observation-{i}' for i in range(4)))
    use_profile = index % 2 if index < 32 else index in (33, 34)
    profile = ProfileSpec('profile', spec.observation_ids, 2) if use_profile else None
    if profile is not None:
        spec = replace(spec, profile_id=profile.profile_id)
    run = online(cfg, 8, unit=2, rate=rng.choice((F(0), F(1, 16), F(1, 8))), grid=None)
    run = replace(run, data=replace(run.data, stream_law=StochasticStreamLaw('external audit law; deterministic generator does not prove it')),
        profiles=() if profile is None else (profile,), searches=(spec,),
        float64=Float64Contract(F(1, 1 << 24), F(1, 1 << 24)),
        persistence=registration(bound=F(4), horizon=4), cpu_install=CpuInstallContract())
    tape = tuple((rng.choice(cfg.source_domain), rng.randrange(len(cfg.semantics.base))) for _ in range(8))
    if index >= 32:
        run = replace(run, learner=replace(run.learner, learning_rate=F(1, 8)))
        tape = ((cfg.source_domain[1], 0),)*4+((cfg.source_domain[0], 0),)*4
    rt = ReferenceCompilerRuntime(cfg, initial_graph, online=run,
        policy=CompilerPolicy((CompilationStep(4, 'native', 100000, 'ref', 'finite'),)))
    return rt, cfg, run, initial_graph, spec, profile, tape


def model_check(cases=None, progress=False):
    rng = random.Random(2026091367)
    counts = {'runs': 0, 'complete_native_members': 0, 'exact_endpoint_scores': 0,
              'range_unresolved_members': 0, 'complete_class_proofs': 0,
              'initial_range_unresolved_members': 0, 'profile_range_unresolved_members': 0,
              'infeasible_class_results_unresolved': 0, 'ordinary_successor_checks': 0,
              'halted_unsafe_ordinary_commits': 0, 'independent_binary64_phases': 0}
    shapes = set()
    for index in range(36):
        rt, cfg, run, base_graph, spec, profile, tape = fixture(rng, index)
        if cases is not None and index not in cases:
            continue
        shapes.add((spec.grammar, len(cfg.semantics.base), len(cfg.semantics.states), profile is not None))
        base_model = initial(base_graph, cfg)
        for i, (inputs, target) in enumerate(tape[:4]):
            assert deliver_context(rt, f'observation-{i}', inputs).status == 'PREDICTED_REFERENCE'
            base_model = step(base_graph, cfg, run.learner, base_model, inputs, target)
            assert rt.observe(target).status == 'OBSERVED_REFERENCE'
            snapshot = validate_residency(rt)
            same(next(c for c in snapshot.candidates if c.candidate_id == snapshot.deployed_id).learner, base_model)
            counts['ordinary_successor_checks'] += 1
        session = snapshot.searches[0]
        expected = {graph: endpoint(graph, cfg, run, profile, tape[:4]) for graph in brute_grammar(cfg.semantics, spec.grammar)}
        assert len(session.rows) == len(expected) and {r.program for r in session.rows} == set(expected)
        scores = {snapshot.deployed_id: likelihood(base_graph, cfg, base_model, tape[:4])}
        assert session.base_likelihood == scores[snapshot.deployed_id]
        models = {snapshot.deployed_id: (base_graph, base_model)}
        unresolved = 0
        for row in session.rows:
            state = expected[row.program]
            if state is None:
                assert row.status != 'COMPARED_REFERENCE' and row.likelihood is None
                unresolved += 1
                key = 'profile_range_unresolved_members' if safe(row.program, cfg, initial(row.program, cfg)) else 'initial_range_unresolved_members'
                counts[key] += 1
                continue
            same(row.learner, state)
            score = likelihood(row.program, cfg, state, tape[:4])
            assert row.status == 'COMPARED_REFERENCE' and row.likelihood == score
            scores[row.candidate_id] = score
            models[row.candidate_id] = row.program, state
            counts['exact_endpoint_scores'] += 1
        assert session.best_likelihood == max(scores.values())
        if unresolved:
            assert not snapshot.reference_proofs and session.status == 'UNRESOLVED'
            counts['infeasible_class_results_unresolved'] += 1
        else:
            assert session.status == 'REFERENCE_CLASS_EXHAUSTED' and len(snapshot.reference_proofs) == 1
            proof = snapshot.reference_proofs[0]
            assert proof.program_count == len(expected) and proof.best_likelihood == max(scores.values())
            counts['complete_class_proofs'] += 1
        counts['range_unresolved_members'] += unresolved
        counts['complete_native_members'] += len(expected)
        for i, (inputs, target) in enumerate(tape[4:], 4):
            active = {c.candidate_id: c for c in snapshot.candidates}
            assert deliver_context(rt, f'observation-{i}', inputs).status == 'PREDICTED_REFERENCE'
            successors, failed = {}, False
            for key, candidate in active.items():
                graph, state = models[key]
                same(candidate.learner, state)
                try:
                    successors[key] = graph, step(graph, cfg, run.learner, state, inputs, target)
                except InfeasibleRange:
                    failed = True
            result = rt.observe(target)
            snapshot = validate_residency(rt)
            if failed:
                assert result.status == 'UNRESOLVED' and snapshot.halted is not None
                assert snapshot.cursor == i and len(snapshot.observations) == i+1 and snapshot.run.closure is None
                for candidate in snapshot.candidates:
                    same(candidate.learner, models[candidate.candidate_id][1])
                counts['halted_unsafe_ordinary_commits'] += 1
                break
            assert result.status == 'OBSERVED_REFERENCE'
            models.update(successors)
            for candidate in snapshot.candidates:
                same(candidate.learner, models[candidate.candidate_id][1])
                counts['ordinary_successor_checks'] += 1
        if snapshot.halted is None:
            assert snapshot.run.status == 'SEALED_REFERENCE_STREAM' and snapshot.cursor == 8
            phases, _, _ = replay(rt)
            counts['independent_binary64_phases'] += phases
        counts['runs'] += 1
        if progress:
            print(f'case {index}: {len(expected)} native members, {unresolved} range-UNRESOLVED, {snapshot.run.status}', file=sys.stderr, flush=True)
    if cases is None:
        assert counts['runs'] == 36 and counts['complete_class_proofs'] and counts['exact_endpoint_scores'] and len(shapes) >= 20
        assert counts['initial_range_unresolved_members'] and counts['profile_range_unresolved_members']
        assert counts['halted_unsafe_ordinary_commits'] >= 3 and counts['infeasible_class_results_unresolved'] >= 3
    return {'status': 'PASS', 'scope': 'owned finite Runtime and independently exhaustive exact native/learner model',
            'seed': 2026091367, 'randomized_classes': 32, 'directed_constraint_cases': 4,
            'selected_cases': cases, 'distinct_class_shapes': len(shapes), 'counts': counts,
            'not_claimed': ['all future continuations or target AMP', 'random sampling is exhaustive over all registrations']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--cases', type=int, nargs='+', choices=range(36))
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    if args.write and args.cases is not None:
        parser.error('only the full model check can write canonical evidence')
    result = model_check(args.cases, args.progress)
    if args.write:
        (ROOT/'evidence/minimal/FP_REFERENCE_MODEL_CHECK.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
