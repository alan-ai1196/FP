"""Run the real upstream estimator and independent frozen-score CPU controls.

Only deterministic synthetic token files are created. No experiment corpus,
GPU, alternative estimator or discount fallback enters this control.
"""
from pathlib import Path
import argparse
import io
import json
import math
import subprocess
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'experiments/next_token'))
from baselines.ngram import write_training_text


def run(command):
    completed = subprocess.run(list(map(str, command)), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    if completed.returncode:
        raise RuntimeError(f'{command[0]} returned {completed.returncode}: '+completed.stderr.decode('utf-8', errors='replace')[-4000:])
    return completed.stdout


def read_arpa(path):
    probabilities, backoffs, order = {}, {}, 0
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('\\') and line.endswith('-grams:'):
            order = int(line[1:].split('-')[0])
        elif line.startswith('\\'):
            order = 0
        elif order and line.strip():
            parts = line.split()
            key = tuple(parts[1:1+order])
            # Independently decode the stored float32 log probabilities/bows,
            # then use float64 arithmetic rather than the KenLM trie evaluator.
            probabilities[key] = float(np.float32(parts[0]))
            if len(parts) == order+2:
                backoffs[key] = float(np.float32(parts[-1]))
    return probabilities, backoffs


def oracle_rows(tape, vocabulary, probabilities, backoffs):
    maximum_order = max(map(len, probabilities))
    seen = {word[0] for word in probabilities if len(word) == 1 and word[0].startswith('t')}
    unseen = vocabulary-len(seen)
    history, output = ('<s>',), []
    def logprob(word):
        suffix, accumulated = history, 0.
        while suffix+(word,) not in probabilities:
            if not suffix:
                raise AssertionError('unigram missing')
            accumulated += backoffs.get(suffix, 0.)
            suffix = suffix[1:]
        return accumulated+probabilities[suffix+(word,)]
    for target in tape:
        symbols = ['t'+str(y) if 't'+str(y) in seen else '<unk>' for y in range(vocabulary)]
        logarithms = [logprob(word)*math.log(10)-(math.log(unseen) if word == '<unk>' else 0) for word in symbols]
        largest = max(logarithms)
        log_total = largest+math.log(math.fsum(math.exp(p-largest) for p in logarithms))
        output.append([math.exp(p-log_total) for p in logarithms])
        history = (history+(symbols[int(target)],))[-(maximum_order-1):]
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-root', required=True, type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    install = args.tool_root/'installed/x64-windows-static'
    tools = install/'tools/kenlm'
    scorer = args.tool_root/'report-build/Release/fp_kenlm_report.exe'
    inventory = json.loads((install/'share/kenlm/vcpkg.spdx.json').read_text(encoding='utf-8'))
    assert inventory['name'].startswith('kenlm:x64-windows-static@20230531#1 ')
    manifest = json.loads((ROOT/'experiments/next_token/baselines/kenlm/vcpkg.json').read_text(encoding='utf-8'))
    assert manifest['builtin-baseline'] == '07f4812200df3d3c931c0c8a6081d3b21fe2bf9f'
    rng = np.random.default_rng(2931)
    frequencies = np.arange(1, 65, dtype=np.float64)**-1.2
    training = rng.choice(64, size=10000, p=frequencies/frequencies.sum()).tolist()
    # Explicit singleton/doubleton/tripleton/four-continuation types keep the
    # synthetic MKN discount problem defined, without estimator fallback.
    for continuations in range(1, 5):
        for distinct in range(4):
            word = 64+4*(continuations-1)+distinct
            for preceding in range(continuations):
                training.extend((preceding, word))
    training = np.asarray(training, dtype='<u2')
    assert set(map(int, training)) == set(range(80))
    encoded = []
    for chunk in (1, 7, 65536):
        stream = io.BytesIO()
        assert write_training_text(training, stream, vocabulary=96, chunk_tokens=chunk) == len(training)
        encoded.append(stream.getvalue())
    assert encoded[0] == encoded[1] == encoded[2]
    assert encoded[0].count(b'\n') == 1 and len(encoded[0].split()) == len(training)
    eot = io.BytesIO()
    write_training_text(np.asarray([0, 50256, 50256, 1], dtype='<u2'), eot, vocabulary=50257, chunk_tokens=2)
    assert eot.getvalue() == b't0 t50256 t50256 t1\n'
    maximum_error, comparisons, refused = 0., 0, 0
    with tempfile.TemporaryDirectory(prefix='fp-kenlm-control-') as temporary:
        directory = Path(temporary)
        text, arpa, binary = directory/'train.txt', directory/'model.arpa', directory/'model.trie'
        text.write_bytes(encoded[0])
        run((tools/'lmplz.exe', '--order', '3', '--memory', '128M', '--vocab_estimate', '1000',
             '--temp_prefix', str(directory)+'/', '--text', text, '--arpa', arpa))
        run((tools/'build_binary.exe', 'trie', arpa, binary))
        probabilities, backoffs = read_arpa(arpa)
        assert set(k[0] for k in probabilities if len(k) == 1) == {'<unk>', '<s>', '</s>'}|{'t'+str(i) for i in range(80)}
        def score(tape, vocabulary, *, rows=True, context=8):
            path = directory/'report.bin'
            np.asarray(tape, dtype='<u2').tofile(path)
            command = [scorer, binary, path, vocabulary, len(tape), context]
            if rows:
                command.append('--rows')
            return json.loads(run(command))
        report_tape = (0, 70, 95, 1, 95, 64, 3, 79)
        original = score(report_tape, 96)
        for tape, vocabulary in ((report_tape, 96), ((0, 70, 1, 64, 3, 79), 80)):
            physical = score(tape, vocabulary)
            expected = oracle_rows(tape, vocabulary, probabilities, backoffs)
            for row, want in zip(physical['rows'], expected):
                got = row['probabilities']
                assert len(got) == vocabulary and abs(math.fsum(got)-1) < 2e-12
                error = max(abs(math.log(a)-math.log(b)) for a, b in zip(got, want))
                maximum_error = max(maximum_error, error)
                # The reference adds decoded float32 ARPA values in float64;
                # KenLM accumulates its backoff path in float32.
                assert error < 1e-5
                assert abs(row['nll']+math.log(got[row['target']])) < 2e-12
                comparisons += vocabulary
        for t in range(len(report_tape)):
            changed = tuple(report_tape[:t])+tuple((x+7) % 96 for x in report_tape[t:])
            result = score(changed, 96)
            assert [row['probabilities'] for row in result['rows'][:t+1]] == [
                row['probabilities'] for row in original['rows'][:t+1]]
        # Report views restart from their own initial context; no training or
        # previous report tail enters a fresh process.
        first = score((report_tape[4],), 96)
        assert first['rows'][0]['probabilities'] == original['rows'][0]['probabilities']
        full_tape = tuple(50256 if x == 95 else x for x in report_tape)
        full = score(full_tape, 50257, rows=False)
        assert full['seen_real_ids'] == 80 and full['unseen_real_ids'] == 50177
        assert full['scored_model_columns'] == 81
        assert abs(full['mean_nll_nats']-original['summary']['mean_nll_nats']
                   -2/len(report_tape)*math.log(50177/16)) < 2e-12
        for vocabulary, count, context, extra in ((96, 9, 8, []), (50257, 8, 8, ['--rows']), (50257, 8, 1, []), (79, 8, 8, [])):
            completed = subprocess.run([str(scorer), str(binary), str(directory/'report.bin'),
                str(vocabulary), str(count), str(context), *extra], capture_output=True, timeout=60)
            assert completed.returncode != 0
            refused += 1
        # Synthetic controls remain ephemeral; no trained model, ARPA or tape
        # is copied into the research evidence directory.
    assert 'torch' not in sys.modules
    result = dict(status='PASS_NATIVE_KENLM_COMPARISON_CONTROL',
        scope='upstream MKN estimator and complete-alphabet frozen score on synthetic tokens; no corpus result or selected trial',
        upstream_commit='5bf7b46558e1c5595bf3b8c9b0b1f9d8d257040a',
        vcpkg_baseline=manifest['builtin-baseline'], port='kenlm:x64-windows-static@20230531#1',
        native_tools_built=True, estimator='unpruned interpolated modified Kneser-Ney', order=3,
        synthetic_training_tokens=len(training), automatic_discounts_without_fallback=True,
        binary_kind='unquantized trie', input_chunk_sizes=[1, 7, 65536],
        one_sentence_per_tape_no_eot_reset=True, independent_float64_probability_checks=comparisons,
        maximum_independent_log_probability_difference=maximum_error, log_probability_tolerance=1e-5,
        causal_suffix_mutations=len(report_tape), full_vocabulary=50257,
        full_vocabulary_unseen_ids=50177, unknown_mass_split_control=True,
        all_seen_alphabet_excludes_unused_unknown_mass=True, malformed_reports_refused=refused,
        experiment_corpus_bytes_read=0, trained_model_or_score_retained=False, device_claim=False)
    if args.write:
        (ROOT/'evidence/minimal/FP_TEXT_NGRAM_BASELINE_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
