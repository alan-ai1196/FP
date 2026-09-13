"""Exact native control: pair-local and linear learners miss path information.

No RN-4 target is rerun. These explicit graphs are not RN-4 constructors or
resource-admitted Runtime states. The rounded checks are CPU interpreters,
not additional actual CUDA execution.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import json

import run_adaptive as experiment
from adaptive_model import AdaptivePosterior
from trajectory_oracle import floor_grid
from audit_balanced_uncertainty import observations
from audit_cuda_learner import model_initial, model_predict, model_observe, model_commit
from audit_float64_runtime import cpu_initial, cpu_predict, cpu_observe, cpu_commit
from audit_reference_events import forward_oracle
from fp_reference.empirical_bound import empirical_upper
from fp_reference.relation_proposal import relation_proposal
from fp_reference.native_search import GrammarLimits
from fp_reference.program import Source, Product, Sum, Term, Program
from fp_reference.learner import LearnerSpec


def mixture_graph(cfg, polynomial):
    assert polynomial in ('linear', 'quadratic', 'mixed')
    n=3
    nodes=[Source(s.source_id) for s in cfg.semantics.sources]
    features={}
    for i,j in product(range(n),repeat=2):
        features[i,j]=len(nodes)
        nodes.append(Product('mass',i,n+j))
    cells=[[],[]]
    for at,bits in enumerate(product((0,1),repeat=2)):
        hidden=(0,)+bits
        for y in (0,1):
            parent=len(nodes)
            nodes.append(Sum('mass',tuple(Term(features[i,j],at+2) for i,j in features
                        if i!=j and (hidden[i]^hidden[j])==y)))
            if polynomial in ('linear','mixed'):
                cells[y].append(Term(parent,0))
            if polynomial in ('quadratic','mixed'):
                nodes.append(Product('mass',parent,parent))
                cells[y].append(Term(len(nodes)-1,0))
    heads=[]
    for y in (0,1):
        within=tuple(Term(features[i,i],1) for i in range(n)) if y==0 else ()
        heads.append(len(nodes));nodes.append(Sum('mass',tuple(cells[y])+within))
    graph=Program(tuple(nodes),6,tuple(heads))
    graph.validate(cfg.semantics)
    return graph


def audit():
    cfg,old,*_=experiment.rn1.fixture_parameters(3)
    pattern=(F(1),F(8))+(F(1),)*6
    counts=((0,0,9,1),(1,1,9,1),(2,2,9,1))
    upper=empirical_upper(observations(cfg,counts),cfg.semantics,bit_limit=32768)
    v4=relation_proposal(upper,cfg.semantics,GrammarLimits(17,2,9,36,8),pattern,
        replace(old.searches[0].relation_sources,solver=experiment.SOLVER),bit_limit=32768).program
    assert v4 is not None
    graphs={'pair-local v4':v4,'linear assignment mixture':mixture_graph(cfg,'linear'),
            'quadratic assignment mixture':mixture_graph(cfg,'quadratic'),
            'linear-plus-quadratic mixture':mixture_graph(cfg,'mixed')}
    rows=[]
    for rate in (F(1,8),F(1)):
        t=rate/3;s=rate/(3+2*t*t)
        quadratic=F(1,2)+8*t*s/(2+4*(1+t*t)*(1+s*s))
        t=3*rate/10;s=rate/(10+4*t*t)
        mixed=F(1,2)+24*t*s/(2+4*(2+t*t+9*s*s+4*t*t*s*s))
        for labels in product((0,1),repeat=2):
            posterior=AdaptivePosterior(3,counts,'conditioned')
            for pair,label in zip(((0,1),(1,2)),labels):
                posterior.predict(*pair);posterior.observe(label)
            assert posterior.predict(0,2)[labels[0]^labels[1]]==F(189,250)
            for kind,graph in graphs.items():
                nonlinear=kind in ('quadratic assignment mixture','linear-plus-quadratic mixture')
                wanted=mixed if kind=='linear-plus-quadratic mixture' else quadratic
                initial=tuple(pattern[:graph.slot_count])
                for grid in (None,16):
                    theta=initial
                    cpu=cpu_initial(graph,cfg.semantics,pattern,0)
                    amp=model_initial(graph,cfg.semantics,theta)
                    spec=LearnerSpec(1,rate,grid)
                    for (i,j),label in zip(((0,1),(1,2)),labels):
                        sources=dict(zip((s.source_id for s in cfg.semantics.sources),experiment.rn1.context(3,i,j)))
                        p,g=forward_oracle(graph,cfg.semantics,theta,sources)
                        assert p==(F(1,2),F(1,2))
                        cp=cpu_predict(graph,cfg.semantics,cpu,sources)
                        ap=model_predict(graph,cfg.semantics,amp,sources)
                        theta=tuple(max(F(0),v-rate*d) for v,d in zip(theta,g[label]))
                        if grid is not None:
                            theta=tuple(map(floor_grid,theta))
                        cpu=cpu_commit(cpu_observe(graph,cpu,cp,label),spec)
                        amp=model_commit(model_observe(graph,amp,ap,label),spec)
                    sources=dict(zip((s.source_id for s in cfg.semantics.sources),experiment.rn1.context(3,0,2)))
                    p,_=forward_oracle(graph,cfg.semantics,theta,sources)
                    cp=cpu_predict(graph,cfg.semantics,cpu,sources)
                    ap=model_predict(graph,cfg.semantics,amp,sources)
                    target=labels[0]^labels[1]
                    if grid is None:
                        assert p[target]==(wanted if nonlinear else F(1,2))
                    else:
                        assert (p[target]>F(1,2))==nonlinear
                        assert (F(cp['probabilities'][target])>F(1,2))==nonlinear
                        assert (ap['probabilities'][target]>F(1,2))==nonlinear
                    assert abs(F(cp['probabilities'][target])-p[target])<F(1,10**12)
                    assert abs(ap['masses'][target]/sum(ap['masses'])-p[target])<F(1,1000)
                    if labels==(0,0):
                        rows.append({'graph':kind,'rate':str(rate),'grid':grid,
                            'next_path_probability_reference':str(p[target]),
                            'next_path_probability_binary64':cp['probabilities'][target],
                            'next_path_probability_rounded_AMP':str(ap['masses'][target]/sum(ap['masses']))})
    boundary=[]
    for kind in ('quadratic assignment mixture','linear-plus-quadratic mixture'):
        graph=graphs[kind];theta=tuple(pattern[:graph.slot_count])
        sources=dict(zip((s.source_id for s in cfg.semantics.sources),experiment.rn1.context(3,0,1)))
        _,g=forward_oracle(graph,cfg.semantics,theta,sources)
        theta=tuple(max(F(0),v-4*d) for v,d in zip(theta,g[0]))
        eliminated=tuple(i for i in range(2,6) if theta[i]==0)
        assert len(eliminated)==2
        _,g=forward_oracle(graph,cfg.semantics,theta,sources)
        theta=tuple(max(F(0),v-4*d) for v,d in zip(theta,g[1]))
        recovered=sum(theta[i]>0 for i in eliminated)
        assert recovered==(0 if kind=='quadratic assignment mixture' else 2)
        boundary.append({'graph':kind,'rate':'4','eliminated_after_one_label':2,
            'recovered_on_next_opposite_label':recovered})
    return {'status':'PASS','label_rate_graph_grid_cases':64,
        'projection_boundary_controls':boundary,
        'posterior_after_two_labels':'189/250','native_graph_counts':{k:v.counts() for k,v in graphs.items()},
        'representative_results':rows,
        'scope':'exact proof control and independent CPU/rounded interpreters; no owned construction, CUDA execution or RN-4 model score'}


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
