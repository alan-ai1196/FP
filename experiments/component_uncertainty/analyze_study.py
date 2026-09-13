"""Independent RN-3 rescore and fresh-decision replay; never executes a model."""
import argparse
from collections import Counter
from fractions import Fraction as F
from itertools import product
import json
from math import isclose, log, prod
from pathlib import Path
from statistics import mean
import sys

import run_study as experiment
from study import data, support, diagnostic_cases, new_cases, counts_from_training, posterior, unseen_pairs

SOURCE = 'a351da9'
ROOT = experiment.ROOT
OLD = experiment.rn2_analysis
ANALYSIS_DEPENDENCIES = OLD.ANALYSIS_DEPENDENCIES + (
    'experiments/component_uncertainty/PROTOCOL.md',
    'experiments/component_uncertainty/study.py',
    'experiments/component_uncertainty/run_study.py')
check_score = OLD.check_score
encode_posterior = OLD.encode_posterior
SINGLE = experiment.SINGLE


def component_model(n, counts):
    """Derive path connectivity by transitive closure, not producer BFS."""
    reachable = [[i == j for j in range(n)] for i in range(n)]
    assignment = [0]*n
    for i, j, a, b in counts:
        assert j == i+1 and a+b == 10
        if a != b:
            reachable[i][j] = reachable[j][i] = True
            assignment[j] = assignment[i] ^ int(b > a)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reachable[i][j] |= reachable[i][k] and reachable[k][j]
    components = sorted({tuple(j for j in range(n) if reachable[i][j]) for i in range(n)})
    alternatives, likelihoods = [], []
    for a in (F(1), F(8)):
        rows = {}
        for i in range(n):
            for j in range(n):
                if not reachable[i][j]:
                    rows[i, j] = (F(1, 2), F(1, 2))
                else:
                    hi, lo = (a+1)/(a+2), 1/(a+2)
                    rows[i, j] = (lo, hi) if assignment[i]^assignment[j] else (hi, lo)
        alternatives.append(rows)
        likelihoods.append(prod(rows[i, j][0]**a * rows[i, j][1]**b for i, j, a, b in counts))
    at = likelihoods.index(max(likelihoods))
    return components, assignment, (F(1), F(8))[at], alternatives[at], max(likelihoods)


def evidence_trace(candidate, evaluation):
    """Finite descriptive wealth trace; no event or new evidence authority."""
    if candidate is None:
        return None
    # check_fp first uses OLD.prospective_boundary(), which independently
    # checks these log enclosures against 100-digit Decimal.
    lowers = {p: OLD.log_enclosure(2*p, terms=12, bit_limit=32768).lower
              for values in candidate.values() for p in values}
    wealth, maximum = F(1), F(1)
    counts = {'positive': 0, 'zero': 0, 'negative': 0}
    crossed = None
    for offset, (i, j, label) in enumerate(evaluation):
        gain = lowers[candidate[i, j][label]]
        counts['positive' if gain > 0 else 'negative' if gain < 0 else 'zero'] += 1
        prior = wealth
        raw = wealth*(1+gain/4)
        wealth = F((raw.numerator*(1 << 16))//raw.denominator, 1 << 16)
        if gain == 0:
            assert wealth == prior
        maximum = max(maximum, wealth)
        if wealth >= 4:
            crossed = offset+1
            break
    return {'first_crossing_fresh_offset': crossed, 'score_sign_counts_until_crossing_or_end': counts,
        'exact_wealth_at_crossing_or_end': str(wealth), 'maximum_exact_wealth': str(maximum)}


def future_information_control(counts, evaluation, n):
    """Condition on one revealed cross label; no adaptive GPU score is claimed."""
    components, _, _, candidate, _ = component_model(n, counts)
    component_of = {v: k for k, vertices in enumerate(components) for v in vertices}
    crossings = [(at, i, j, y) for at, (i, j, y) in enumerate(evaluation)
                 if component_of[i] != component_of[j]]
    first, second = crossings[:2]
    _, i, j, label = first
    # Conditioned 9:1 training fixes only within-component parities. Explicit
    # fair-bit enumeration leaves four assignments, including global flips.
    family = [h for h in product((0, 1), repeat=n)
              if all((h[u]^h[v]) == int(b > a) for u, v, a, b in counts)]
    assert len(family) == 4 and all(sorted((a, b)) == [1, 9] for _, _, a, b in counts)
    weights = [9 if (h[i]^h[j]) == label else 1 for h in family]
    _, u, v, _ = second  # The next target is not used by this prediction.
    probability = sum(w*(F(9, 10) if h[u]^h[v] else F(1, 10)) for h, w in zip(family, weights))/sum(weights)
    prediction = (1-probability, probability)
    assert sorted(prediction) == [F(9, 50), F(41, 50)]
    assert candidate[i, j] == candidate[u, v] == (F(1, 2), F(1, 2))
    assert OLD.log_enclosure(2*candidate[i, j][label], terms=12, bit_limit=32768).lower == 0
    return {'first_cross_query_offset': first[0]+1, 'next_cross_query_offset': second[0]+1,
        'next_cross_prediction_after_one_label_exact': list(map(str, prediction)),
        'current_FP_prediction': ['1/2', '1/2'], 'first_label_current_log_gain': '0',
        'scope': 'exact conditional control; not an executed adaptive posterior or native endpoint'}


def check_fp(row, n, counts, hidden, train, evaluation, unseen):
    assert row['run_status'] == 'SEALED_CUDA_STREAM'
    assert (row['training_events'], row['evaluation_events']) == (len(train), n*n)
    cuda = row['independent_CUDA']
    assert cuda['phases'] == row['independent_binary64_phases']
    assert cuda['actual_arena_bytes'] == 16 << 20
    assert cuda['maximum_output_cells'] <= 4096 and cuda['largest_phase_frame_used'] <= 131072
    assert row['resources']['consumed_native_arena_extent'] <= 16 << 20
    assert row['resources']['peak_packed_bytes'] <= 1 << 30
    domain = tuple((i, j) for i in range(n) for j in range(n))
    uniform = {p: (F(1, 2), F(1, 2)) for p in domain}
    candidate, raw = None, None
    components, assignment, scale, proposed, likelihood = component_model(n, counts)
    baseline = F(1, 2)**len(train)
    best = baseline
    checked = 2
    if row['native_candidate'] is not None:
        assert row['proposal_status'] == 'PROPOSED_NATIVE' and row['actually_compared'] == 1
        assert row['proposal_assignment'] == assignment and F(row['proposal_scale']) == scale
        assert sorted(map(tuple, row['components'])) == components
        c = len(components)
        graph = row['native_candidate']
        assert (graph['nodes'], graph['sources'], graph['SUMs'], graph['PRODUCTs'], graph['edges'], graph['slots']) == (
            2*n+8*c+2, 2*n, 4*c+2, 4*c, 2*n+12*c, 1 if scale == 1 else 2)
        candidate = proposed
        raw = {p: tuple(SINGLE.decode(SINGLE.rounded(v)) for v in values) for p, values in candidate.items()}
        check_score(row['frozen_candidate_unseen'], candidate, hidden, unseen, raw)
        check_score(row['frozen_candidate_full_domain'], candidate, hidden, domain, raw)
        best = prod(candidate[i, j][label] for i, j, label in train)
        assert best == likelihood > baseline
        assert F(row['alpha_spent']) == F(1, 2)
        checked += 2
    else:
        assert row['frozen_candidate_unseen'] is None and row['frozen_candidate_full_domain'] is None
        assert F(row['alpha_spent']) == 0
        # Absence is retained, never given the hypothetical proposed score.
        assert row['actually_compared'] in (0, 1)
    upper = prod(F(a, a+b)**a * F(b, a+b)**b for _, _, a, b in counts)
    assert best <= upper
    complete = best == upper
    assert row['reference_proofs'] == int(complete)
    decision, = row['final_class_decisions']
    assert decision['has_proof'] == complete
    assert decision['status'] == ('HISTORICAL_REFERENCE_CLASS_BOUNDED' if complete else 'UNRESOLVED')
    assert decision['ordinary_cursor'] == len(train)
    assert decision['grammar'] == dict(nodes=2*n+n*n+2, SUMs=n*n+6, PRODUCTs=n*n+4, edges=4*n*n+2*n+12, slots=2)
    assert row['cutoff_search_status'] == ('REFERENCE_CLASS_BOUNDED' if complete else 'UNRESOLVED')
    install = row['install_cursor']
    boundary = OLD.prospective_boundary(candidate, len(train), evaluation)
    trace = evidence_trace(candidate, evaluation)
    if trace is not None:
        offset = trace['first_crossing_fresh_offset']
        inferred = None if offset is None else 10*((len(train)+offset+9)//10)
        if inferred is not None and inferred > len(train)+len(evaluation):
            inferred = None
        assert inferred == boundary
    if install is not None:
        assert candidate is not None and len(train) < install <= len(train)+n*n and install % 10 == 0
        assert row['final_policy_stage'] == 'INSTALLED_CUDA' and install == boundary
    elif row['final_policy_stage'] == 'EVIDENCE':
        assert boundary is None
    deployed, deployed_raw = {}, {}
    for offset, (i, j, _) in enumerate(evaluation):
        used = install is not None and len(train)+offset >= install
        deployed[i, j] = candidate[i, j] if used else uniform[i, j]
        deployed_raw[i, j] = raw[i, j] if used else uniform[i, j]
    check_score(row['deployed_stream_unseen'], deployed, hidden, unseen, deployed_raw)
    check_score(row['deployed_stream_full_domain'], deployed, hidden, domain, deployed_raw)
    component_of = {v: k for k, vertices in enumerate(components) for v in vertices}
    # This is a descriptive information-cut count. Uniform cross-component
    # forecasts have exactly zero log gain against the actual uniform base;
    # they still consume real events, work and optimizer-boundary positions.
    wait = install-len(train) if install is not None else len(evaluation)
    neutral = sum(component_of[i] != component_of[j] for i, j, _ in evaluation[:wait])
    return checked, {'recomputed_evidence_ready_boundary': boundary,
        'empirical_component_sizes': list(map(len, components)),
        'unseen_cross_component_contexts': sum(component_of[i] != component_of[j] for i, j in unseen),
        'unseen_contexts': len(unseen),
        'all_domain_within_component_contexts': sum(len(c)**2 for c in components),
        'fresh_events_until_install_or_end': wait,
        'neutral_cross_component_events_before_install_or_end': neutral,
        'recomputed_fresh_trace': trace}


def check_baseline(row, n, counts, law, hidden, unseen, *, historical=False):
    law = 'iid' if law.startswith('iid') else law
    full_ce = OLD.check_baseline(row, n, counts, law, hidden, unseen)
    if historical:
        return 0, full_ce
    exact = posterior(n, counts, law)
    amp, raw = encode_posterior(exact)
    domain = tuple(exact)
    check_score(row['exact_full_domain'], exact, hidden, domain)
    check_score(row['AMP_full_domain'], amp, hidden, domain, raw)
    assert isclose(full_ce, row['AMP_full_domain']['expected_CE_binary64'], rel_tol=0, abs_tol=2**-42)
    return 4, full_ce


def verify(*, partial=False):
    report = json.loads(experiment.OUTPUT.read_text(encoding='utf-8'))
    source = experiment.git('rev-parse', SOURCE)
    assert report['registration_source'] == source and report['experiment'] == 'RN-3'
    assert report['protocol_commit'] == experiment.git('rev-parse', experiment.PROTOCOL_COMMIT)
    # No current Runtime/constructor is executed by this rescore. Guard
    # actual data, recorded worker and arithmetic dependencies while allowing
    # later solver research and improvements to the independent audit itself.
    assert not experiment.git('diff', source, '--', *ANALYSIS_DEPENDENCIES)
    old, reference = experiment.historical()
    assert report['historical_control'] == json.loads(json.dumps(reference))
    workers = report['workers']
    assert [(r['kind'], tuple(r['case'])) for r in workers] == list(experiment.tasks()[:len(workers)])
    assert len(workers) <= 18
    if not partial:
        assert len(workers) == 18 and report['status'] in ('COMPLETE_EXECUTION', 'COMPLETE_WITH_FAILURES')
    device = next(iter(old.values()))['device']
    for row in workers:
        OLD.verify_job(row, source, device)
    successful = [r for r in workers if r['worker_status'] == 'EXECUTED']
    attempted = {(r['kind'], tuple(r['case'])): r for r in workers}
    rows = {(r['kind'], tuple(r['case'])): r for r in successful}
    scores, decisions = 0, 0
    cases = []
    for case in diagnostic_cases()+new_cases():
        if not any((kind, case) in attempted for kind in ('FP', 'posterior')):
            continue
        n, law, seed = case
        hidden, edges, train, evaluation = data(case)
        counts = counts_from_training(n, train)
        unseen = unseen_pairs(n, edges)
        fp = rows.get(('FP', case))
        baseline = old['posterior', case] if case in diagnostic_cases() else rows.get(('posterior', case))
        details, full_ce = {}, None
        if baseline is not None:
            assert baseline['counts'] == [list(r) for r in counts]
            checked, full_ce = check_baseline(baseline, n, counts, law, hidden, unseen,
                                            historical=case in diagnostic_cases())
            scores += checked
        if fp is not None:
            assert fp['counts'] == [list(r) for r in counts]
            checked, details = check_fp(fp, n, counts, hidden, train, evaluation, unseen)
            scores += checked
            decisions += fp['native_candidate'] is not None
        if case in diagnostic_cases():
            previous = old['FP', case]
            assert previous['counts'] == [list(r) for r in counts]
            OLD.check_fp(previous, n, counts, hidden, train, evaluation, unseen)
            details['future_information_control'] = future_information_control(counts, evaluation, n)
        else:
            previous = None
        cases.append({'case': list(case), 'split': 'diagnostic' if case in diagnostic_cases() else 'new',
            'FP': fp, 'posterior': baseline, 'old_FP': previous,
            'FP_attempt_status': attempted.get(('FP', case), {}).get('worker_status', 'NOT_ATTEMPTED'),
            'posterior_full_domain_CE_recomputed': full_ce,
            'balanced_edges': sum(a == b for _, _, a, b in counts),
            'incorrect_untied_edges': sum(a != b and (b > a) != bool(hidden[i]^hidden[j]) for i, j, a, b in counts),
            **details})
    groups = []
    for n, law in dict.fromkeys((r['case'][0], r['case'][1]) for r in cases):
        selected = [r for r in cases if r['case'][:2] == [n, law]]
        models = [r['FP'] for r in selected if r['FP'] is not None]
        controls = [r['posterior'] for r in selected if r['posterior'] is not None]
        candidates = [r for r in models if r['frozen_candidate_unseen'] is not None]
        groups.append({'n': n, 'law': law, 'FP_workers': len(models), 'candidates': len(candidates),
            'installs': sum(r['install_cursor'] is not None for r in models),
            'unresolved_classes': sum(r['reference_proofs'] == 0 for r in models),
            'candidate_CE_mean': mean(r['frozen_candidate_unseen']['expected_CE_binary64'] for r in candidates) if candidates else None,
            'deployed_CE_mean': mean(r['deployed_stream_unseen']['expected_CE_binary64'] for r in models) if models else None,
            'posterior_AMP_CE_mean': mean(r['AMP_unseen']['expected_CE_binary64'] for r in controls) if controls else None,
            'candidate_full_domain_CE_mean': mean(r['frozen_candidate_full_domain']['expected_CE_binary64'] for r in candidates) if candidates else None,
            'deployed_full_domain_CE_mean': mean(r['deployed_stream_full_domain']['expected_CE_binary64'] for r in models) if models else None,
            'posterior_full_domain_CE_mean': mean(r['posterior_full_domain_CE_recomputed'] for r in selected if r['posterior'] is not None) if controls else None})
    fps = [r for r in successful if r['kind'] == 'FP']
    baselines = [r for r in successful if r['kind'] == 'posterior']
    summary = {'source': source, 'status': report['status'], 'new_workers': len(workers),
        'executed_workers': len(successful), 'failed_attempts': len(workers)-len(successful),
        'recomputed_new_score_records': scores, 'recomputed_prospective_decisions': decisions,
        'FP_run_status': dict(Counter(r['run_status'] for r in fps)),
        'FP_search_status': dict(Counter(r['cutoff_search_status'] for r in fps)),
        'FP_final_policy_stage': dict(Counter(r['final_policy_stage'] for r in fps)),
        'CUDA_phases': sum(r['independent_CUDA']['phases'] for r in fps),
        'binary64_phases': sum(r['independent_binary64_phases'] for r in fps),
        'new_posterior_GPU_forecasts': sum(r['complete_domain_raw_predictions_checked'] for r in baselines),
        'groups': groups,
        'maximum_job_commit': max((r['completed_job']['peak_job_commit'] for r in workers), default=0),
        'maximum_FP_packed_bytes': max((r['resources']['peak_packed_bytes'] for r in fps), default=0),
        'maximum_FP_native_extent': max((r['resources']['consumed_native_arena_extent'] for r in fps), default=0),
        'cases_with_tied_or_incorrect_edges': [r['case'] for r in cases if r['balanced_edges'] or r['incorrect_untied_edges']]}
    diagnostics = [r for r in cases if r['split'] == 'diagnostic']
    if len(diagnostics) == 2 and all(r['FP'] is not None and r['FP']['native_candidate'] is not None for r in diagnostics):
        a, b = diagnostics
        assert a['FP']['counts'] == b['FP']['counts']
        assert a['FP']['components'] == b['FP']['components']
        assert a['FP']['proposal_assignment'] == b['FP']['proposal_assignment']
        for r in diagnostics:
            assert r['FP']['frozen_candidate_unseen'] == r['posterior']['AMP_unseen']
        candidate = mean(r['FP']['frozen_candidate_unseen']['expected_CE_binary64'] for r in diagnostics)
        old_candidate = mean(r['old_FP']['frozen_candidate_unseen']['expected_CE_binary64'] for r in diagnostics)
        assert isclose(old_candidate-candidate, F(8, 11)*log(5/3), rel_tol=0, abs_tol=2**-42)
        summary['known_equal_world'] = {'v2_frozen_candidate_CE': old_candidate,
            'v3_frozen_candidate_CE': candidate, 'frozen_CE_improvement': old_candidate-candidate,
            'v2_deployed_CE': mean(r['old_FP']['deployed_stream_unseen']['expected_CE_binary64'] for r in diagnostics),
            'v3_deployed_CE': mean(r['FP']['deployed_stream_unseen']['expected_CE_binary64'] for r in diagnostics)}
        summary['zero_gain_label_changes_future_conditional_prediction'] = [
            r['future_information_control'] for r in diagnostics]
    assert 'torch' not in sys.modules
    return cases, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--partial', action='store_true')
    parser.add_argument('--plot', action='store_true')
    parser.add_argument('--preview')
    args = parser.parse_args()
    assert not (args.partial and (args.plot or args.preview))
    cases, summary = verify(partial=args.partial)
    if args.plot:
        plot(cases, summary, args.preview)
    else:
        assert args.preview is None
    print(json.dumps(summary, indent=2))


def plot(cases, summary, preview=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FormatStrFormatter
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
        'svg.fonttype': 'none', 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.9), gridspec_kw={'width_ratios': [1, 1.5]})
    blue, orange, green = '#1874A8', '#CE7430', '#247B58'
    known = summary['known_equal_world']
    for offset, version, color in ((-.18, 'v2', orange), (.18, 'v3', blue)):
        values = [known[version+'_frozen_candidate_CE'], known[version+'_deployed_CE']]
        bars = axes[0].bar([offset, 1+offset], values, width=.32, color=color,
                           label='v2 hard guess' if version == 'v2' else 'v3 component uncertainty')
        axes[0].bar_label(bars, fmt='%.3f', padding=4, fontsize=9)
    axes[0].set_xticks((0, 1), ('Frozen at train cutoff', 'Actual deployed stream'))
    axes[0].set_ylim(0, 1.08)
    axes[0].set_ylabel('Expected unseen cross entropy (lower is better)')
    axes[0].set_title('Known worlds A/B, equal weights', loc='left', pad=14)
    axes[0].legend(loc='upper right', frameon=False, fontsize=9)
    groups = ((8, 'iid-c2'), (16, 'iid-c2'), (8, 'iid-c4'), (16, 'iid-c4'))
    for offset, label, color, owner, key in ((-.18, 'FP frozen', blue, 'FP', 'frozen_candidate_unseen'),
            (0, 'Strong AMP posterior', green, 'posterior', 'AMP_unseen'),
            (.18, 'FP deployed', orange, 'FP', 'deployed_stream_unseen')):
        positions, values, lower, upper = [], [], [], []
        for at, group in enumerate(groups):
            selected = [r for r in cases if tuple(r['case'][:2]) == group]
            outcomes = [r[owner][key]['expected_CE_binary64'] for r in selected
                        if r[owner] is not None and r[owner][key] is not None]
            if not outcomes:
                continue
            center = mean(outcomes)
            positions.append(at+offset); values.append(center)
            lower.append(center-min(outcomes)); upper.append(max(outcomes)-center)
        axes[1].errorbar(positions, values, yerr=(lower, upper), fmt='o', color=color,
                         capsize=4, markersize=5, label=label)
    axes[1].axhline(log(2), color='#888888', linestyle=':', linewidth=1)
    axes[1].text(3.45, log(2)+.005, 'uniform', ha='right', fontsize=9, color='#666666')
    axes[1].set_xticks(range(4), ('n=8 / c=2', 'n=16 / c=2', 'n=8 / c=4', 'n=16 / c=4'))
    axes[1].set_ylim(.49, .735)
    axes[1].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    axes[1].set_title('Eight new IID forests: two seeds per group', loc='left', pad=14)
    axes[1].legend(loc='lower right', frameon=False, fontsize=9)
    for ax in axes:
        ax.grid(axis='y', alpha=.18)
        ax.set_axisbelow(True)
    fig.suptitle('Native uncertainty improves frozen risk; fresh deployment has its own cost',
                 x=.075, ha='left', fontsize=13, y=.99)
    fig.text(.075, .035, 'RN-3 / RTX 3090 / source '+SOURCE+
        '   |   bars and points are measured scores; ranges span two seeds, not confidence intervals.\n'
        'Historical v2 and posterior controls retain their original sources. Frozen and deployed models use different information cuts.',
        fontsize=8.5, color='#444444')
    fig.tight_layout(rect=(.02, .105, .995, .95), w_pad=2.4)
    fig.savefig(Path(__file__).with_name('component_uncertainty.svg'))
    if preview:
        fig.savefig(preview, dpi=150)
    plt.close(fig)


if __name__ == '__main__':
    main()
