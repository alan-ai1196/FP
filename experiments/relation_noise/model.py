"""RN-1 data laws and exact forest posterior; no Runtime or GPU authority."""
from collections import deque
from fractions import Fraction as F
from itertools import product
from math import comb, log
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from audit_reference_acceleration import context, fixture_parameters
from fp_reference.empirical_bound import empirical_upper
from fp_reference.data_usage import ObservationRecord
from fp_reference.relation_proposal import relation_proposal
from audit_reference_events import forward_oracle


def cases():
    return tuple((n, law, seed) for n in (8, 16) for law in ('conditioned', 'iid')
                 for seed in range(4))+((8, 'disconnected-a', 0), (8, 'disconnected-b', 0))


def data(case):
    n, law, seed = case
    hidden_rng = random.Random(2026091300+100*n+seed)
    hidden = tuple(hidden_rng.randrange(2) for _ in range(n))
    if law == 'disconnected-b':
        hidden = hidden[:n//2]+tuple(1-v for v in hidden[n//2:])
    edges = tuple((i, i+1) for i in range(n-1) if not law.startswith('disconnected') or i != n//2-1)
    noise = random.Random(2026091400+100*n+seed)
    train = []
    for i, j in edges:
        flips = tuple(noise.randrange(10) == 0 for _ in range(10)) if law == 'iid' else None
        at = None if flips else noise.randrange(10)
        for k in range(10):
            train.append((i, j, (hidden[i]^hidden[j]) ^ (int(flips[k]) if flips else int(k == at))))
    pairs = list(product(range(n), repeat=2))
    random.Random(2026091600+100*n+seed).shuffle(pairs)
    noise = random.Random(2026091500+100*n+seed)
    evaluation = tuple((i, j, (hidden[i]^hidden[j]) ^ int(noise.randrange(10) == 0)) for i, j in pairs)
    return hidden, edges, tuple(train), evaluation


def counts_from_training(n, training):
    counts = {}
    for i, j, label in training:
        assert 0 <= i < n and 0 <= j < n and i != j and label in (0, 1)
        counts.setdefault(tuple(sorted((i, j))), [0, 0])[label] += 1
    return tuple((i, j, *row) for (i, j), row in sorted(counts.items()))


def posterior(n, counts, law):
    adjacent = [[] for _ in range(n)]
    for i, j, c0, c1 in counts:
        if law == 'iid':
            a, b = 9**c0, 9**c1
            correlation = F(a-b, a+b)
        else:
            assert sorted((c0, c1)) == [1, 9]
            correlation = F(1 if c0 > c1 else -1)
        adjacent[i].append((j, correlation))
        adjacent[j].append((i, correlation))
    predictions = {}
    for root in range(n):
        seen, queue = {root: F(1)}, deque([(root, None)])
        while queue:
            vertex, parent = queue.popleft()
            for other, edge in adjacent[vertex]:
                if other == parent:
                    continue
                assert other not in seen, 'the registered posterior is for forests'
                seen[other] = seen[vertex]*edge
                queue.append((other, vertex))
        for other in range(n):
            p1 = (1-F(4, 5)*seen.get(other, F(0)))/2
            predictions[root, other] = (1-p1, p1)
    assert all(sum(row) == 1 and min(row) >= F(1, 10) for row in predictions.values())
    return predictions


def enumerated_posterior(n, counts, law):
    values, total = {(i,j):F(0) for i,j in product(range(n), repeat=2)}, F(0)
    for assignment in product((0, 1), repeat=n):
        weight = F(1)
        for i, j, c0, c1 in counts:
            correct = c1 if assignment[i]^assignment[j] else c0
            if law == 'iid':
                weight *= 9**correct
            else:
                weight *= int(correct == 9 and c0+c1 == 10)
        total += weight
        for i, j in values:
            values[i,j] += weight*(F(9,10) if assignment[i]^assignment[j] else F(1,10))
    assert total > 0
    return {key:(1-value/total,value/total) for key,value in values.items()}


def unseen_pairs(n, edges):
    trained = {tuple(sorted(e)) for e in edges}
    return tuple((i,j) for i,j in product(range(n),repeat=2) if i != j and tuple(sorted((i,j))) not in trained)


def score(predictions, hidden, pairs):
    ce, brier, gap, mistake = 0.0, F(0), F(0), F(0)
    for i,j in pairs:
        truth = hidden[i]^hidden[j]
        q = (F(1,10), F(9,10)) if truth else (F(9,10), F(1,10))
        p = predictions[i,j]
        assert len(p)==2 and min(p)>0 and sum(p)==1
        ce += -sum(float(a)*log(float(b)) for a,b in zip(q,p))
        brier += sum(q[y]*sum((p[k]-int(y==k))**2 for k in (0,1)) for y in (0,1))
        gap += abs(p[truth]-F(9,10))
        mistake += F(1,2) if p[0]==p[1] else F(int((p[1]>p[0]) != bool(truth)))
    return {'contexts': len(pairs), 'expected_CE_binary64': ce/len(pairs),
            'expected_Brier_exact': str(brier/len(pairs)), 'mean_true_probability_gap': str(gap/len(pairs)),
            'latent_relation_error_with_half_ties': str(mistake/len(pairs))}


def exact_audit():
    posterior_cases = 0
    for n, edges in ((3, ((0,1),(1,2))), (4, ((0,1),(2,3)))):
        for counts in product(range(4), repeat=2):
            rows = tuple((i,j,c,3-c) for (i,j),c in zip(edges, counts))
            assert posterior(n, rows, 'iid') == enumerated_posterior(n, rows, 'iid')
            posterior_cases += 1
        for signs in product((0,1),repeat=2):
            rows = tuple((i,j,9-8*s,1+8*s) for (i,j),s in zip(edges,signs))
            assert posterior(n, rows, 'conditioned') == enumerated_posterior(n, rows, 'conditioned')
            posterior_cases += 1
    cfg, run, _, _, _ = fixture_parameters(3)
    gate_cases, eligible = 0, 0
    for c0, c1 in product(range(11),repeat=2):
        records = []
        for i, zeroes in enumerate((c0,c1)):
            source = context(3,i,i+1)
            for k in range(10):
                cursor=len(records)
                records.append(ObservationRecord(f'o{cursor}','train','train',cursor,source,
                    tuple((s.source_id,v) for s,v in zip(cfg.semantics.sources,source)), int(k>=zeroes)))
        upper = empirical_upper(tuple(records),cfg.semantics,bit_limit=32768)
        bound = upper.likelihood == F(1,2)**20
        if not bound:
            proposal = relation_proposal(upper,cfg.semantics,run.searches[0].grammar,
                                        cfg.initializer_pattern,run.searches[0].relation_sources,bit_limit=32768)
            if proposal.program is not None:
                likelihood = F(1)
                for record in records:
                    p,_ = forward_oracle(proposal.program,cfg.semantics,cfg.initializer_pattern,dict(record.sources))
                    likelihood *= p[record.target]
                bound = likelihood == upper.likelihood
        assert bound == (all(c in (1,9) for c in (c0,c1)) or (c0,c1)==(5,5))
        gate_cases += 1
        eligible += bound
    p9 = sum(F(comb(10,k)*9**(10-k),10**10) for k in (1,9))
    p5 = F(comb(10,5)*9**5,10**10)
    correct = sum(F(comb(10,k)*9**(10-k),10**10) for k in range(5))
    a,b = data((8,'disconnected-a',0)), data((8,'disconnected-b',0))
    assert a[1:3] == b[1:3] and a[0] != b[0]
    assert all((a[0][i]^a[0][j]) != (b[0][i]^b[0][j]) for i in range(4) for j in range(4,8))
    return {'enumerated_posterior_cases':posterior_cases, 'two_edge_count_patterns':gate_cases,
            'eligible_patterns':eligible, 'p9':str(p9),'p5':str(p5),
            'IID_arithmetic_gate_eligibility':{str(n):{'exact':str(p9**(n-1)+p5**(n-1)),
                'binary64':float(p9**(n-1)+p5**(n-1))} for n in (8,16,32)},
            'IID_all_strict_majorities_correct':{str(n):float(correct**(n-1)) for n in (8,16,32)},
            'disconnected_training_equality_and_opposite_cross_relations':True}


if __name__ == '__main__':
    import json
    print(json.dumps(exact_audit(), indent=2))
