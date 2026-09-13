"""Verify the compact experiment record and plot its measured critical-cap curves."""
import argparse
from collections import Counter
from fractions import Fraction as F
import json
from pathlib import Path

import resource_frontier as experiment
from fp_reference.learner import ce_gradient
from fp_reference.semantics import evaluate
from audit_cuda_learner import SINGLE
from audit_reference_events import forward_oracle

ROOT = experiment.ROOT
EVIDENCE = ROOT/'evidence/minimal/FP_ERC1_RTX3090_FRONTIER.json'


def verify():
    report = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    assert report['experiment'] == 'ERC1-RTX3090-1' and report['execution_status'] == 'COMPLETE_EXECUTION'
    assert report['executed_configurations'] == 54
    rows = report['results']
    assert tuple(tuple(r['case']) for r in rows) == experiment.configurations()
    experiment.unchanged_registration(report['registration_source'])
    for revision in {r['execution_source'] for r in rows}:
        experiment.unchanged_registration(revision)
    gradient_vectors = 0
    for row in rows:
        cfg, graph, run, tape, exact = experiment.build(*row['case'])
        assert row['native'] == graph.counts() and F(row['cap']) == cfg.normalizer_cap
        assert F(row['reference']['error']) == exact['error']
        assert row['reference']['maximum_significand_bits'] == exact['maximum_significand_bits']
        assert row['reference']['direct_materialization_bits'] == exact['direct_bit_volume']
        assert row['reference']['probabilities_included_bits'] == exact['including_rational_predictions_bits']
        assert F(row['reference']['minimum_positive_activation']) == min(v for vs in exact['values'] for v in vs if v)
        for values in experiment.domain(1):
            sources = dict(zip((s.source_id for s in cfg.semantics.sources), values))
            prediction = evaluate(graph, cfg.semantics, experiment.PATTERN, sources,
                                  bit_limit=cfg.reference_integer_bits)
            probability, gradients = forward_oracle(graph, cfg.semantics, experiment.PATTERN, sources)
            assert probability == prediction.probabilities
            for label in range(len(cfg.semantics.base)):
                assert ce_gradient(graph, experiment.PATTERN, prediction, label,
                    bit_limit=cfg.reference_integer_bits) == gradients[label]
                gradient_vectors += 1
        sealed = row['run_status'] == 'SEALED_CUDA_STREAM'
        assert row['run_status'] in ('SEALED_CUDA_STREAM', 'HALTED_UNRESOLVED')
        if sealed:
            expected_phases = 1+2*len(tape)+len(tape)//2
            assert row['cursor'] == row['independent_reference_events'] == len(tape)
            assert row['endpoint_failure'] is None
            assert row['cuda']['checked'] == row['binary64']['checked'] == expected_phases
            assert row['cuda']['failed_complete_outputs_replayed'] == row['binary64']['failed_complete_outputs_replayed'] == 0
            assert F(row['cuda']['max_complete_state_error_including_failure']) <= F(1, 100)
        else:
            assert row['endpoint_failure'] and row['cursor'] < len(tape)
            assert row['cuda']['failed_complete_outputs_replayed']+row['binary64']['failed_complete_outputs_replayed'] == 1
        metrics = row['predictions']
        contexts = metrics['retained_contexts']
        assert metrics['complete_checked_context_domain'] == sealed
        if sealed:
            assert [r['context'] for r in contexts] == [0, 1]
        errors = []
        for context in contexts:
            masses = tuple(SINGLE.decode(w) for w in context['mass_words'])
            normalizer = SINGLE.decode(context['normalizer_word'])
            probability = tuple(SINGLE.decode(w) for w in context['prediction_words'])
            assert tuple(context['prediction_words']) == tuple(SINGLE.rounded(m/normalizer) for m in masses)
            target = experiment.TABLES[row['case'][0]][context['context']]
            a = max(abs(m/sum(masses)-q) for m, q in zip(masses, target))
            b = max(abs(p-q) for p, q in zip(probability, target))
            assert F(context['mathematical_mass_error']) == a
            assert F(context['rounded_prediction_error']) == b
            if context['status'] == 'CHECKED_CUDA_PREFIX_PHASE':
                assert normalizer <= cfg.normalizer_cap and sum(masses) <= cfg.normalizer_cap
            else:
                assert context['status'] == 'UNRESOLVED' and not sealed
            errors.append((a, b))
        if sealed:
            assert F(metrics['mathematical_mass_error']) == max(a for a, _ in errors)
            assert F(metrics['rounded_prediction_error']) == max(b for _, b in errors)
        else:
            assert metrics['mathematical_mass_error'] is metrics['rounded_prediction_error'] is None
        resources, job, host = row['resources'], row['completed_job'], row['host']
        assert resources['peak_packed_bytes'] <= 1 << 30
        assert resources['consumed_native_arena_extent'] <= 16 << 20
        assert resources['largest_phase_frame_used'] <= 131072 and resources['maximum_output_cells'] <= 4096
        assert job['exit_code'] == 0 and not job['timed_out'] and job['attached_before_resume']
        assert job['commit_limit'] == experiment.HOST_CAP
        assert host['lifetime_process_commit_peak'] <= job['peak_process_commit'] <= experiment.HOST_CAP
        assert job['peak_job_commit'] <= experiment.HOST_CAP
        assert (host['process_id'], host['creation_100ns']) == (job['process_id'], job['process_creation_100ns'])
    assert gradient_vectors == 270
    # This figure is empirical; these finite comparisons do not assert an
    # optimum over omitted Programs, formats, policies or parameter values.
    critical = [r for r in rows if r['case'][1] in experiment.METHODS[:3] and r['run_status'] == 'SEALED_CUDA_STREAM']
    floors = {target: min(F(r['predictions']['mathematical_mass_error']) for r in critical if r['case'][0] == target)
              for target in experiment.TABLES}
    assert floors == {'scalar': F(1, 43688), 'mixed': F(1, 65532)}
    for target in experiment.TABLES:
        reciprocal = [r for r in critical if r['case'][0] == target and r['case'][1] == 'reciprocal' and r['case'][2] >= 3]
        assert len(reciprocal) == 3
        assert all(F(r['predictions']['mathematical_mass_error']) == floors[target] for r in reciprocal)
        assert F(reciprocal[-1]['reference']['error']) < F(reciprocal[0]['reference']['error'])/10**14
    summary = {'configurations': len(rows), 'status': dict(Counter(r['run_status'] for r in rows)),
        'independent_CUDA_outputs': sum(r['cuda']['checked']+r['cuda']['failed_complete_outputs_replayed'] for r in rows),
        'independent_binary64_outputs': sum(r['binary64']['checked']+r['binary64']['failed_complete_outputs_replayed'] for r in rows),
        'reference_events': sum(r['independent_reference_events'] for r in rows),
        'independent_exact_gradient_vectors': gradient_vectors,
        'observed_critical_mass_error_minima': {k: str(v) for k, v in floors.items()},
        'failures': dict(Counter(r['endpoint_failure'][2] for r in rows if r['endpoint_failure'])),
        'peak_resources': {key: max(r['resources'][key] for r in rows) for key in rows[0]['resources']},
        'maximum_completed_job_commit': max(r['completed_job']['peak_job_commit'] for r in rows)}
    return rows, summary


def plot(rows, preview=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({'svg.fonttype': 'none', 'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False})
    colors = {'horner': '#c16b22', 'fractional-horner': '#2867a8', 'reciprocal': '#198369'}
    names = {'horner': 'Ordinary Horner', 'fractional-horner': 'Fractional Horner', 'reciprocal': 'Shared reciprocal'}
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.7), sharey=True)
    for ax, target in zip(axes, experiment.TABLES):
        for method, color in colors.items():
            selected = [r for r in rows if r['case'][0] == target and r['case'][1] == method]
            counts = [r['native']['SUMs']+r['native']['PRODUCTs'] for r in selected]
            ax.plot(counts, [float(F(r['reference']['error'])) for r in selected],
                    '--', color=color, linewidth=1.3, marker='.', alpha=.75)
            checked = [r for r in selected if r['run_status'] == 'SEALED_CUDA_STREAM']
            ax.plot([r['native']['SUMs']+r['native']['PRODUCTs'] for r in checked],
                    [float(F(r['predictions']['mathematical_mass_error'])) for r in checked],
                    '-o', color=color, markersize=4, linewidth=1.7)
            for row, count in zip(selected, counts):
                if row['run_status'] != 'SEALED_CUDA_STREAM':
                    ax.text(count, 1.04, 'U', color=color, ha='center', transform=ax.get_xaxis_transform())
        cap = '8/3' if target == 'scalar' else '4'
        ax.set_title(target.capitalize()+' table, T <= '+cap, loc='left', pad=12)
        ax.set_yscale('log')
        ax.set_ylim(1e-22, 1e-2)
        ax.set_xlabel('SUM + PRODUCT nodes (two additional sources)')
        ax.set_yticks([10.**i for i in (-2, -6, -10, -14, -18, -22)])
        ax.grid(axis='y', alpha=.2)
    axes[0].set_ylabel('Maximum probability error on both contexts')
    handles = [Line2D([], [], color=color, linewidth=2, label=names[method]) for method, color in colors.items()]
    handles += [Line2D([], [], color='#555555', linestyle='--', label='Exact reference'),
                Line2D([], [], color='#555555', marker='o', label='Normalized retained AMP masses')]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(.5, 1.0))
    fig.text(.08, .015, 'U: unresolved complete run; no AMP error is plotted. Fixed RTX 3090 half/single executor.\n'
             'These are measured registered constructions, not a complete graph frontier or a GPU memory/speedup claim.',
             fontsize=9, color='#444444')
    fig.tight_layout(rect=(0, .095, 1, .84))
    svg = Path(__file__).with_name('resource_frontier.svg')
    fig.savefig(svg, metadata={'Date': None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
    if preview is not None:
        fig.savefig(preview, dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    rows, summary = verify()
    if args.plot:
        plot(rows)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
