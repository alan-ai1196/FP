"""Prospective gain of a learned delayed bit on a contiguous full-vocabulary stream."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import prod
from pathlib import Path
import argparse
import json

from partitions import (attributions, entropy, fit_sparse_trigram, grouped_counts, price,
                        two_successor_cut)
from text import FIT, SCALE, TAU, VOCAB, Rows, git_json, log_bounds, outward, ratio_log, tape
from text_memory import CAL, GRID, fitted_masses, frequency_mask, quantize

BOUNDARY = FIT + 2*CAL
EXTENDED_HASH = "85c0816d0b46861c606e88361461c13c4782a8da5e5aeb58989d4b895779b59e"
LAMBDAS = (F(1,32), F(1,8), F(1,2), F(2))


@lru_cache(maxsize=65536)
def cell_entropy(n, hits):
    return entropy(n, hits)


def exact_reduction(changes):
    coefficients = Counter()
    for before, after in changes:
        for sign, group in ((1,before),(-1,after)):
            for n,h in group:
                for term,k in ((1,n),(-1,h),(-1,n-h)):
                    if k > 1:
                        coefficients[k] += sign*term*k
    positive = prod(k**c for k,c in coefficients.items() if c > 0)
    negative = prod(k**(-c) for k,c in coefficients.items() if c < 0)
    return positive > negative


def reduced(changes):
    low = high = 0
    terms = 0
    for before, after in changes:
        if before == after or before == after[::-1]:
            continue
        for sign, cells in ((1,before),(-1,after)):
            for cell in cells:
                l,h = cell_entropy(*cell)
                low += l if sign == 1 else -h
                high += h if sign == 1 else -l
                terms += 1
    if low > 0 or high <= 0:
        return low > 0, terms, False
    return exact_reduction(changes), terms, True


def exchange(by_word, vocab):
    side = bytearray(vocab)
    totals = defaultdict(lambda: [(0,0),(0,0)])
    for records in by_word.values():
        for x,(n,h) in records.items():
            a,b = totals[x][0]
            totals[x][0] = (a+n,b+h)
    records_seen = terms = exact = 0
    accepted = []
    order = sorted(by_word)
    for ids in (order,reversed(order)):
        flips = 0
        for word in ids:
            src = side[word]
            changes = []
            for x,(n,h) in by_word[word].items():
                a,b = totals[x][src]
                c,d = totals[x][1-src]
                changes.append((((a,b),(c,d)),((a-n,b-h),(c+n,d+h))))
            improve, scanned, fallback = reduced(changes)
            terms += scanned
            records_seen += len(changes)
            exact += fallback
            if improve:
                side[word] = 1-src
                flips += 1
                for x,(_,after) in zip(by_word[word],changes,strict=True):
                    totals[x][src],totals[x][1-src] = after
        accepted.append(flips)
    return side, dict(occupied_past_ids=len(order), context_records_scanned=records_seen,
                      entropy_terms=terms, exact_sign_comparisons=exact, accepted_flips=accepted)


def acquire(tokens, output):
    by_word = defaultdict(lambda: defaultdict(lambda: [0,0]))
    for i in range(2,len(tokens)):
        cell = by_word[tokens[i-2]][tokens[i-1]]
        cell[0] += 1
        cell[1] += output[tokens[i]]
    return exchange(by_word,len(output))


def signed(value, upper=False, digits=9):
    scaled = value * 10**digits
    k = -((-scaled.numerator)//scaled.denominator) if upper else scaled.numerator//scaled.denominator
    unit = 10**digits
    return f"{'-' if k < 0 else ''}{abs(k)//unit}.{abs(k)%unit:0{digits}d}"


@dataclass
class Model:
    output: str
    base: list
    input_map: object
    installed: dict
    bits: int

    def forecast(self, x, delayed):
        return self.installed.get((x,delayed),self.base[x])


def fit_bit(train, inputs, output, base, group):
    a = grouped_counts(train,FIT,FIT+CAL,inputs,output)
    b = grouped_counts(train,FIT+CAL,BOUNDARY,inputs,output)
    rates = {key:quantize(bins[1]*GRID+TAU*base[key[0]],(sum(bins)+TAU)*GRID) for key,bins in a.items()}
    setup = 1 + (len(inputs) if inputs != output else 0)
    chosen = price(b,base,rates,setup)
    installed = {(x,bit):rates.get((x,bit),base[x]) for x in chosen for bit in (0,1)}
    bits = 40*len(chosen) + (setup if chosen else 0)
    return Model(group,base,inputs,installed,bits), dict(rows=len(chosen), bits=bits,
                 cal_cells=len(a), gate_cells=len(b), setup_bits=setup if chosen else 0)


def gain_certificate(hist, normalizer, incremental_bits):
    low = high = square_upper = 0
    observed = 0
    for (p,q),bins in hist.items():
        n = sum(bins)
        observed += n
        if p == q:
            continue
        for num,den,count in ((p,q,bins[1]),(GRID-p,GRID-q,bins[0])):
            l,h = ratio_log(num,den)
            low += count*l
            high += count*h
        l,h = ratio_log(p*(GRID-q),q*(GRID-p))
        square_upper += n * max(abs(l),abs(h))**2
    charge_l, charge_h = log_bounds(2)
    charge = F(incremental_bits*(charge_h if incremental_bits >= 0 else charge_l),256*SCALE)
    penalties = [lam*F(square_upper,8*SCALE**2) + F(log_bounds(480)[1],SCALE)/lam for lam in LAMBDAS]
    index = min(range(len(LAMBDAS)),key=penalties.__getitem__)
    lower = F(low,SCALE) - penalties[index] - charge
    return dict(eligible_targets=observed, incremental_bits=incremental_bits,
                raw_gain_per_target=[signed(F(low,SCALE*normalizer)),signed(F(high,SCALE*normalizer),True)],
                width_squared_sum_upper=signed(F(square_upper,SCALE**2),True,6),
                best_lambda=str(LAMBDAS[index]), net_conditional_lower_per_target=signed(lower/normalizer),
                net_conditional_lower_total_nats=signed(lower,digits=6), positive=lower>0)


def score(data, start, masks, group_nums, rows, models, eligible):
    n = len(data)-start
    comparisons = (("exchange","frequency_overwrite"),("exchange","raw_frequency"),("exchange","frequency"),
                   ("forward","forward_overwrite"),("forward","raw_forward"),("forward","forward_overwrite"))
    joint = [defaultdict(lambda:[0,0]) for _ in comparisons]
    totals = {name: Counter() for name in models}
    delays = {k: m.input_map[data[start-2]] if m.input_map is not None else 0 for k,m in models.items()}
    eligible_types = set()
    eligible_seen = unseen_successors = 0
    for i in range(start,len(data)):
        x = data[i-1]
        predictions = {k:m.forecast(x,delays[k]) for k,m in models.items()}
        for k,m in models.items():
            if m.input_map is not None:
                delays[k] = m.input_map[x]
        y = data[i]
        if x in eligible:
            eligible_seen += 1
            eligible_types.add(x)
            unseen_successors += y not in eligible[x]
        for k,m in models.items():
            p = predictions[k]
            totals[k][p if masks[m.output][y] else GRID-p] += 1
        for j,(first,second) in enumerate(comparisons):
            if j==5 and x not in eligible:
                continue
            assert models[first].output==models[second].output
            joint[j][predictions[first],predictions[second]][masks[models[first].output][y]] += 1
    pairs = Counter(zip(data[start-1:-1],data[start:],strict=True))
    within = {k:attributions(mask,rows,group_nums[k],pairs)[0] for k,mask in masks.items()}
    scores = {}
    for k,m in models.items():
        lo,hi = within[m.output]
        for mass,count in totals[k].items():
            l,h = ratio_log(GRID,mass)
            lo += count*l
            hi += count*h
        scores[k] = outward((lo,hi),n)
    lo=hi=0
    for (x,y),count in pairs.items():
        num,den = rows.mass(x,y,True)
        l,h = ratio_log(den,num)
        lo += count*l
        hi += count*h
    scores["full_successor"]=outward((lo,hi),n)
    certificates = {}
    for j,(a,b) in enumerate(comparisons):
        bits = models[a].bits-models[b].bits if j!=5 else 0
        name = a+"_vs_"+b+("_eligible" if j==5 else "")
        certificates[name] = gain_certificate(joint[j],n,bits)
        if j!=5:
            gain_lo,gain_hi = map(F,certificates[name]["raw_gain_per_target"])
            assert F(scores[b][0])-F(scores[a][1]) <= gain_hi
            assert F(scores[b][1])-F(scores[a][0]) >= gain_lo
    return dict(targets=n, scores=scores, certificates=certificates,
                forward_eligible_targets=eligible_seen, forward_eligible_types=len(eligible_types),
                forward_unseen_successors=unseen_successors,
                registered_success=all(certificates[a+"_vs_"+b]["positive"] for a,b in comparisons[:3]))


def original(directory):
    journal=git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    reference=next(e for e in journal["results"] if e["case"]=="ngram")
    assert reference["accepted_execution"]
    source=dict(reference["result"]["train_source"],bytes_read=2*(BOUNDARY+CAL),prefix_sha256=EXTENDED_HASH)
    data=tape(source,directory)
    train=data[:BOUNDARY]
    fit=train[:FIT]
    rows=Rows(fit,VOCAB,TAU)
    frequency=frequency_mask(rows)
    forward,eligible,graph=two_successor_cut(fit,frequency,rows)
    learned,search=acquire(fit,frequency)
    masks=dict(frequency=frequency,forward=forward)
    models={}
    work={}
    numerators={}
    for group,output in masks.items():
        _,num,base,_ = fitted_masses(rows,train[FIT:FIT+CAL],train[FIT-1],output)
        numerators[group]=num
        models[group+"_overwrite"]=Model(group,base,None,{},0)
        name="exchange" if group=="frequency" else "forward"
        inputs=learned if group=="frequency" else frequency
        candidate,stats=fit_bit(train,inputs,output,base,group)
        models[name],work[name]=candidate,stats
        table,raw=fit_sparse_trigram(train,output,base,candidate.bits)
        models["raw_"+group]=Model(group,base,range(VOCAB),table,raw["installed_bits"])
        work["raw_"+group]=raw
        if group=="frequency":
            models[group],work[group]=fit_bit(train,frequency,output,base,group)
    return dict(registration="8b20275",prefix_sha256=EXTENDED_HASH,scored_indices=[BOUNDARY,len(data)],
                exact_old_graph=graph, exchange_search=search, fit_targets=FIT-2, positive_input_ids=sum(learned),
                fit_resources=work, continuation=score(data,BOUNDARY,masks,numerators,rows,models,eligible))

def small_checks():
    from partitions import weight
    cases=0
    for values in product(range(2),repeat=7):
        def likelihood(mask):
            cells=defaultdict(lambda:[0,0])
            for w,x,y in zip(values[:-2],values[1:-1],values[2:],strict=True):
                c=cells[x,mask[w]]
                c[0]+=1
                c[1]+=y
            return prod(weight(n,h) for n,h in cells.values())
        expected=[0,0]
        for ids in (range(2),reversed(range(2))):
            for word in ids:
                revised=list(expected)
                revised[word]=1-revised[word]
                if likelihood(revised) > likelihood(expected):
                    expected=revised
        actual,_=acquire(values,[0,1])
        assert list(actual)==expected
        cases+=1
    words=(1,0,0,1)
    observed=grouped_counts(words,2,4,[0,1],[0,1])
    assert dict(observed)=={(0,1):[1,0],(0,0):[0,1]}
    assert F(2,3)*F(4,3)==F(8,9)
    # Under fair independent outcomes, log(3) and -log(3) each have probability 1/2.
    # Count all first crossings up to 128 events using the exact binomial path multiplicities.
    paths={0:1}
    crossed=0
    horizon=128
    for t in range(1,horizon+1):
        new=Counter()
        for previous,multiplicity in paths.items():
            new[previous]+=multiplicity
            new[previous+1]+=multiplicity
        paths={}
        for ones,ways in new.items():
            report=gain_certificate({(3*GRID//4,GRID//4):(t-ones,ones)},t,0)
            if report["positive"]:
                crossed += ways*2**(horizon-t)
            else:
                paths[ones]=ways
    assert crossed+sum(paths.values())==2**horizon
    risk=F(crossed,2**horizon)
    assert 0 < risk <= F(1,120)
    return dict(exchange_trajectories=cases, fitting_word="1001", true_two_step_gain_product="8/9",
                null_crossing_horizon=horizon,null_crossing_probability=str(risk))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text",action="store_true")
    parser.add_argument("--data-dir",type=Path)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result={"controls":small_checks()}
    if args.text:
        result["original_text"]=original(args.data_dir)
    if args.check:
        expected=json.loads(Path(__file__).with_name("transfer_result.json").read_text())
        assert result=={k:expected[k] for k in result}
    print(json.dumps(result,indent=2))
