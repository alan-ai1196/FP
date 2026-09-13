"""Separate fixed-endpoint empirical fit from causal recurrent evidence.

Exact information-model audit. Existing Runtime/search semantics are used
unchanged, and no retrospective score receives fresh or Bayesian authority.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations,product
import json
import sys

import recurrent_control as native
from fp_reference import ReferenceCompilerRuntime,CompilerPolicy
from fp_reference.program import Sum,Term
from fp_reference.search import likelihood
from audit_float64_runtime import replay
from ingress_audit_support import deliver_context


def marginal(n,observations,noise):
    total=F(0)
    for z in product((0,1),repeat=n):
        weight=F(1,2**n)
        for i,j,label in observations:
            weight*=1-noise if z[i]^z[j]==label else noise
        total+=weight
    return total


def forest(n,edges):
    parent=list(range(n))
    def root(i):
        while parent[i]!=i:
            i=parent[i]
        return i
    for i,j in edges:
        a,b=root(i),root(j)
        if a==b:
            return False
        parent[a]=b
    return True


def exact_information():
    noises=(F(0),F(1,10),F(1,4),F(1,2))
    graphs=forecasts=cycles=0
    for n in (2,3,4):
        available=tuple(combinations(range(n),2))
        for size in range(n):
            for edges in combinations(available,size):
                if not forest(n,edges):
                    continue
                graphs+=1
                for labels,noise in product(product((0,1),repeat=size),noises):
                    observations=tuple((i,j,y) for (i,j),y in zip(edges,labels))
                    assert marginal(n,observations,noise)==F(1,2**size)
                    forecasts+=1
    for noise,labels in product(noises,product((0,1),repeat=3)):
        observations=tuple((i,j,y) for (i,j),y in zip(((0,1),(1,2),(0,2)),labels))
        sign=(-1)**sum(labels)
        expected=(1+sign*(1-2*noise)**3)/8
        assert marginal(3,observations,noise)==expected
        cycles+=1
    assert marginal(3,((0,1,0),(1,2,0)),F(1,10))==F(1,4)
    assert marginal(3,((0,1,0),(1,2,0),(0,2,0)),F(1,10))==F(189,1000)
    assert marginal(3,((0,1,0),(1,2,0),(0,2,0)),F(1,4))==F(9,64)
    return {'forest_graphs':graphs,'exact_signed_forest_noise_likelihoods':forecasts,
        'exact_signed_triangle_noise_likelihoods':cycles,
        'forest_noise_distribution_identification':False,'one_cycle_changes_the_distribution':True,
        'same_two_labels_next_query_probabilities':['189/250','9/16']}


def endpoint_control(kind,excess):
    noise=F(1,excess+2)
    n=2 if kind=='repeat' else 3
    sequence=((0,1,0),(0,1,0)) if kind=='repeat' else ((0,1,0),(1,2,0))
    cfg,graph,online,_=native.fixture(n=n,window=2,horizon=2)
    # Every forest model uses the same declared initializer and retains all
    # four coordinates. Only its native SUM-edge slot references differ.
    # The existing H2 bounds for excess8 cover all available noise slots.
    initializer=tuple(map(F,(1,0,2,8)))
    selected=initializer.index(F(excess))
    graph=replace(graph,slot_count=4,nodes=tuple(
        replace(node,terms=tuple(Term(t.parent,selected if t.slot==1 else 0) for t in node.terms))
        if type(node) is Sum else node for node in graph.nodes))
    cfg=replace(cfg,initializer_pattern=initializer)
    rt=ReferenceCompilerRuntime(cfg,graph,online=online,policy=CompilerPolicy(()))
    causal=F(1)
    for at,(i,j,label) in enumerate(sequence):
        forecast=deliver_context(rt,f'bayes-{at}',native.context(n,i,j))
        assert forecast.status=='PREDICTED_REFERENCE'
        pending=rt.snapshot()
        assert pending.pending.record.target is None
        p=dict(forecast.predictions)[pending.deployed_id]
        causal*=p[label]
        assert rt.observe(label).status=='OBSERVED_REFERENCE'
    final=rt.snapshot()
    assert final.run.status=='SEALED_REFERENCE_STREAM' and final.halted is None
    assert final.candidates[0].theta==initializer
    assert len(final.observations)==2 and not final.reference_proofs and not final.install_receipts
    retrospective=likelihood(graph,cfg.semantics,final.candidates[0].learner,final.observations,bit_limit=32768)
    assert rt.snapshot()==final  # This read-only audit supplies no Runtime transition.
    assert causal==marginal(n,sequence,noise)
    if kind=='repeat':
        assert excess==8 and causal==F(41,100) and retrospective==F(73,100)
    else:
        assert causal==F(1,4) and retrospective==(1+(1-2*noise)**2)/4
    phases,*_=replay(rt)
    assert phases==7
    return {'kind':kind,'registered_excess':excess,'noise':str(noise),
        'shared_initializer':list(map(str,initializer)),'selected_noise_slot':selected,
        'causal_sequence_likelihood':str(causal),'frozen_endpoint_likelihood':str(retrospective),
        'independent_binary64_phases':phases,'run_status':final.run.status,
        'host_scope':final.run.host_scope,'class_fresh_or_Bayesian_certificate':False}


if __name__=='__main__':
    results={'information':exact_information(),
        'native_controls':[endpoint_control('repeat',8)]+[endpoint_control('forest',s) for s in (0,2,8)]}
    assert 'torch' not in sys.modules
    print(json.dumps(results,indent=2))
