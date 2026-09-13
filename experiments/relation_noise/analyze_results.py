"""Recompute RN-1 metrics from its compact outcomes; never rerun a GPU worker.

Scores are descriptive binary64 quantities, not ordering certificates. Exact
Brier/probability checks accompany them. Original workers independently
checked every actual CUDA word and complete reference/binary64 phase.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import json
from math import fsum, isclose, log
from pathlib import Path
from statistics import mean
import subprocess
import sys

from model import ROOT, cases, counts_from_training, data, posterior, unseen_pairs
from audit_cuda_learner import HALF, SINGLE

SOURCE = '5b050c70cea7b51de70eea1ddf6be761fc4afbc3'
RESULT = ROOT/'evidence/minimal/FP_RELATION_NOISE_EXPERIMENT.json'


def check_score(record, predictions, hidden, pairs, raw=None):
    """Use binary Brier decomposition and fsum, independent of worker score()."""
    q = {pair: F(9, 10) if hidden[pair[0]] ^ hidden[pair[1]] else F(1, 10)
         for pair in pairs}
    ce = fsum(-float(q[pair])*log(float(predictions[pair][1]))
              -float(1-q[pair])*log(float(predictions[pair][0])) for pair in pairs)/len(pairs)
    brier = sum((2*v*(1-v)+2*(predictions[pair][1]-v)**2 for pair, v in q.items()), F(0))/len(pairs)
    gap = sum((abs(predictions[pair][1]-v) for pair, v in q.items()), F(0))/len(pairs)
    mistakes = sum((F(1, 2) if predictions[pair][0] == predictions[pair][1]
                    else F((predictions[pair][1] > F(1, 2)) != (v > F(1, 2)))
                    for pair, v in q.items()), F(0))/len(pairs)
    assert record['contexts'] == len(pairs)
    assert isclose(record['expected_CE_binary64'], ce, rel_tol=0, abs_tol=2**-42)
    assert F(record['expected_Brier_exact']) == brier
    assert F(record['mean_true_probability_gap']) == gap
    assert F(record['latent_relation_error_with_half_ties']) == mistakes
    if raw is not None:
        ce_raw = fsum(-float(v)*log(float(raw[pair][1]))-float(1-v)*log(float(raw[pair][0]))
                      for pair, v in q.items())/len(pairs)
        assert isclose(record['raw_division_expected_CE_binary64'], ce_raw, rel_tol=0, abs_tol=2**-42)


def encode_posterior(exact):
    normalized, raw = {}, {}
    for pair, probabilities in exact.items():
        excesses = []
        for value in probabilities:
            target = 10*value-1
            word = HALF.rounded(target)
            word -= int(HALF.decode(word) > target)
            assert HALF.decode(word) <= target < HALF.decode(word+1)
            excesses.append(HALF.decode(word))
        masses = tuple(SINGLE.decode(SINGLE.rounded(1+value)) for value in excesses)
        total = SINGLE.decode(SINGLE.rounded(sum(masses)))
        assert sum(masses) <= 10 and total <= 10
        normalized[pair] = tuple(value/sum(masses) for value in masses)
        raw[pair] = tuple(SINGLE.decode(SINGLE.rounded(value/total)) for value in masses)
    return normalized, raw


def verify():
    report = json.loads(RESULT.read_text(encoding='utf-8'))
    assert report['status'] == 'COMPLETE_EXECUTION' and report['registration_source'] == SOURCE
    workers = report['workers']
    expected = [(kind, case) for case in cases() for kind in ('FP', 'posterior')]
    assert [(r['kind'], tuple(r['case'])) for r in workers] == expected
    # Historical workers stay bound to SOURCE; no current Runtime is executed
    # here. Guard the retained experiment and actual metric/rounding dependencies,
    # rather than preventing future solver work or relabelling old outcomes.
    changed = subprocess.check_output(['git', 'diff', SOURCE, '--',
        'src/reference_compiler/fp_reference/core.py',
        'src/reference_compiler/fp_reference/semantics.py',
        'src/reference_compiler/fp_reference/numerics.py',
        'src/reference_compiler/fp_reference/binary_arithmetic.py',
        'scripts/audit_reference_acceleration.py', 'scripts/audit_cuda_learner.py',
        'scripts/audit_cuda_primitives.py', 'experiments/relation_noise/PROTOCOL.md',
        'experiments/relation_noise/model.py', 'experiments/relation_noise/run_experiment.py'],
        cwd=ROOT, text=True, encoding='utf-8')
    assert not changed
    device = workers[0]['device']
    assert device['native']['uuid'] == 'GPU-229f6784-2b41-5313-3f21-e30f26b0bf5c'
    assert device['physical_vram_upper'] == 24 << 30
    for row in workers:
        assert row['execution_source'] == SOURCE and row['device'] == device
        job = row['completed_job']
        assert job['exit_code'] == 0 and not job['timed_out'] and job['attached_before_resume']
        assert job['commit_limit'] == 4 << 30
        assert max(job['peak_process_commit'], job['peak_job_commit']) <= job['commit_limit']
        assert job['limit_terminated_processes'] == 0
        if row['kind'] == 'FP':
            host = row['host']
            assert (host['process_id'], host['creation_100ns']) == (job['process_id'], job['process_creation_100ns'])
            assert host['lifetime_process_commit_peak'] <= job['peak_process_commit']
        else:
            assert row['process_id'] == job['process_id']

    diagnosed_scales, checked_scores = [], 0
    for index, case in enumerate(cases()):
        fp, baseline = workers[2*index:2*index+2]
        n, law, seed = case
        hidden, edges, train, evaluation = data(case)
        counts = counts_from_training(n, train)
        assert fp['counts'] == baseline['counts'] == [list(row) for row in counts]
        assert (fp['training_events'], fp['evaluation_events']) == (len(train), n*n)
        domain = unseen_pairs(n, edges)
        exact = posterior(n, counts, law)
        amp, raw = encode_posterior(exact)
        check_score(baseline['exact_unseen'], exact, hidden, domain)
        check_score(baseline['AMP_unseen'], amp, hidden, domain, raw)
        checked_scores += 2
        assert baseline['complete_domain_raw_predictions_checked'] == n*n
        assert baseline['maximum_exact_integer_bits'] == max(max(v.numerator.bit_length(), v.denominator.bit_length())
            for row in exact.values() for v in row) <= 32768
        assert F(baseline['maximum_AMP_mass_probability_error']) == max(abs(amp[pair][y]-exact[pair][y])
            for pair in exact for y in (0, 1))
        resources = baseline['resources']
        assert resources['materialized_half_table_bytes'] == 4*n*n
        assert resources['native_tensor_peak_bytes'] <= 16 << 20
        assert resources['native_allocator_peak_reserved_bytes'] <= 32 << 20
        assert fp['run_status'] == 'SEALED_CUDA_STREAM'
        assert fp['independent_CUDA']['phases'] == fp['independent_binary64_phases']
        assert fp['independent_CUDA']['actual_arena_bytes'] == 16 << 20
        assert fp['independent_CUDA']['maximum_output_cells'] <= 4096
        assert fp['independent_CUDA']['largest_phase_frame_used'] <= 131072
        assert fp['resources']['consumed_native_arena_extent'] <= 16 << 20
        assert fp['resources']['peak_packed_bytes'] <= 1 << 30

        uniform = {pair: (F(1, 2), F(1, 2)) for pair in exact}
        if law == 'iid':
            assert fp['cutoff_search_status'] == fp['proposal_status'] == fp['final_policy_stage'] == 'UNRESOLVED'
            assert fp['proposal_reason'] == 'the empirical construction needs values absent from the registered initializer'
            assert fp['native_candidate'] is None and fp['frozen_candidate_unseen'] is None
            assert fp['actually_compared'] == fp['reference_proofs'] == 0
            assert fp['install_cursor'] is None and F(fp['alpha_spent']) == 0
            check_score(fp['deployed_stream_unseen'], uniform, hidden, domain, uniform)
            checked_scores += 1
            # Post hoc explanation only: no counterfactual candidate gains an
            # actual construction, forecast, freshness or installation result.
            assert all(a != b and (b > a) == bool(hidden[i] ^ hidden[j]) for i, j, a, b in counts)
            majority = sum(max(a, b) for _, _, a, b in counts)
            minority = sum(min(a, b) for _, _, a, b in counts)
            scale = F(majority-minority, minority)
            assert scale not in (1, 8)
            # Exact pooled likelihoods for reachable readout scales 8, 1, 0.
            assert 9**majority*3**(majority+minority) > 2**majority*10**(majority+minority)
            assert 9**majority*2**(majority+minority) > 10**(majority+minority)
            diagnosed_scales.append([list(case), str(scale)])
        else:
            assert fp['cutoff_search_status'] == 'REFERENCE_CLASS_BOUNDED'
            assert fp['proposal_status'] == 'PROPOSED_NATIVE'
            assert fp['actually_compared'] == fp['reference_proofs'] == 1 and F(fp['alpha_spent']) == F(1, 2)
            graph = fp['native_candidate']
            assert (graph['nodes'], graph['sources'], graph['SUMs'], graph['PRODUCTs'], graph['edges'], graph['slots']) == (2*n+10, 2*n, 6, 4, 2*n+12, 2)
            assignment = [0]*n
            for i, j, a, b in counts:
                assert j == i+1 and sorted((a, b)) == [1, 9]
                assignment[j] = assignment[i] ^ int(b > a)
            assert fp['proposal_assignment'] == assignment
            candidate = {pair: ((F(1, 10), F(9, 10)) if assignment[pair[0]] ^ assignment[pair[1]]
                                 else (F(9, 10), F(1, 10))) for pair in exact}
            candidate_raw = {pair: tuple(SINGLE.decode(SINGLE.rounded(v)) for v in values)
                             for pair, values in candidate.items()}
            check_score(fp['frozen_candidate_unseen'], candidate, hidden, domain, candidate_raw)
            install = fp['install_cursor']
            if law == 'disconnected-b':
                assert install is None and fp['final_policy_stage'] == 'EVIDENCE'
            else:
                assert install is not None and install % 10 == 0 and install >= len(train)
                assert fp['final_policy_stage'] == 'INSTALLED_CUDA'
            deployed, deployed_raw = {}, {}
            for offset, (i, j, _) in enumerate(evaluation):
                used = install is not None and len(train)+offset >= install
                deployed[i, j] = candidate[i, j] if used else uniform[i, j]
                deployed_raw[i, j] = candidate_raw[i, j] if used else uniform[i, j]
            check_score(fp['deployed_stream_unseen'], deployed, hidden, domain, deployed_raw)
            checked_scores += 2

    a, ba, b, bb = workers[-4:]
    assert a['counts'] == b['counts'] and a['proposal_assignment'] == b['proposal_assignment']
    assert ba['AMP_unseen'] == bb['AMP_unseen']
    paired_gap = mean(row['frozen_candidate_unseen']['expected_CE_binary64'] for row in (a, b))-ba['AMP_unseen']['expected_CE_binary64']
    assert isclose(paired_gap, F(8, 11)*log(5/3), rel_tol=0, abs_tol=2**-42)
    fp = workers[::2]
    baselines = workers[1::2]
    groups = []
    for n in (8, 16):
        for law in ('conditioned', 'iid'):
            chosen = [r for r in fp if r['case'][:2] == [n, law]]
            controls = [r for r in baselines if r['case'][:2] == [n, law]]
            groups.append({'n': n, 'law': law, 'installed': sum(r['install_cursor'] is not None for r in chosen),
                'candidate_CE': None if law == 'iid' else mean(r['frozen_candidate_unseen']['expected_CE_binary64'] for r in chosen),
                'deployed_CE_mean': mean(r['deployed_stream_unseen']['expected_CE_binary64'] for r in chosen),
                'posterior_AMP_CE_mean': mean(r['AMP_unseen']['expected_CE_binary64'] for r in controls),
                'posterior_AMP_CE_range': [min(r['AMP_unseen']['expected_CE_binary64'] for r in controls), max(r['AMP_unseen']['expected_CE_binary64'] for r in controls)]})
    assert 'torch' not in sys.modules
    return workers, {'workers': len(workers), 'independently_recomputed_score_records': checked_scores,
        'FP_run_status': dict(Counter(r['run_status'] for r in fp)),
        'FP_search_status': dict(Counter(r['cutoff_search_status'] for r in fp)),
        'FP_final_policy_stage': dict(Counter(r['final_policy_stage'] for r in fp)),
        'independently_replayed_CUDA_phases': sum(r['independent_CUDA']['phases'] for r in fp),
        'independently_replayed_binary64_phases': sum(r['independent_binary64_phases'] for r in fp),
        'baseline_actual_GPU_forecasts_checked': sum(r['complete_domain_raw_predictions_checked'] for r in baselines),
        'groups': groups, 'post_hoc_IID_pooled_scales': diagnosed_scales,
        'disconnected_paired_candidate_CE_excess': paired_gap,
        'maximum_baseline_AMP_probability_error': str(max(F(r['maximum_AMP_mass_probability_error']) for r in baselines)),
        'FP_peak_resources': {key: max(r['resources'][key] for r in fp) for key in fp[0]['resources']},
        'baseline_peak_resources': {key: max(r['resources'][key] for r in baselines) for key in baselines[0]['resources']},
        'maximum_completed_job_commit': max(r['completed_job']['peak_job_commit'] for r in workers)}


def plot(workers, preview=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({'svg.fonttype': 'none', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.6), gridspec_kw={'width_ratios': [1, 1, 1.15]})
    series = [('frozen_candidate_unseen', '#2867a8', 'o', -.14, 'FP candidate, frozen at training cutoff'),
              ('AMP_unseen', '#198369', 's', 0, 'AMP posterior, same training cutoff'),
              ('deployed_stream_unseen', '#c16b22', 'x', .14, 'FP deployed stream, future evidence allowed')]
    panels = [(8, ('conditioned', 'iid')), (16, ('conditioned', 'iid')),
              (8, ('disconnected-a', 'disconnected-b'))]
    for panel, (ax, (n, laws)) in enumerate(zip(axes, panels)):
        for x, law in enumerate(laws):
            for key, color, marker, shift, _ in series:
                chosen = [r for r in workers if r['case'][:2] == [n, law] and r.get(key) is not None]
                ax.scatter([x+shift+.025*(r['case'][2]-1.5 if panel < 2 else 0) for r in chosen],
                           [r[key]['expected_CE_binary64'] for r in chosen], color=color, marker=marker, s=35, zorder=3)
            if law == 'iid':
                ax.text(x-.14, .46, 'No FP\ncandidate', ha='center', color='#2867a8', fontsize=9)
        ax.axhline(log(2), color='#666666', linestyle=':', linewidth=.8)
        ax.axhline(-.9*log(.9)-.1*log(.1), color='#666666', linestyle='--', linewidth=.8)
        ax.set_xlim(-.4, 1.4)
        ax.set_xticks((0, 1), ('Fixed 9:1', 'IID noise') if panel < 2 else ('World A', 'World B'))
        ax.set_ylim(.27, .75 if panel < 2 else 1.72)
        ax.set_title(f'{n} tokens, connected' if panel < 2 else '8 tokens, identical disconnected training', loc='left', fontsize=10)
        ax.grid(axis='y', alpha=.18)
    axes[0].set_ylabel('Expected CE on unseen relations')
    handles = [Line2D([], [], color=color, marker=marker, linestyle='none', label=label)
               for _, color, marker, _, label in series]
    fig.legend(handles=handles, loc='upper center', ncol=1, frameon=False, bbox_to_anchor=(.5, 1.01), fontsize=9)
    fig.text(.06, .018, 'Every seed is shown; absent candidates are not imputed. CE uses normalized retained AMP masses.\n'
             'Dashed: known-world noise floor. Dotted: uniform predictor. Deployment and frozen-model comparisons use different information cuts.',
             fontsize=9, color='#444444')
    fig.tight_layout(rect=(0, .1, 1, .82))
    svg = Path(__file__).with_name('relation_noise.svg')
    fig.savefig(svg, metadata={'Date': None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
    if preview is not None:
        fig.savefig(preview, dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    workers, summary = verify()
    if args.plot:
        plot(workers)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
