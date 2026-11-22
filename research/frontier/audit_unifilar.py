"""Test synchronized state discovery against raw next-token and categorical learners."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import product
from math import lcm, prod
from pathlib import Path
from random import Random
import argparse
import json

from text import log_bounds, outward, ratio_log
from unifilar import (Blocks, determinant, discover, emission_counts, exact_closure, moments,
                      ratios, smoothed)

ACTIONS=((0,0),(1,1),(0,1),(1,0))
WEIGHTS=((1,1,5,1),(1,1,1,5))
EMISSIONS=tuple(tuple(F(v,8) for v in row) for row in WEIGHTS)


def categorical(actions):
    return [[[EMISSIONS[i][a] if dest[i]==j else F(0) for j in (0,1)] for i in (0,1)]
            for a,dest in enumerate(actions)]


def stationary(matrices):
    up=sum(m[0][1] for m in matrices)
    down=sum(m[1][0] for m in matrices)
    return (down/(up+down),up/(up+down))


def law(word, initial, matrices):
    row=initial
    for a in word:
        m=matrices[a]
        row=tuple(sum(row[i]*m[i][j] for i in (0,1)) for j in (0,1))
    return sum(row)


def exact_blocks(initial, matrices):
    alphabet=range(len(matrices))
    probability=lambda word: law(word,initial,matrices)
    candidates=[(probability((p,s))-probability((p,))*probability((s,)),p,s)
                for p,s in product(alphabet,repeat=2)]
    best=max(v for v,_,_ in candidates)
    if not best:
        return None
    p,s=min((p,s) for v,p,s in candidates if v==best)
    basis=[[F(1),probability((s,))],[probability((p,)),probability((p,s))]]
    blocks=[[[probability((a,)),probability((a,s))],
             [probability((p,a)),probability((p,a,s))]] for a in alphabet]
    return Blocks((p,s),basis,blocks,probability((s,)))


def balanced_tape(initial, matrices):
    triples={w:law(w,initial,matrices) for w in product(range(len(matrices)),repeat=3)}
    length=lcm(*(p.denominator for p in triples.values()))
    outgoing=defaultdict(list)
    for (a,b,c),p in triples.items():
        outgoing[a,b].extend([(b,c)]*int(length*p))
    stack=[next(iter(outgoing))]
    reversed_tour=[]
    while stack:
        key=stack[-1]
        if outgoing[key]:
            stack.append(outgoing[key].pop())
        else:
            reversed_tour.append(stack.pop())
    tour=reversed_tour[::-1]
    tape=tuple(tour[0])+tuple(pair[1] for pair in tour[1:])
    assert len(tape)==length+2
    assert Counter(zip(tape[:-2],tape[1:-1],tape[2:],strict=True))=={w:length*p for w,p in triples.items()}
    return tape


def same_law(fitted, actions, emissions, initial):
    if fitted is None:
        return False
    for mapping in ((0,1),(1,0)):
        if fitted["initial_second"] != initial[mapping[1]]:
            continue
        if all(fitted["emissions"][i]==list(emissions[mapping[i]]) for i in (0,1)):
            if all(mapping[op[i]]==actions[a][mapping[i]] for a,op in enumerate(fitted["actions"]) for i in (0,1)):
                return True
    return False


def same_actions(fitted, reference):
    return fitted is not None and any(all(mapping[op[i]]==reference[a][mapping[i]]
                   for a,op in enumerate(fitted) for i in (0,1)) for mapping in ((0,1),(1,0)))


def brier_gap(initial, actions):
    result=F(0)
    for a,dest in enumerate(actions):
        weights=[initial[i]*EMISSIONS[i][a] for i in (0,1)]
        mean=[sum(weights[i]*EMISSIONS[dest[i]][y] for i in (0,1))/sum(weights) for y in range(4)]
        for i,w in enumerate(weights):
            result+=w*sum((p-q)**2 for p,q in zip(EMISSIONS[dest[i]],mean,strict=True))
    return result


def matched_triple_control(initial, matrices):
    """The order-two Markov extension of the stationary pair and triple tables."""
    alphabet = range(len(matrices))
    pairs = {w: law(w, initial, matrices) for w in product(alphabet, repeat=2)}
    triples = {w: law(w, initial, matrices) for w in product(alphabet, repeat=3)}
    kernel = {w: tuple(triples[w+(a,)] / p for a in alphabet) for w,p in pairs.items()}
    assert all(sum(row) == 1 and min(row) > 0 for row in kernel.values())
    for (b,c), p in pairs.items():
        assert sum(pairs[a,b] * kernel[a,b][c] for a in alphabet) == p
    assert all(pairs[a,b] * kernel[a,b][c] == p for (a,b,c),p in triples.items())
    histories = ((0,2,2), (1,2,2))
    truth = [law(w+(2,), initial, matrices) / law(w, initial, matrices) for w in histories]
    other = [kernel[w[-2:]][2] for w in histories]
    assert truth == [F(5,8), F(1,8)] and other == [F(47,76)]*2
    return dict(matched_triples=len(triples), reset_then_two_retains=list(map(str, truth)),
                order_two_next_forecast=str(other[0]))


def exact_tests():
    matrices=categorical(ACTIONS)
    initial=stationary(matrices)
    tape=balanced_tape(initial,matrices)
    blocks=moments(tape,4)
    population=exact_blocks(initial,matrices)
    assert blocks.anchor==population.anchor and ratios(blocks)==ratios(population)
    fitted,status=exact_closure(blocks)
    assert status=="closed" and same_law(fitted,ACTIONS,EMISSIONS,initial)
    assert same_actions(discover(tape,blocks,F(1,8)),ACTIONS)
    assert all(r==determinant(m) for r,m in zip(ratios(blocks),matrices,strict=True))
    assert brier_gap(initial,ACTIONS) == F(45,1024)
    recognized=0
    for actions in product(ACTIONS,repeat=4):
        if not any(f[0]==f[1] for f in actions) or not all(any(f[i]==1-i for f in actions) for i in (0,1)):
            continue
        m=categorical(actions)
        starting=stationary(m)
        recovered,reason=exact_closure(exact_blocks(starting,m))
        assert reason=="closed" and same_law(recovered,actions,EMISSIONS,starting)
        recognized+=1
    nonstationary,reason = exact_closure(exact_blocks((F(1),F(0)),matrices))
    assert nonstationary is None and reason == "initial two-state mixture is nonstationary"
    # A rank-one observation can reset to a mixture in a general stochastic realization.
    reset=[[F(1,8),F(1,8)],[F(1,8),F(1,8)]]
    repeat=[[F(1,2),F(0)],[F(0),F(1,4)]]
    other=[[F(1,4),F(0)],[F(0),F(1,2)]]
    soft=[reset,repeat,other]
    start=stationary(soft)
    soft_blocks=moments(balanced_tape(start,soft),3)
    invalid,reason=exact_closure(soft_blocks)
    assert invalid is None and reason=="third distinct post-reset forecast"
    successive=[law((0,)+(1,)*(k+1),start,soft)/law((0,)+(1,)*k,start,soft) for k in range(3)]
    assert successive==[F(3,8),F(5,12),F(9,20)]
    return dict(balanced_raw_tokens=len(tape),stationary=list(map(str,initial)),
                pivot=list(blocks.anchor),symbol_determinants=list(map(str,ratios(blocks))),
                recovered_actions=fitted["actions"],balanced_emissions=[list(map(str,r)) for r in fitted["emissions"]],
                stationary_one_step_excess_multiclass_brier=str(brier_gap(initial,ACTIONS)),
                recovered_topologies=recognized,counterexample_next_means=list(map(str,successive)),
                counterexample_verdict=reason,
                same_triples_different_law=matched_triple_control(initial,matrices))


def sampled_tape(n,seed):
    rng=Random(seed)
    state=int(rng.randrange(4)==0)
    data=bytearray()
    for _ in range(n):
        ticket=rng.randrange(8)
        for a,count in enumerate(WEIGHTS[state]):
            if ticket<count:
                break
            ticket-=count
        data.append(a)
        state=ACTIONS[a][state]
    return data


def profile(counts):
    low=high=0
    for row in counts:
        for n in row:
            if n:
                l,h=ratio_log(sum(row),n)
                low+=n*l
                high+=n*h
    return low,high


def exact_weight(counts):
    return prod(F(prod(n**n for n in row),sum(row)**sum(row)) for row in counts)


def exhaustive(data):
    best=None
    for actions in product(ACTIONS,repeat=4):
        counts,state,_=emission_counts(data,actions,0)
        bounds=profile(counts)
        take=best is None or bounds[1]<best_bounds[0]
        if best is not None and not take and bounds[0]<=best_bounds[1] and sorted(counts)!=sorted(best_counts):
            take=exact_weight(counts)>exact_weight(best_counts)
        if take:
            best,best_counts,best_state,best_bounds=actions,counts,state,bounds
    return best,smoothed(best_counts),best_state


def paired_stream(train, test, actions, emissions, state):
    successor=[[0]*4 for _ in range(4)]
    for x,y in zip(train[:-1],train[1:],strict=True):
        successor[x][y]+=1
    row_model=smoothed(successor)
    pair_counts=Counter()
    state_counts=Counter()
    last=train[-1]
    for a in test:
        pair_counts[last,a]+=1
        if state is not None:
            state_counts[state,a]+=1
            state=actions[a][state]
        last=a
    def score(cells,rows):
        lo=hi=0
        for (i,a),n in cells.items():
            p=rows[i][a]
            l,h=ratio_log(p.denominator,p.numerator)
            lo+=n*l
            hi+=n*h
        return outward((lo,hi),len(test))
    baseline=score(pair_counts,row_model)
    return score(state_counts,emissions) if state_counts else baseline, baseline


def experiment():
    n, report, seed=65536,16384,120311
    raw=sampled_tape(n+report,seed)
    train,test=raw[:n],raw[n:]
    blocks=moments(train,4)
    actions=discover(train,blocks,F(1,8))
    counts=[[0]*4 for _ in range(2)]
    state=None
    skipped=n
    if actions is not None:
        counts,state,skipped=emission_counts(train,actions)
    emissions=smoothed(counts)
    learned,baseline=paired_stream(train,test,actions,emissions,state)
    enumerated,freqs,terminal=exhaustive(train)
    conventional,_=paired_stream(train,test,enumerated,freqs,terminal)
    result=dict(registered_at="f8bae86",exact=exact_tests(),
                sampled=dict(seed=seed,training_tokens=n,report_tokens=report,pivot=blocks.anchor if blocks else None,
                             recovered_topology=same_actions(actions,ACTIONS), actions=actions,
                             training_emissions=counts, skipped_before_sync=skipped,
                             successful_fit_visits=3*(n-2)+n if actions is not None else None,
                             stored_action_bits=2*len(actions) if actions is not None else 0,
                             nll=dict(learned=learned,successor=baseline,exhaustive=conventional),
                             exhaustive_correct=same_actions(enumerated,ACTIONS),exhaustive_table_visits=256*n))
    return json.loads(json.dumps(result)),actions,emissions


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--r4-root",type=Path)
    args=parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result,actions,emissions=experiment()
    if args.r4_root and actions is not None:
        from positive_comparison import compare_emissions
        result["r4"]=compare_emissions(args.r4_root,"abcd",actions,emissions)
    if args.check:
        expected=json.loads(Path(__file__).with_name("unifilar_result.json").read_text())
        assert result=={k:expected[k] for k in result}
    print(json.dumps(result,indent=2))
