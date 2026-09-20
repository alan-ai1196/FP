"""Plot the complete retained n8 likelihood comparison; no worker execution."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT/'evidence/minimal'
journal = json.loads((EVIDENCE/'FP_LIKELIHOOD_MODEL_EXPERIMENT.json').read_text())
analysis = json.loads((EVIDENCE/'FP_LIKELIHOOD_MODEL_ANALYSIS.json').read_text())
old = json.loads((EVIDENCE/'FP_JOINT_UNCERTAINTY_EXPERIMENT.json').read_text())
assert journal['status'] == analysis['journal_status'] == 'COMPLETE_EXECUTION'
assert len(journal['workers']) == analysis['sealed_workers'] == 4
assert journal['registration_source'] == analysis['execution_source']
cases = [row['case'] for row in journal['workers']]
new = [row['result'] for row in journal['workers']]
prior = {(tuple(row['case']), row['rate']): row for row in old['workers'] if row['kind'] == 'FP'}
assert all(row['worker_status'] == 'EXECUTED' and row['result']['run_status'] == 'SEALED_CUDA_STREAM'
           for row in journal['workers'])
plt.rcParams.update({'svg.fonttype': 'none', 'font.size': 10, 'axes.spines.top': False,
                     'axes.spines.right': False})
fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.8), sharey=True)
labels = ['c2 / seed16', 'c2 / seed17', 'c4 / seed18', 'c4 / seed19']
for ax, key, title in zip(axes, ('candidate_stream_unseen', 'deployed_stream_unseen'),
                          ('Candidate predictions', 'Actually deployed predictions')):
    for rate, offset, color, marker in (('1', -.19, '#c96b24', 's'), ('4', 0, '#9b6aa5', '^')):
        values = [prior[tuple(case), rate][key]['expected_CE_binary64'] for case in cases]
        ax.scatter([i+offset for i in range(4)], values, color=color, marker=marker, s=48,
                   label='RN-5 polynomial, rate'+rate, zorder=3)
    actual = [row['scores'][key]['expected_CE_binary64'] for row in new]
    ax.scatter([i+.19 for i in range(4)], actual, color='#147b9e', marker='o', s=55,
               label='Owned likelihood learner', zorder=4)
    if key.startswith('candidate'):
        control = [row['scores']['adaptive_exact_unseen']['expected_CE_binary64'] for row in new]
        ax.scatter([i+.19 for i in range(4)], control, color='#152c39', marker='x', s=24,
                   linewidths=1.1, label='Retained exact posterior', zorder=5)
    else:
        ax.axhline(0.6931471805599453, color='#929a9e', linestyle=':', linewidth=1)
        ax.text(3.34, .6931471805599453+.006, 'uniform', ha='right', color='#677279', fontsize=9)
        for i, row in enumerate(new):
            wait = row['install_cursor']-row['training_events']
            ax.annotate(str(wait)+' fresh', (i+.19, actual[i]), xytext=(0, -16),
                        textcoords='offset points', ha='center', fontsize=8, color='#147b9e')
    ax.set_title(title, loc='left', fontweight='bold')
    ax.set_xticks(range(4), labels)
    ax.set_xlim(-.4, 3.45)
    ax.set_ylim(.315, .725)
    ax.grid(axis='y', color='#e5eaec', linewidth=.7)
    ax.set_axisbelow(True)
axes[0].set_ylabel('Expected unseen-relation CE (nats; lower is better)')
handles, names = axes[0].get_legend_handles_labels()
fig.legend(handles, names, loc='lower center', bbox_to_anchor=(.5, .035), ncol=2, frameon=False)
fig.suptitle('n8: posterior learning completes; fresh-evidence delay remains', x=.06, ha='left', fontsize=14)
fig.text(.06, .014, 'Four retained cases; matched tapes, different learners/resources. No new IID or single-mechanism causal claim.',
         fontsize=8, color='#52616a')
fig.subplots_adjust(left=.075, right=.98, top=.84, bottom=.27, wspace=.12)
path = Path(__file__).with_name('likelihood_model_results.svg')
fig.savefig(path, metadata={'Date': None})
path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',
                encoding='utf-8')
print(path)
