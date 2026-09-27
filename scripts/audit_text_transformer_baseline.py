"""CPU controls for the ordinary-text Transformer adapter; no corpus or GPU."""
from pathlib import Path
import argparse
import json
import sys

import numpy as np
import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'experiments/next_token'))
from baselines.transformer import Spec, Transformer, training_batch, reporting_inputs, normalized_nll, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    torch.set_num_threads(1)
    spec = Spec(vocabulary=5, context=8, layers=2, heads=2, width=16, dropout=0., bias=True)
    random_before = torch.random.get_rng_state().clone()
    model = Transformer(spec, seed=481).double()
    assert torch.equal(random_before, torch.random.get_rng_state())
    twin = Transformer(spec, seed=481).double()
    assert all(torch.equal(a, b) for a, b in zip(model.parameters(), twin.parameters()))
    tape = np.asarray([0, 1, 4, 2, 1, 3, 0, 4, 2, 3, 1, 0, 2, 4, 4, 1, 0, 3, 2], dtype=np.uint16)
    inputs, targets = training_batch(tape, [-1, 0, 3, len(tape)-spec.context-1], spec)
    assert inputs[0].tolist() == [spec.vocabulary]+tape[:spec.context-1].tolist()
    for row, start in enumerate((-1, 0, 3, len(tape)-spec.context-1)):
        assert targets[row].tolist() == tape[start+1:start+spec.context+1].tolist()
    adapter = model(inputs)
    upstream, _ = model.model(inputs, targets)
    torch.testing.assert_close(adapter, upstream[..., :spec.vocabulary], atol=1e-12, rtol=1e-12)
    own_loss = model.training_loss(inputs, targets)
    own_loss.backward()
    own_gradients = tuple(p.grad.clone() for p in model.parameters())
    model.zero_grad(set_to_none=True)
    upstream, _ = model.model(inputs, targets)
    expected_loss = F.cross_entropy(upstream[..., :spec.vocabulary].reshape(-1, spec.vocabulary), targets.reshape(-1))
    expected_loss.backward()
    torch.testing.assert_close(own_loss, expected_loss, atol=1e-12, rtol=1e-12)
    for expected, parameter in zip(own_gradients, model.parameters()):
        torch.testing.assert_close(expected, parameter.grad, atol=1e-12, rtol=1e-12)
    assert model.model.transformer.wte.weight.grad[spec.vocabulary].abs().sum() > 0
    # The upstream V+1-way CE is different: the extra row must never be a label.
    unmasked = F.cross_entropy(upstream.reshape(-1, spec.vocabulary+1), targets.reshape(-1))
    assert unmasked > expected_loss

    model.eval()
    causal_prefixes = 0
    for length in range(1, spec.context+1):
        first = inputs[1:2, :length].clone()
        for cut in range(length):
            altered = first.clone()
            altered[:, cut+1:] = (altered[:, cut+1:]+1) % spec.vocabulary
            torch.testing.assert_close(model(first)[:, :cut+1], model(altered)[:, :cut+1], atol=1e-12, rtol=1e-12)
            causal_prefixes += 1

    class PastOnly:
        def __init__(self, values, position):
            self.values, self.position = values, position
        def __len__(self):
            return len(self.values)
        def __getitem__(self, key):
            assert isinstance(key, slice) and key.step is None
            assert 0 <= key.start <= key.stop <= self.position
            return self.values[key]

    reference = []
    for t in range(len(tape)):
        [(positions, x)] = list(reporting_inputs(PastOnly(tape, t), [t], spec))
        expected = tape[max(0, t-spec.context):t].tolist() if t else [spec.vocabulary]
        assert x.tolist() == [expected] and positions == (t,)
        changed = tape.copy()
        changed[t:] = (changed[t:]+1) % spec.vocabulary
        [(other_positions, other)] = list(reporting_inputs(changed, [t], spec))
        assert other_positions == positions and torch.equal(x, other)
        logits = model(x, last_only=True)
        reference.append(float(normalized_nll(logits, torch.tensor([int(tape[t])])).detach()))
    # EOT=4 is treated as an ordinary token, including repeated EOT; no reset.
    [(positions, after_eot)] = list(reporting_inputs(tape, [15], spec))
    assert after_eot.tolist() == [tape[7:15].tolist()]
    # A new tape view starts empty; no training-tail context can enter this API.
    [(positions, first)] = list(reporting_inputs(tape[7:], [0], spec))
    assert first.tolist() == [[spec.vocabulary]]
    frozen = {key: value.clone() for key, value in model.state_dict().items()}
    for batch_size in (1, 3, 8, 32):
        result = report(model, tape, batch_size=batch_size)
        assert result['tokens'] == len(tape)
        assert result['full_context_tokens'] == len(tape)-spec.context
        assert abs(result['mean_nll_nats']-sum(reference)/len(reference)) < 1e-12
        assert all(torch.equal(value, model.state_dict()[key]) for key, value in frozen.items())

    optimizer = model.optimizer(learning_rate=0.003, weight_decay=0.1, betas=(0.9, 0.95))
    model.train()
    optimizer.zero_grad(set_to_none=True)
    model.training_loss(inputs, targets).backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    assert isinstance(optimizer, torch.optim.AdamW)
    assert any(not torch.equal(value, model.state_dict()[key]) for key, value in frozen.items())
    assert optimizer.state and all(int(value['step']) == 1 for value in optimizer.state.values())

    full_spec = Spec(vocabulary=50257, context=4, layers=1, heads=1, width=8, dropout=0., bias=True)
    full = Transformer(full_spec, seed=481).double().eval()
    full_tape = np.asarray([0, 50256, 234, 50255, 1, 50256, 50256], dtype=np.uint16)
    full_rows = 0
    with torch.no_grad():
        for ids, x in reporting_inputs(full_tape, range(len(full_tape)), full_spec):
            logits = full(x, last_only=True)
            assert logits.shape == (len(ids), 50257)
            loss = normalized_nll(logits, torch.tensor([int(full_tape[t]) for t in ids]))
            all_losses = torch.logsumexp(logits, dim=-1, keepdim=True)-logits
            torch.testing.assert_close(torch.exp(-all_losses).sum(-1), torch.ones(len(ids), dtype=torch.float64), atol=1e-12, rtol=0)
            for row, t in enumerate(ids):
                torch.testing.assert_close(loss[row], all_losses[row, int(full_tape[t])], atol=1e-12, rtol=0)
            full_rows += len(ids)

    refused = 0
    for starts in ([], [-2], [True], [len(tape)-spec.context]):
        try:
            training_batch(tape, starts, spec)
        except ValueError:
            refused += 1
        else:
            raise AssertionError('invalid block accepted')
    try:
        list(reporting_inputs(np.asarray([spec.vocabulary, 1]), [1], spec))
    except ValueError:
        refused += 1
    else:
        raise AssertionError('input-only PAD accepted as corpus token')
    assert not torch.cuda.is_initialized()
    evidence = dict(status='PASS_CPU_TRANSFORMER_COMPARISON_CONTROL',
        upstream_commit='3adf61e154c3fe3fca428ad6bc3818b27a3b8291',
        scope='fresh standard architecture, training/report contexts and full-alphabet losses; no corpus score, chosen model budget or GPU result',
        shifted_training_blocks=4, upstream_logits_and_all_parameter_gradients_match=True,
        input_only_pad_trains_without_output_mass=True, causal_attention_prefixes=causal_prefixes,
        past_only_report_windows=len(tape), report_batch_sizes=[1, 3, 8, 32],
        reporting_parameters_unchanged=True, ordinary_adamw_update_checked=True,
        full_vocabulary=50257, full_vocabulary_normalized_rows=full_rows,
        malformed_inputs_refused=refused, numerical_control_dtype='float64',
        corpus_bytes_read=0, cuda_initialized=False,
        strongest_baseline_or_language_quality_claim=False)
    if args.write:
        (ROOT/'evidence/minimal/FP_TEXT_TRANSFORMER_BASELINE_CPU.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
