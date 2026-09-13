"""Exact synthetic model-dynamics audit, independent of RN-5 target tapes."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import json
import sys

import run_joint as experiment
from audit_component_symmetry import observations
from audit_reference_events import forward_oracle
from fp_reference.relation_proposal import relation_proposal
from fp_reference.empirical_bound import empirical_upper
from fp_reference.native_search import GrammarLimits
from fp_reference.program import Source,Sum,Term,Product,Program


def fixture(n):
    cfg,old,*_=experiment.rn1.fixture_parameters(n)
    prefix=(F(1),F(8))+(F(1),)*(n*(n-1))
    K=2**(n-1)
    grammar=GrammarLimits(2*n+n*n+2*K+2,2*K+2,n*n,(2+2*K)*n*n+2*K,len(prefix))
    upper=empirical_upper(observations(cfg,tuple((i,i,9,1) for i in range(n))),cfg.semantics,bit_limit=32768)
    proposal=relation_proposal(upper,cfg.semantics,grammar,prefix,
        replace(old.searches[0].relation_sources,solver=experiment.SOLVER),bit_limit=32768)
    assert proposal.program is not None and proposal.scale==8
    graph=proposal.program
    return cfg,graph,list(prefix[:graph.slot_count]),tuple(i for i in range(graph.slot_count) if i!=1)


def audit():
    identities=projected=gradients=large_steps=radial=0
    decreases={2:0,4:0,8:0,16:0}
    for n in (2,3,4,5):
        cfg,graph,theta,slots=fixture(n)
        K=2**(n-1)
        assert len(slots)==K
        for index in range(24):
            for k,slot in enumerate(slots):
                theta[slot]=F((index*(k+1)+k*k+index//3)%9,4)
            for i,j in sorted({(0,1),(n-2,n-1)}):
                inputs=dict(zip((v.source_id for v in cfg.semantics.sources),experiment.rn1.context(n,i,j)))
                probabilities,g,values=forward_oracle(graph,cfg.semantics,tuple(theta),inputs,return_values=True)
                masses=tuple(F(1)+values[h] for h in graph.heads);T=sum(masses)
                assert T==2+sum(theta[k]+theta[k]**2 for k in slots)
                d=F(1)-F(K,8)
                for label,eta in product((0,1),(F(1,8),F(1),F(4))):
                    M=masses[label];N=T-M
                    if eta==F(1,8):
                        # Every coordinate in this prediction-preserving
                        # direction is strictly positive, including a=0.
                        directions=[(theta[k]+theta[k]**2+F(2,K))/(1+2*theta[k]) for k in slots]
                        assert min(directions)>0
                        assert sum(direction*g[label][k] for k,direction in zip(slots,directions))==0
                        radial+=1
                    A=d*(1/M-2/T)
                    B=(M-d)*(1/T-1/M)**2+(N-d)/T**2
                    assert sum((theta[k]+F(1,2))*g[label][k] for k in slots)==2*A
                    assert sum(g[label][k]**2 for k in slots)==4*B
                    raw=[value-eta*derivative for value,derivative in zip(theta,g[label])]
                    rawT=2+sum(raw[k]+raw[k]**2 for k in slots)
                    assert rawT==T-4*eta*A+4*eta**2*B
                    identities+=1;gradients+=len(slots)
                    if min(raw)>=0 and rawT<T:
                        decreases[K]+=1
                    if K==8 and eta<=T/2:
                        actual=[max(F(0),v) for v in raw]
                        _,_,after=forward_oracle(graph,cfg.semantics,tuple(actual),inputs,return_values=True)
                        actualT=2+sum(after[h] for h in graph.heads)
                        assert actualT>=T+4*eta**2*N/(T*M)>T
                        projected+=1
                if K==8:
                    for label in (0,1):
                        eta=T;M=masses[label];N=T-M
                        actual=tuple(max(F(0),value-eta*derivative) for value,derivative in zip(theta,g[label]))
                        _,_,after=forward_oracle(graph,cfg.semantics,actual,inputs,return_values=True)
                        actualT=2+sum(after[h] for h in graph.heads)
                        assert actualT==M*(1+2*N/M)**2+1>T
                        large_steps+=1
    assert decreases[2]>0 and decreases[4]>0 and decreases[8]==0
    cfg,graph,theta,slots=fixture(4)
    inputs=dict(zip((v.source_id for v in cfg.semantics.sources),experiment.rn1.context(4,0,1)))
    examples=[]
    for amplitude,eta in ((F(1),F(1)),(F(5,2),F(1)),(F(1),F(1,4))):
        for k in slots:theta[k]=amplitude
        p,g=forward_oracle(graph,cfg.semantics,tuple(theta),inputs)
        assert p==(F(1,2),F(1,2))
        updated=tuple(max(F(0),v-eta*dv) for v,dv in zip(theta,g[0]))
        actual=forward_oracle(graph,cfg.semantics,updated,inputs)[0][0]
        examples.append(str(actual))
    assert examples==['25/41','1369/2594','1369/2594']
    # Pure squares retain a suboptimal first-order stationary point at zero.
    # This is a free-parameter counterexample, not an initializer/profile
    # reachability claim or an optimizer action for the registered model.
    square=Program((Source(cfg.semantics.sources[0].source_id),
        Sum('mass',(Term(0,0),)),Product('mass',1,1),
        Sum('mass',(Term(0,1),)),Product('mass',3,3)),2,(2,4))
    square.validate(cfg.semantics)
    neutral,zero_gradient=forward_oracle(square,cfg.semantics,(F(0),F(0)),inputs)
    improved,_=forward_oracle(square,cfg.semantics,(F(1),F(0)),inputs)
    assert neutral==(F(1,2),F(1,2)) and zero_gradient==((F(0),F(0)),(F(0),F(0)))
    assert improved==(F(2,3),F(1,3))
    assert improved[0]**9*improved[1]>neutral[0]**9*neutral[1]
    assert radial==336
    assert identities==1008 and 'torch' not in sys.modules
    return {'exact_mass_drift_identities':identities,'full_graph_gradient_coordinates':gradients,
        'positive_value_preserving_direction_checks':radial,
        'square_zero_stationary_counterexample':{'before':list(map(str,neutral)),'better_free_parameters':list(map(str,improved))},
        'projected_K8_strict_growth_controls':projected,
        'large_rate_K8_projection_growth_controls':large_steps,
        'legal_unrounded_decrease_controls_by_K':decreases,
        'rescaled_same_forecast_different_next_learner':examples,
        'scope':'unrounded synthetic dynamics; no grid/AMP monotonicity or new target score'}


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
