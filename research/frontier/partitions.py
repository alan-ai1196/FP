"""Learn a binary output partition from ordinary counts and price its use as history."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cmp_to_key
from itertools import combinations, product
from math import prod
from pathlib import Path
import argparse
import json

from text import FIT, SCALE, TAU, VOCAB, Rows, load_prefixes, log_bounds, outward, ratio_log
from text_memory import CAL, GRID, entropy_bound, fitted_masses, frequency_mask, quantize


def entropy(n, hits):
    lo = hi = 0
    for k in (hits, n-hits):
        if k:
            l, h = ratio_log(n,k)
            lo += k*l
            hi += k*h
    return lo, hi


def weight(n, hits):
    return F(hits**hits*(n-hits)**(n-hits), n**n)


def learn_partition(vocab, counts):
    """An output with no evidence gets the pooled posterior. A constant optimum needs no split."""
    by_rate = defaultdict(list)
    total = positive = 0
    for token,(n,h) in counts.items():
        if n:
            by_rate[F(h,n)].append((token,n,h))
            total += n
            positive += h
    rates = sorted(by_rate)
    if len(rates) < 2:
        return bytearray(vocab), dict(posterior_values=len(rates), boundaries=0, exact_ties=0)
    n = h = exact = 0
    best = best_bounds = threshold = None
    for i,rate in enumerate(rates[:-1]):
        for _,cells,ones in by_rate[rate]:
            n += cells
            h += ones
        bounds = tuple(a+b for a,b in zip(entropy(n,h), entropy(total-n,positive-h), strict=True))
        take = best is None or bounds[1] < best_bounds[0]
        if best is not None and not take and bounds[0] <= best_bounds[1]:
            exact += 1
            bn,bh = best
            take = weight(n,h)*weight(total-n,positive-h) > weight(bn,bh)*weight(total-bn,positive-bh)
        if take:
            best, best_bounds, threshold = (n,h), bounds, rates[i+1]
    default = int(F(positive,total) >= threshold)
    mask = bytearray([default])*vocab
    for rate,entries in by_rate.items():
        for token,_,_ in entries:
            mask[token] = rate >= threshold
    return mask, dict(posterior_values=len(rates), boundaries=len(rates)-1, exact_ties=exact,
                      threshold=str(threshold), unseen_group=default)


def grouped_counts(tokens, start, stop, past, output):
    hist = defaultdict(lambda: [0,0])
    for t in range(start, stop):
        hist[tokens[t-1],past[tokens[t-2]]][output[tokens[t]]] += 1
    return hist


def gain(factors):
    lo = hi = 0
    for num,den,n in factors:
        l, h = ratio_log(num,den)
        lo += n*l
        hi += n*h
    return lo, hi


def net_positive(bounds, bits, factors):
    l,h = log_bounds(2)
    if 256*bounds[0] > bits*h:
        return True
    if 256*bounds[1] <= bits*l:
        return False
    odds = prod(F(num,den)**n for num,den,n in factors)
    return odds**256 > 2**bits


def price(gate, base, conditional):
    by_token = defaultdict(list)
    for (x,b),bins in gate.items():
        p = conditional.get((x,b), base[x])
        if p != base[x]:
            for y,n in enumerate(bins):
                if n:
                    num, den = (p,base[x]) if y else (GRID-p,GRID-base[x])
                    by_token[x].append((num,den,n))
    selected = set()
    lo = hi = 0
    for x,factors in by_token.items():
        bounds = gain(factors)
        if net_positive(bounds,40,factors):
            selected.add(x)
            lo += bounds[0]
            hi += bounds[1]
    factors = (v for x in selected for v in by_token[x])
    return selected if selected and net_positive((lo,hi),40*len(selected)+1,factors) else set()


def permutation_gain(report, selected, base, trained):
    lo = hi = 0
    for x in selected:
        n00,n01 = report.get((x,0),(0,0))
        n10,n11 = report.get((x,1),(0,0))
        covariance = n00*n11 - n01*n10
        if not covariance:
            continue
        p0 = trained.get((x,0),base[x])
        p1 = trained.get((x,1),base[x])
        l,h = ratio_log(p1*(GRID-p0),p0*(GRID-p1))
        products = (covariance*l,covariance*h)
        n = n00+n01+n10+n11
        lo += min(products)//n
        hi += -((-max(products))//n)
    den = SCALE*sum(sum(c) for c in report.values())
    return [lo*10**9//den,-((-hi*10**9)//den)]


def fitted_arm(cal, gate, tape, past, output, base, within):
    report = grouped_counts(tape,4096,len(tape),past,output)
    trained = {k: quantize(v[1]*GRID + TAU*base[k[0]], (sum(v)+TAU)*GRID) for k,v in cal.items()}
    rows = price(gate, base, trained)
    totals = [list(within),list(within)]
    used = set()
    observed = set(report)
    expected_masses = Counter()
    for (x,b), bins in report.items():
        p = trained.get((x,b), base[x]) if x in rows else base[x]
        if (x,1-b) in observed and x in rows and p != trained.get((x,1-b),base[x]):
            used.add(x)
        for idx,rate in enumerate((base[x],p)):
            for y,n in enumerate(bins):
                if n:
                    l,h = ratio_log(GRID,rate if y else GRID-rate)
                    totals[idx][0] += n*l
                    totals[idx][1] += n*h
                    if idx == 1:
                        expected_masses[rate if y else GRID-rate] += n
    # Independent streaming execution has just the previous membership bit when x arrives.
    stream_masses = Counter()
    delayed = past[tape[0]]
    for i in range(1,len(tape)-1):
        x = tape[i]
        p = trained.get((x,delayed),base[x]) if x in rows else base[x]
        delayed = past[x]
        if i+1 >= 4096:
            stream_masses[p if output[tape[i+1]] else GRID-p] += 1
    assert stream_masses == expected_masses
    n = sum(sum(bins) for bins in report.values())
    return dict(calibration_cells=len(cal), gate_cells=len(gate), installed_rows=len(rows),
                extra_payload_bits=40*len(rows)+int(bool(rows)), varying_last_tokens=len(used),
                shuffled_minus_observed_nanonats=permutation_gain(report,rows,base,trained),
                overwrite=outward(totals[0],n), conditional=outward(totals[1],n))


def attributions(mask, rows, numerator, pairs):
    inside = [0,0]
    hist = defaultdict(lambda:[0,0])
    for (x,y),n in pairs.items():
        num,den = rows.mass(x,y,True)
        group = mask[y]
        mass = numerator[x] if group else den-numerator[x]
        low,high = ratio_log(mass,num)
        inside[0] += n*low
        inside[1] += n*high
        hist[x][group] += n
    lo,hi = entropy_bound(hist)
    return inside,(inside[0]+lo,inside[1]+hi)


def sparse_trigram(train, val, output, base, within, bit_budget):
    """A full pair of token IDs can buy a distinct group rate under the same extra payload."""
    raw_id = range(len(output))
    boundary = FIT+CAL
    cal = grouped_counts(train,FIT,boundary,raw_id,output)
    gate = grouped_counts(train,boundary,len(train),raw_id,output)
    report = grouped_counts(val,4096,len(val),raw_id,output)
    candidates = {}
    fitted = {}
    for key,(zeros,ones) in cal.items():
        x,_ = key
        if key not in gate:
            continue
        p = quantize(ones*GRID + TAU*base[x],(zeros+ones+TAU)*GRID)
        factors = [(num,den,n) for num,den,n in
                   ((GRID-p,GRID-base[x],gate[key][0]),(p,base[x],gate[key][1])) if n]
        bounds = gain(factors)
        if net_positive(bounds,44,factors):
            candidates[key] = (bounds,factors)
            fitted[key] = p
    def compare(a,b):
        (al,ah), af = candidates[a]
        (bl,bh), bf = candidates[b]
        if al > bh:
            return -1
        if bl > ah:
            return 1
        odds_a = prod(F(n,d)**c for n,d,c in af)
        odds_b = prod(F(n,d)**c for n,d,c in bf)
        if odds_a != odds_b:
            return -1 if odds_a > odds_b else 1
        return (a > b)-(a < b)
    maximum = max(0,(bit_budget-16)//44)
    chosen = set(sorted(candidates,key=cmp_to_key(compare))[:maximum])
    bounds = tuple(sum(candidates[k][0][i] for k in chosen) for i in range(2))
    if not net_positive(bounds,44*len(chosen)+16,(v for k in chosen for v in candidates[k][1])):
        chosen.clear()
    lo,hi = within
    for key,(zeros,ones) in report.items():
        p = fitted[key] if key in chosen else base[key[0]]
        for num,n in ((GRID-p,zeros),(p,ones)):
            if n:
                l,h = ratio_log(GRID,num)
                lo += n*l
                hi += n*h
    return dict(available_bits=bit_budget, cells=len(chosen), installed_bits=44*len(chosen)+16*bool(chosen),
                calibration_cells=len(cal), gate_cells=len(gate),
                nll=outward((lo,hi),sum(sum(v) for v in report.values())))


def greedy_cut(vocab, edges):
    previous = defaultdict(list)
    for (a,b), weight_lower in edges.items():
        left,right = sorted((a,b))
        previous[right].append((left,weight_lower))
    side = bytearray(vocab)
    for vertex in range(vocab):
        same = [0,0]
        for other,weight_lower in previous.get(vertex,()):
            same[side[other]] += weight_lower
        side[vertex] = same[0] > same[1]
    return side


def two_successors(tokens, past, rows):
    contexts = defaultdict(lambda: defaultdict(lambda: [0,0]))
    for t in range(2,len(tokens)):
        x = tokens[t-1]
        if rows.degrees[x] == 2:
            cell = contexts[x][tokens[t]]
            cell[0] += 1
            cell[1] += past[tokens[t-2]]
    edges = defaultdict(lambda: [0,0])
    used = events = 0
    for cells in contexts.values():
        if len(cells) != 2:
            continue
        a,b = sorted(cells)
        n,h = cells[a]
        m,k = cells[b]
        before = entropy(n+m,h+k)
        first, second = entropy(n,h), entropy(m,k)
        bounds = edges[a,b]
        bounds[0] += max(0,before[0]-first[1]-second[1])
        bounds[1] += max(0,before[1]-first[0]-second[0])
        events += n+m
        used += 1
    side = greedy_cut(rows.vocab,{e:value[0] for e,value in edges.items()})
    total = [sum(v[i] for v in edges.values()) for i in range(2)]
    cut = [sum(v[i] for (a,b),v in edges.items() if side[a]!=side[b]) for i in range(2)]
    assert 2*cut[0] >= total[0]
    return dict(contexts=used, observations=events, token_pairs=len(edges),
                total_distinguishable_nats=outward(total,1), greedy_retained_nats=outward(cut,1))


def small_checks():
    tests = 0
    for hits in product(range(4),repeat=4):
        counts = {i:(3,h) for i,h in enumerate(hits)}
        learned,_ = learn_partition(5,counts)
        def objective(mask):
            value=F(1)
            for g in (0,1):
                positive = sum(h for i,h in enumerate(hits) if mask[i]==g)
                size = 3*sum(1 for i in range(4) if mask[i]==g)
                value *= weight(size,positive)
            return value
        assert objective(learned)==max(objective(m) for m in product((0,1),repeat=4))
        tests+=1
    contexts = (((3,0),(2,2),(1,0)), ((1,1),(2,0),(3,3)))
    def conditional_quality(mask):
        result=F(1)
        for cells in contexts:
            for g in (0,1):
                group=[v for i,v in enumerate(cells) if mask[i]==g]
                result*=weight(sum(n for n,_ in group),sum(h for _,h in group))
        return result
    assert conditional_quality((0,1,0))==1 > max(conditional_quality((0,1,1)),conditional_quality((0,0,1)))
    all_edges = list(combinations(range(4),2))
    graphs = 0
    for weights in product(range(3),repeat=6):
        edges = dict(zip(all_edges,weights,strict=True))
        side = greedy_cut(4,edges)
        def cut(bits):
            return sum(w for (a,b),w in edges.items() if bits[a]!=bits[b])
        def empirical_weight(bits):
            # Each edge context has w labels of each kind, one kind at each endpoint.
            return prod(weight(2*w,w) for (a,b),w in edges.items() if bits[a]==bits[b])
        masks = list(product((0,1),repeat=4))
        assert all(empirical_weight(b) == F(1,4**(sum(weights)-cut(b))) for b in masks)
        assert 2*cut(side) >= sum(weights) >= max(map(cut,masks))
        graphs += 1
    # Direct likelihood times deployment price tests coupled rent and tie handling.
    base=[1024,2048]
    alternatives={(0,0):1100,(0,1):1023,(1,0):1400,(1,1):2100}
    for a,b in product(range(4),repeat=2):
        gate={(0,0):(a,b),(1,1):(b,a)}
        chosen=price(gate,base,alternatives)
        def objective(selected):
            odds=F(1)
            for (x,bit),bins in gate.items():
                if x in selected:
                    p=alternatives[x,bit]
                    odds*=F(GRID-p,GRID-base[x])**bins[0]*F(p,base[x])**bins[1]
            return odds**256/2**(40*len(selected)+int(bool(selected)))
        assert objective(chosen)==max(objective(s) for s in (set(),{0},{1},{0,1}))
    return dict(exhaustive_count_tables=tests, partitions_per_table=16, shared_rent_cases=16,
                weighted_graphs=graphs)


def original(directory):
    train,val,source = load_prefixes(directory)
    rows = Rows(train[:FIT], VOCAB, TAU)
    frequency = frequency_mask(rows)
    evidence = defaultdict(lambda:[0,0])
    for t in range(2,FIT):
        cell=evidence[train[t]]
        cell[0]+=1
        cell[1]+=frequency[train[t-2]]
    learned,search = learn_partition(VOCAB,evidence)
    assert 0 < sum(learned) < VOCAB
    masks={"frequency":frequency,"learned":learned}
    calibration_end=FIT+CAL
    pairs=Counter(zip(val[4095:-1],val[4096:],strict=True))
    n=sum(pairs.values())
    inside_bounds={}
    arms={}
    trigrams={}
    for out_name,output in masks.items():
        _,numerator,base,_=fitted_masses(rows,train[FIT:calibration_end],train[FIT-1],output)
        within, best_static=attributions(output,rows,numerator,pairs)
        inside_bounds[out_name]=dict(oracle=outward(within,n),hindsight_overwrite=outward(best_static,n))
        for in_name,past in masks.items():
            cal=grouped_counts(train,FIT,calibration_end,past,output)
            gate=grouped_counts(train,calibration_end,len(train),past,output)
            arms[in_name+"/"+out_name]=fitted_arm(cal,gate,val,past,output,base,within)
        budget=arms[out_name+"/"+out_name]["extra_payload_bits"]
        trigrams[out_name]=sparse_trigram(train,val,output,base,within,budget)
    raw_lo=raw_hi=0
    for (x,y),count in pairs.items():
        num,den=rows.mass(x,y,True)
        l,h=ratio_log(den,num)
        raw_lo+=count*l
        raw_hi+=count*h
    raw=outward((raw_lo,raw_hi),n)
    candidate=arms["learned/learned"]
    success=all(F(candidate["conditional"][1]) < F(control[0]) for control in
                (candidate["overwrite"],arms["frequency/frequency"]["conditional"],raw))
    return dict(registration="d737b5d", train_sha256=source["train_source"]["prefix_sha256"],
                val_sha256=source["reporting_source"]["prefix_sha256"], fit_pairs=FIT-2,
                observed_target_types=len(evidence), calibration_targets=CAL, gate_targets=CAL,
                report_targets=n, frequency_group_types=sum(frequency), learned_group_types=sum(learned),
                two_successor_fit_diagnostic=two_successors(train[:FIT],frequency,rows),
                partition_search=search, floors=inside_bounds, arms=arms, matched_sparse_trigram=trigrams,
                original_full_bank=raw, registered_success=success)


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
        expected=json.loads(Path(__file__).with_name("partition_result.json").read_text())
        assert result=={k:expected[k] for k in result}
    print(json.dumps(result,indent=2))
