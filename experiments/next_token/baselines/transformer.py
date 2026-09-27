"""Fresh standard Transformer comparison primitives, outside FP semantics.

No corpus is opened and no model size, training budget or outcome is selected
by this module. The trial must register those coordinates before using it.
"""
from collections import defaultdict
from dataclasses import dataclass
from operator import index
from typing import Sequence
import math

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from .nanogpt.model import GPT, GPTConfig


@dataclass(frozen=True)
class Spec:
    vocabulary: int
    context: int
    layers: int
    heads: int
    width: int
    dropout: float
    bias: bool

    def __post_init__(self):
        for value in (self.vocabulary, self.context, self.layers, self.heads, self.width):
            if type(value) is not int or value < 1:
                raise ValueError('positive integer model dimensions required')
        if self.width % self.heads or not 0 <= self.dropout < 1 or type(self.bias) is not bool:
            raise ValueError('invalid head width, dropout or bias')


class Transformer(nn.Module):
    def __init__(self, spec: Spec, *, seed: int):
        super().__init__()
        self.spec = spec
        # Initialize on CPU without changing the caller's CPU random stream.
        # No CUDA context, pretrained weights or corpus is needed here.
        with torch.random.fork_rng(devices=[]):
            torch.random.default_generator.manual_seed(seed)
            self.model = GPT(GPTConfig(block_size=spec.context, vocab_size=spec.vocabulary+1,
                n_layer=spec.layers, n_head=spec.heads, n_embd=spec.width,
                dropout=spec.dropout, bias=spec.bias))

    def forward(self, inputs, *, last_only=False):
        if inputs.ndim != 2 or not 1 <= inputs.shape[1] <= self.spec.context:
            raise ValueError('nonempty input block within registered context required')
        # The upstream hidden computation, with the input-only PAD row removed
        # from the output projection itself. Every loss uses exactly V logits.
        m = self.model.transformer
        pos = torch.arange(inputs.shape[1], dtype=torch.long, device=inputs.device)
        hidden = m.drop(m.wte(inputs)+m.wpe(pos))
        for block in m.h:
            hidden = block(hidden)
        hidden = m.ln_f(hidden)
        if last_only:
            hidden = hidden[:, -1, :]
        return F.linear(hidden, self.model.lm_head.weight[:self.spec.vocabulary])

    def training_loss(self, inputs, targets):
        if targets.shape != inputs.shape:
            raise ValueError('one next-token target for each input position required')
        logits = self(inputs)
        return F.cross_entropy(logits.reshape(-1, self.spec.vocabulary), targets.reshape(-1))

    def optimizer(self, *, learning_rate, weight_decay, betas):
        # Preserve the upstream ordinary AdamW parameter groups/fused option.
        return self.model.configure_optimizers(weight_decay, learning_rate, betas,
                                                next(self.parameters()).device.type)


def _ids(tape, start, stop, vocabulary):
    values = np.asarray(tape[start:stop])
    if values.ndim != 1 or values.dtype.kind not in 'iu' or np.any(values < 0) or np.any(values >= vocabulary):
        raise ValueError('corpus tokens must be integer IDs in the full target alphabet')
    return values.astype(np.int64, copy=True)


def training_batch(tape: Sequence[int], starts, spec: Spec, *, device='cpu'):
    """Ordinary shifted contiguous blocks; start=-1 includes the empty prefix.

    An entry start=s predicts targets s+1,...,s+L. Their available contexts
    grow across this block; this is explicitly not full-context prequential
    training. The caller samples starts within its preregistered train view.
    """
    xs, ys = [], []
    for value in starts:
        start = index(value)
        if isinstance(value, (bool, np.bool_)) or start < -1 or start+spec.context >= len(tape):
            raise ValueError('training block leaves the declared tape view')
        targets = _ids(tape, start+1, start+spec.context+1, spec.vocabulary)
        inputs = (np.concatenate(([spec.vocabulary], targets[:-1])) if start == -1
                  else _ids(tape, start, start+spec.context, spec.vocabulary))
        xs.append(inputs)
        ys.append(targets)
    if not xs:
        raise ValueError('empty training batch')
    return (torch.tensor(np.stack(xs), dtype=torch.long, device=device),
            torch.tensor(np.stack(ys), dtype=torch.long, device=device))


def reporting_inputs(tape: Sequence[int], positions, spec: Spec, *, device='cpu'):
    """Group past-only windows by length; never access a target or later token."""
    groups = defaultdict(list)
    for value in positions:
        position = index(value)
        if isinstance(value, (bool, np.bool_)) or not 0 <= position < len(tape):
            raise ValueError('reporting position outside tape')
        past = (_ids(tape, max(0, position-spec.context), position, spec.vocabulary)
                if position else np.asarray([spec.vocabulary], dtype=np.int64))
        groups[len(past)].append((position, past))
    for entries in groups.values():
        positions, inputs = zip(*entries)
        yield positions, torch.tensor(np.stack(inputs), dtype=torch.long, device=device)


def normalized_nll(logits, targets):
    """Float64 proper softmax loss of the actual logits, over all V categories."""
    if logits.ndim != 2 or targets.shape != logits.shape[:1] or not torch.isfinite(logits).all():
        raise ValueError('finite complete logits and one target per row required')
    values = logits.double()
    return torch.logsumexp(values, dim=-1)-values.gather(1, targets[:, None]).squeeze(1)


@torch.no_grad()
def report(model: Transformer, tape: Sequence[int], *, batch_size: int):
    """Score every token of one supplied report view with rolling past context.

    No optimizer call or parameter mutation. The trial owns file identities,
    split/tuning policy and resource limits; this is not an FP Runtime port.
    """
    if type(batch_size) is not int or batch_size < 1 or len(tape) == 0:
        raise ValueError('nonempty reporting tape and positive batch size required')
    model.eval()
    spec, device = model.spec, next(model.parameters()).device
    totals, count = [], 0
    for start in range(0, len(tape), batch_size):
        positions = range(start, min(start+batch_size, len(tape)))
        for ids, inputs in reporting_inputs(tape, positions, spec, device=device):
            logits = model(inputs, last_only=True)
            # Targets are looked up only after their past-only forecasts exist.
            targets = torch.tensor([index(tape[t]) for t in ids], dtype=torch.long, device=device)
            if torch.any(targets < 0) or torch.any(targets >= spec.vocabulary):
                raise ValueError('report target outside alphabet')
            losses = normalized_nll(logits, targets)
            totals.append(math.fsum(losses.cpu().tolist()))
            count += len(ids)
    return dict(tokens=count, mean_nll_nats=math.fsum(totals)/count,
                vocabulary=spec.vocabulary, context=spec.context,
                full_context_tokens=max(0, count-spec.context),
                reporting_mode='frozen rolling context; actual logits normalized in float64')
