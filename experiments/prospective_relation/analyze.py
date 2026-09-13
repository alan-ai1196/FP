"""Independently rescore RN-2's recorded outcomes; no model worker is rerun."""
import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F
import json
from math import fsum, isclose, log, prod
from pathlib import Path
from statistics import mean
import sys

import run as experiment
from model import counts_from_training, data, posterior, unseen_pairs

SOURCE = '5bcbb49'
ANALYSIS_DEPENDENCIES = (
    'src/reference_compiler/fp_reference/core.py',
    'src/reference_compiler/fp_reference/semantics.py',
    'src/reference_compiler/fp_reference/numerics.py',
    'src/reference_compiler/fp_reference/binary_arithmetic.py',
    'scripts/audit_cuda_learner.py',
    'scripts/audit_cuda_primitives.py', 'experiments/relation_noise/model.py',
    'experiments/relation_noise/run_experiment.py',
    'experiments/prospective_relation/run.py', 'experiments/prospective_relation/PROTOCOL.md')
check_score = experiment.rn1_analysis.check_score
encode_posterior = experiment.rn1_analysis.encode_posterior
SINGLE = experiment.rn1.SINGLE
from fp_reference.numerics import log_enclosure


def prospective_boundary(candidate, train_count, evaluation):
    """Post-run decision audit; it grants no Runtime or future authority.

    At these zero-rate integer endpoints reference and CUDA stored-mass
    probabilities are equal. Replay their separately owned rules using the
    registered log enclosure, independently check it in 100-digit Decimal,
    and compute exact dyadic wealth without calling Runtime/next_wealth().
    """
    if candidate is None:
        return None
    lowers = {}
    for probability in set(v for row in candidate.values() for v in row):
        ratio = 2*probability  # Actual comparator stays uniform.
        enclosure = log_enclosure(ratio, terms=12, bit_limit=32768)
        with localcontext() as decimal_context:
            decimal_context.prec = 100
            dec = lambda value: Decimal(value.numerator)/Decimal(value.denominator)
            truth = dec(ratio).ln()
            assert dec(enclosure.lower) <= truth <= dec(enclosure.upper)
        assert -3 < enclosure.lower <= enclosure.upper < 3
        lowers[probability] = enclosure.lower
    wealth = F(1)
    for offset, (i, j, label) in enumerate(evaluation):
        raw = wealth*(1+lowers[candidate[i, j][label]]/4)
        wealth = F((raw.numerator*(1 << 16))//raw.denominator, 1 << 16)
        if wealth >= 4:
            # Crossed identities stop betting, but both complete learners
            # continue until the first full optimizer boundary.
            boundary = 10*((train_count+offset+10)//10)
            return boundary if boundary <= train_count+len(evaluation) else None
    return None


def verify_job(row, source, device):
    assert row['execution_source'] == source
    job = row['completed_job']
    assert job['commit_limit'] == 4 << 30 and job['attached_before_resume']
    if row['worker_status'] != 'EXECUTED':
        return
    assert row['device'] == device and job['exit_code'] == 0 and not job['timed_out']
    assert job['limit_terminated_processes'] == 0
    assert max(job['peak_process_commit'], job['peak_job_commit']) <= 4 << 30
    if row['kind'] == 'FP':
        host = row['host']
        assert (host['process_id'], host['creation_100ns']) == (job['process_id'], job['process_creation_100ns'])
        assert host['lifetime_process_commit_peak'] <= job['peak_process_commit']
    else:
        assert row['process_id'] == job['process_id']


def check_baseline(row, n, counts, law, hidden, unseen):
    exact = posterior(n, counts, law)
    amp, raw = encode_posterior(exact)
    check_score(row['exact_unseen'], exact, hidden, unseen)
    check_score(row['AMP_unseen'], amp, hidden, unseen, raw)
    assert row['complete_domain_raw_predictions_checked'] == n*n
    assert row['maximum_exact_integer_bits'] == max(max(v.numerator.bit_length(), v.denominator.bit_length())
        for values in exact.values() for v in values) <= 32768
    assert F(row['maximum_AMP_mass_probability_error']) == max(abs(amp[p][y]-exact[p][y]) for p in exact for y in (0, 1))
    resources = row['resources']
    assert resources['materialized_half_table_bytes'] == 4*n*n
    assert resources['native_tensor_peak_bytes'] <= 16 << 20
    assert resources['native_allocator_peak_reserved_bytes'] <= 32 << 20
    domain = tuple(exact)
    # All n^2 actual baseline forecasts were word-checked by the original
    # worker. This is a new descriptive rescore of that audited pipeline,
    # not an additional GPU execution or an unobserved candidate score.
    full_ce = fsum(-.9*log(float(amp[i, j][hidden[i]^hidden[j]]))
                   -.1*log(float(amp[i, j][1-(hidden[i]^hidden[j])])) for i, j in domain)/len(domain)
    return full_ce


def check_fp(row, n, counts, hidden, train, evaluation, unseen):
    assert row['run_status'] == 'SEALED_CUDA_STREAM'
    assert (row['training_events'], row['evaluation_events']) == (len(train), n*n)
    assert row['independent_CUDA']['phases'] == row['independent_binary64_phases']
    cuda = row['independent_CUDA']
    assert cuda['actual_arena_bytes'] == 16 << 20
    assert cuda['maximum_output_cells'] <= 4096 and cuda['largest_phase_frame_used'] <= 131072
    assert row['resources']['consumed_native_arena_extent'] <= 16 << 20
    assert row['resources']['peak_packed_bytes'] <= 1 << 30
    domain = tuple((i, j) for i in range(n) for j in range(n))
    uniform = {p: (F(1, 2), F(1, 2)) for p in domain}
    candidate, candidate_raw = None, None
    baseline_likelihood = F(1, 2)**len(train)
    best = baseline_likelihood
    scored = 2
    if row['native_candidate'] is not None:
        assert row['proposal_status'] == 'PROPOSED_NATIVE' and row['actually_compared'] == 1
        assert all(a != b for _, _, a, b in counts)
        assignment = [0]*n
        for i, j, a, b in counts:
            assert j == i+1
            assignment[j] = assignment[i] ^ int(b > a)
        assert row['proposal_assignment'] == assignment
        M, m = sum(max(a, b) for _, _, a, b in counts), sum(min(a, b) for _, _, a, b in counts)
        scores = tuple(((a+1)/(a+2))**M*(1/(a+2))**m for a in (F(1), F(8)))
        scale = (F(1), F(8))[scores.index(max(scores))]
        assert F(row['proposal_scale']) == scale
        graph = row['native_candidate']
        assert (graph['nodes'], graph['sources'], graph['SUMs'], graph['PRODUCTs'], graph['edges'], graph['slots']) == (
            2*n+10, 2*n, 6, 4, 2*n+12, 1 if scale == 1 else 2)
        candidate = {p: ((1/(scale+2), (scale+1)/(scale+2)) if assignment[p[0]] ^ assignment[p[1]]
                        else ((scale+1)/(scale+2), 1/(scale+2))) for p in domain}
        candidate_raw = {p: tuple(SINGLE.decode(SINGLE.rounded(v)) for v in values) for p, values in candidate.items()}
        check_score(row['frozen_candidate_unseen'], candidate, hidden, unseen, candidate_raw)
        check_score(row['frozen_candidate_full_domain'], candidate, hidden, domain, candidate_raw)
        actual_likelihood = prod(candidate[i, j][label] for i, j, label in train)
        assert actual_likelihood == max(scores) > baseline_likelihood
        best = actual_likelihood
        assert F(row['alpha_spent']) == F(1, 2)
        scored += 2
    else:
        assert row['frozen_candidate_unseen'] is None and row['frozen_candidate_full_domain'] is None
        assert row['actually_compared'] == 0 and F(row['alpha_spent']) == 0
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
    boundary = prospective_boundary(candidate, len(train), evaluation)
    if install is not None:
        assert candidate is not None and len(train) < install <= len(train)+n*n and install % 10 == 0
        assert row['final_policy_stage'] == 'INSTALLED_CUDA'
        assert install == boundary
    elif row['final_policy_stage'] == 'EVIDENCE':
        assert boundary is None
    deployed, deployed_raw = {}, {}
    for offset, (i, j, _) in enumerate(evaluation):
        used = install is not None and len(train)+offset >= install
        deployed[i, j] = candidate[i, j] if used else uniform[i, j]
        deployed_raw[i, j] = candidate_raw[i, j] if used else uniform[i, j]
    check_score(row['deployed_stream_unseen'], deployed, hidden, unseen, deployed_raw)
    check_score(row['deployed_stream_full_domain'], deployed, hidden, domain, deployed_raw)
    return scored, boundary


def verify(*, partial=False):
    report = json.loads(experiment.OUTPUT.read_text(encoding='utf-8'))
    source = experiment.git('rev-parse', SOURCE)
    assert report['registration_source'] == source and report['experiment'] == 'RN-2'
    assert report['protocol_commit'] == experiment.git('rev-parse', experiment.PROTOCOL_COMMIT)
    # Historical workers retain their execution source. Guard this rescore's
    # actual arithmetic/data dependencies; it executes no current Runtime
    # and must not forbid later solver research or documentation updates.
    # The rescore does not execute the acceleration fixture or its tests.
    # Audit logic may improve; recorded workers and model/data code stay fixed.
    assert not experiment.git('diff', source, '--', *ANALYSIS_DEPENDENCIES)
    old, reference = experiment.historical()
    assert report['historical_control'] == json.loads(json.dumps(reference))
    workers = report['workers']
    assert [(r['kind'], tuple(r['case'])) for r in workers] == list(experiment.tasks()[:len(workers)])
    assert len(workers) <= 28
    if not partial:
        assert len(workers) == 28 and report['status'] in ('COMPLETE_EXECUTION', 'COMPLETE_WITH_FAILURES')
    device = next(iter(old.values()))['device']
    for row in workers:
        verify_job(row, source, device)
    successful = [r for r in workers if r['worker_status'] == 'EXECUTED']
    attempted = {(r['kind'], tuple(r['case'])): r for r in workers}
    rows = {(r['kind'], tuple(r['case'])): r for r in successful}
    scores = 0
    decisions_replayed = 0
    cases = []
    for case in experiment.diagnostic_cases()+experiment.new_cases():
        fp = rows.get(('FP', case))
        baseline = old['posterior', case] if case in experiment.diagnostic_cases() else rows.get(('posterior', case))
        if not any((kind, case) in attempted for kind in ('FP', 'posterior')):
            continue
        n, law, seed = case
        hidden, edges, train, evaluation = data(case)
        counts = counts_from_training(n, train)
        unseen = unseen_pairs(n, edges)
        baseline_full_ce = None
        if baseline is not None:
            assert baseline['counts'] == [list(r) for r in counts]
            baseline_full_ce = check_baseline(baseline, n, counts, law, hidden, unseen)
            if case in experiment.new_cases():
                scores += 2
        boundary = None
        if fp is not None:
            assert fp['counts'] == [list(r) for r in counts]
            checked, boundary = check_fp(fp, n, counts, hidden, train, evaluation, unseen)
            scores += checked
            decisions_replayed += fp['native_candidate'] is not None
        cases.append({'case': list(case), 'split': 'diagnostic' if case in experiment.diagnostic_cases() else 'new',
            'FP': fp, 'posterior': baseline, 'posterior_full_domain_CE_recomputed': baseline_full_ce,
            'FP_attempt_status': attempted.get(('FP', case), {}).get('worker_status', 'NOT_ATTEMPTED'),
            'recomputed_evidence_ready_boundary': boundary,
            'old_FP': old['FP', case] if case in experiment.diagnostic_cases() else None,
            'strict_edge_majorities_correct': all(a != b and (b > a) == bool(hidden[i]^hidden[j]) for i, j, a, b in counts)})
    groups = []
    for split, law in (('diagnostic', 'iid'), ('new', 'iid'), ('diagnostic', 'conditioned'),
                       ('diagnostic', 'disconnected-a'), ('diagnostic', 'disconnected-b')):
        for n in (8, 16):
            selected = [r for r in cases if r['split'] == split and r['case'][:2] == [n, law]]
            if not selected:
                continue
            models = [r['FP'] for r in selected if r['FP'] is not None]
            controls = [r['posterior'] for r in selected if r['posterior'] is not None]
            values = [r['frozen_candidate_unseen']['expected_CE_binary64'] for r in models if r['frozen_candidate_unseen'] is not None]
            groups.append({'split': split, 'n': n, 'law': law, 'FP_workers': len(models),
                'candidates': len(values), 'installs': sum(r['install_cursor'] is not None for r in models),
                'unresolved_classes': sum(r['reference_proofs'] == 0 for r in models),
                'candidate_CE_mean': mean(values) if values else None,
                'candidate_CE_range': [min(values), max(values)] if values else None,
                'candidate_full_domain_CE_mean': mean(r['frozen_candidate_full_domain']['expected_CE_binary64']
                    for r in models if r['frozen_candidate_full_domain'] is not None) if values else None,
                'deployed_CE_mean': mean(r['deployed_stream_unseen']['expected_CE_binary64'] for r in models) if models else None,
                'deployed_full_domain_CE_mean': mean(r['deployed_stream_full_domain']['expected_CE_binary64'] for r in models) if models else None,
                'posterior_full_domain_CE_mean_recomputed': mean(r['posterior_full_domain_CE_recomputed']
                    for r in selected if r['posterior'] is not None) if controls else None,
                'posterior_AMP_CE_mean': mean(r['AMP_unseen']['expected_CE_binary64'] for r in controls) if controls else None,
                'posterior_AMP_CE_range': [min(r['AMP_unseen']['expected_CE_binary64'] for r in controls),
                    max(r['AMP_unseen']['expected_CE_binary64'] for r in controls)] if controls else None})
    fp_rows = [r for r in successful if r['kind'] == 'FP']
    baselines = [r for r in successful if r['kind'] == 'posterior']
    summary = {'source': source, 'status': report['status'], 'new_workers': len(workers),
        'executed_workers': len(successful), 'failed_attempts': len(workers)-len(successful),
        'recomputed_new_score_records': scores,
        'recomputed_prospective_decisions': decisions_replayed,
        'reused_RN1_control_workers': 12, 'original_RN1_recomputed_score_records': 64,
        'FP_run_status': dict(Counter(r['run_status'] for r in fp_rows)),
        'FP_search_status': dict(Counter(r['cutoff_search_status'] for r in fp_rows)),
        'FP_final_policy_stage': dict(Counter(r['final_policy_stage'] for r in fp_rows)),
        'CUDA_phases': sum(r['independent_CUDA']['phases'] for r in fp_rows),
        'binary64_phases': sum(r['independent_binary64_phases'] for r in fp_rows),
        'new_posterior_GPU_forecasts': sum(r['complete_domain_raw_predictions_checked'] for r in baselines),
        'groups': groups,
        'maximum_job_commit': max(r['completed_job']['peak_job_commit'] for r in workers),
        'maximum_FP_packed_bytes': max((r['resources']['peak_packed_bytes'] for r in fp_rows), default=0),
        'maximum_FP_native_extent': max((r['resources']['consumed_native_arena_extent'] for r in fp_rows), default=0),
        'new_cases_with_incorrect_or_tied_edges': [r['case'] for r in cases if r['split'] == 'new' and not r['strict_edge_majorities_correct']]}
    if not partial:
        disconnected = [r for r in cases if r['case'][1].startswith('disconnected')]
        if len(disconnected) == 2 and all(r['FP'] is not None and r['FP']['frozen_candidate_unseen'] is not None for r in disconnected):
            a, b = disconnected
            assert a['FP']['counts'] == b['FP']['counts'] and a['FP']['proposal_assignment'] == b['FP']['proposal_assignment']
            gap = mean(r['FP']['frozen_candidate_unseen']['expected_CE_binary64'] for r in disconnected)-a['posterior']['AMP_unseen']['expected_CE_binary64']
            assert isclose(gap, F(8, 11)*log(5/3), rel_tol=0, abs_tol=2**-42)
            summary['disconnected_equal_world_candidate_excess_CE'] = gap
    assert 'torch' not in sys.modules
    return cases, summary


def plot(cases, preview=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({'svg.fonttype': 'none', 'font.size': 9,
        'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 3, figsize=(12.8, 7.3))
    panels = [('diagnostic', 8, 'iid'), ('diagnostic', 16, 'iid'), ('diagnostic', 8, 'disconnected'),
              ('new', 8, 'iid'), ('new', 16, 'iid'), ('diagnostic', None, 'conditioned')]
    series = [('FP', 'frozen_candidate_unseen', '#2867a8', 'o', -.18, 'FP frozen candidate'),
              ('posterior', 'AMP_unseen', '#198369', 's', -.06, 'AMP posterior, same cutoff'),
              ('FP', 'deployed_stream_unseen', '#c16b22', 'x', .06, 'FP deployed stream'),
              ('old_FP', 'deployed_stream_unseen', '#999999', 'v', .18, 'RN-1 deployed stream (retained)')]
    for ax, (split, n, law) in zip(axes.flat, panels):
        selected = [r for r in cases if r['split'] == split and (n is None or r['case'][0] == n)
                    and r['case'][1].startswith(law)]
        for x, item in enumerate(selected):
            for who, key, color, marker, shift, _ in series:
                record = item[who]
                if record is not None and record.get(key) is not None:
                    ax.scatter(x+shift, record[key]['expected_CE_binary64'], color=color, marker=marker, s=29, zorder=3)
            if item['FP'] is not None and item['FP']['frozen_candidate_unseen'] is None:
                ax.text(x, .49, 'No FP\ncandidate', ha='center', color='#2867a8', fontsize=8)
            elif item['FP_attempt_status'] == 'FAILED':
                ax.text(x, .49, 'FP attempt\nfailed', ha='center', color='#2867a8', fontsize=8)
        labels = ([str(r['case'][0]) for r in selected] if law == 'conditioned' else
                  ['A', 'B'] if law == 'disconnected' else [str(r['case'][2]) for r in selected])
        ax.set_xticks(range(len(selected)), labels)
        ax.set_xlim(-.5, max(.5, len(selected)-.5))
        ax.set_ylim(.28, 1.69 if law == 'disconnected' else .73)
        ax.axhline(log(2), color='#777777', linestyle=':', linewidth=.8)
        ax.axhline(-.9*log(.9)-.1*log(.1), color='#777777', linestyle='--', linewidth=.8)
        ax.grid(axis='y', alpha=.15)
        ax.set_title(('Known disconnected worlds' if law == 'disconnected' else
                      'Known conditioned controls' if law == 'conditioned' else
                      f'{n} tokens, '+('known IID seeds' if split == 'diagnostic' else 'new IID seeds')), loc='left', fontsize=10)
        ax.set_xlabel('Tokens' if law == 'conditioned' else 'World' if law == 'disconnected' else 'Seed')
    for ax in axes[:, 0]:
        ax.set_ylabel('Expected CE on unseen relations')
    fig.legend(handles=[Line2D([], [], color=color, marker=marker, linestyle='none', label=label)
                        for _, _, color, marker, _, label in series],
               loc='upper center', ncol=2, frameon=False, bbox_to_anchor=(.5, 1.01))
    fig.text(.06, .017, 'Dashed: known-world noise floor. Dotted: uniform. All registered cases shown; no absent score is imputed.\n'
        'Deployment can use later evidence; frozen-model comparisons share the training cutoff. No population or per-world Bayes dominance claim.',
        fontsize=9, color='#444444')
    fig.tight_layout(rect=(0, .07, 1, .92))
    svg = Path(__file__).with_name('prospective_relation.svg')
    fig.savefig(svg, metadata={'Date': None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
    if preview is not None:
        fig.savefig(preview, dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--partial', action='store_true')
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    assert not (args.partial and args.plot)
    cases, summary = verify(partial=args.partial)
    if args.plot:
        plot(cases)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
