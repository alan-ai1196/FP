"""Exact factor/forest learning laws against native graph SGD and full Bayes.

Synthetic data only. No Runtime state, target tape, commit grid or GPU claim.
"""
from fractions import Fraction as F
from itertools import combinations,product
import json
from math import prod
import sys

from scale_dynamics import fixture,forward_oracle,experiment


def general_factor_audit():
    updates=coordinates=nonneutral=clipped=0
    for n in (3,4,5):
        cfg,graph,initial,slots=fixture(n)
        worlds=tuple((0,)+bits for bits in product((0,1),repeat=n-1))
        sequences=[((0,1),(1,2),(0,2),(0,1)),((0,1),(0,1),(1,2),(0,2))]
        if n>=4:
            sequences.append(((0,1),(2,3),(1,2),(0,3)))
        sources=lambda i,j:dict(zip((v.source_id for v in cfg.semantics.sources),experiment.rn1.context(n,i,j)))
        for sequence,labels,eta in product(sequences,product((0,1),repeat=4),(F(1,8),F(1))):
            theta=tuple(initial);factors={}
            for (i,j),label in zip(sequence,labels):
                p,g=forward_oracle(graph,cfg.semantics,theta,sources(i,j))
                T=2+sum(theta[k]+theta[k]**2 for k in slots)
                S=sum((theta[k]+F(1,2))**2 for k in slots)
                Q=p[label];lam=eta/T
                A=1-2*lam+lam/Q;B=lam/Q
                raw=tuple(v-eta*dv for v,dv in zip(theta,g[label]))
                for slot,z in zip(slots,worlds):
                    expected=(theta[slot]+F(1,2))*(A+B*(-1)**(label^z[i]^z[j]))-F(1,2)
                    assert raw[slot]==expected
                    coordinates+=1
                next_S=sum((raw[k]+F(1,2))**2 for k in slots)
                assert next_S==(A*A+B*B)*S+2*A*B*T*(2*Q-1)
                updates+=1;nonneutral+=Q!=F(1,2)
                if min(raw)<0:
                    clipped+=1
                    break
                edge=tuple(sorted((i,j)))
                previous=factors.get(edge,(F(1),F(1)))
                factor=(A+B*(-1)**label,A-B*(-1)**label)
                assert min(factor)>0
                factors[edge]=tuple(a*b for a,b in zip(previous,factor))
                for slot,z in zip(slots,worlds):
                    assert raw[slot]+F(1,2)==F(3,2)*prod(value[z[u]^z[v]] for (u,v),value in factors.items())
                theta=raw
    assert nonneutral>0
    return {'general_native_factor_updates':updates,'general_native_factor_coordinates':coordinates,
        'nonneutral_cycle_or_repeated_edge_updates':nonneutral,
        'prefixes_stopped_at_projection':clipped}


def path(n,history,start,end):
    adjacency=[[] for _ in range(n)]
    for i,j,label,lam in history:
        rho=4*lam/(1+4*lam*lam)
        adjacency[i].append((j,(-1)**label*rho,(-1)**label))
        adjacency[j].append((i,(-1)**label*rho,(-1)**label))
    queue=[(start,F(1),1,0)];seen={start}
    for vertex,correlation,sign,length in queue:
        if vertex==end:
            return correlation,sign,length
        for other,rho,edge_sign in adjacency[vertex]:
            if other not in seen:
                seen.add(other)
                queue.append((other,correlation*rho,sign*edge_sign,length+1))
    return None


def audit():
    states=coordinates=forecasts=updates=bayes_checks=0
    per_n={}
    for n in (2,3,4,5):
        cfg,graph,initial,slots=fixture(n)
        K=len(slots);offset=2-F(K,4)
        orientations=tuple((0,)+bits for bits in product((0,1),repeat=n-1))
        assignments=tuple(product((0,1),repeat=n))
        pairs=tuple(combinations(range(n),2))
        inputs={pair:dict(zip((v.source_id for v in cfg.semantics.sources),
            experiment.rn1.context(n,*pair))) for pair in pairs}
        before=states
        for eta in (F(1,8),F(1)):
            def visit(theta,history,S,weights):
                nonlocal states,coordinates,forecasts,updates,bayes_checks
                T=S+offset
                assert T==2+sum(theta[k]+theta[k]**2 for k in slots)
                for slot,orientation in zip(slots,orientations):
                    expected=F(3,2)*prod(1+2*lam*(-1)**(label^orientation[i]^orientation[j])
                        for i,j,label,lam in history)
                    assert theta[slot]+F(1,2)==expected>=F(1,2)
                    coordinates+=1
                states+=1;next_edges=[]
                for i,j in pairs:
                    p,g=forward_oracle(graph,cfg.semantics,theta,inputs[i,j])
                    route=path(n,history,i,j)
                    contrast=F(0) if route is None else S/T*route[0]
                    assert p[0]==(1+contrast)/2
                    forecasts+=1
                    bayes=sum(weight*F(9 if latent[i]==latent[j] else 1,10)
                        for latent,weight in zip(assignments,weights))/sum(weights)
                    conditional=F(1,2) if route is None else (1+route[1]*F(4,5)**(route[2]+1))/2
                    assert bayes==conditional
                    bayes_checks+=1
                    if route is None:
                        next_edges.append((i,j,g))
                for i,j,g in next_edges:
                    # Exhaust every ordered forest prefix through n=4.
                    # At n=5 retain the full signed path prefixes, which
                    # additionally test the negative normalization offset.
                    if n==5 and (i,j)!=(len(history),len(history)+1):
                        continue
                    for label in (0,1):
                        lam=eta/T
                        next_theta=tuple(v-eta*derivative for v,derivative in zip(theta,g[label]))
                        assert min(next_theta)>=0
                        for slot,orientation in zip(slots,orientations):
                            sign=(-1)**(label^orientation[i]^orientation[j])
                            assert g[label][slot]==-(1+2*theta[slot])*sign/T
                        next_weights=tuple(w*(9 if (z[i]^z[j])==label else 1)
                            for z,w in zip(assignments,weights))
                        updates+=1
                        visit(next_theta,history+((i,j,label,lam),),S*(1+4*lam*lam),next_weights)
            visit(tuple(initial),(),F(9*K,4),(1,)*len(assignments))
        per_n[n]=states-before

    # An unrelated fourth component dilutes the same two-label evidence.
    dilution=[]
    for n in (3,4,5):
        cfg,graph,theta,slots=fixture(n)
        inputs=lambda i,j:dict(zip((v.source_id for v in cfg.semantics.sources),experiment.rn1.context(n,i,j)))
        for i,j in ((0,1),(1,2)):
            p,g=forward_oracle(graph,cfg.semantics,tuple(theta),inputs(i,j))
            assert p==(F(1,2),F(1,2))
            theta=[v-dv for v,dv in zip(theta,g[0])]
            assert min(theta)>=0
        actual=forward_oracle(graph,cfg.semantics,tuple(theta),inputs(0,2))[0][0]
        dilution.append({'components':n,'FP_exact_rate1':str(actual),
            'FP_binary64_display':float(actual),'same_information_Bayes':str(F(189,250))})
    assert [F(r['FP_exact_rate1']) for r in dilution[:2]]==[F(20289979,35917958),F(292289,558010)]

    # Even unequal rates cannot calibrate all three noisy pair forecasts
    # within the unprojected two-edge family: its global S/T is too large.
    calibration=boundary=0
    for n in (3,4,5):
        cfg,graph,initial,slots=fixture(n)
        K=len(slots)
        inputs=lambda i,j:dict(zip((v.source_id for v in cfg.semantics.sources),experiment.rn1.context(n,i,j)))
        for rates,labels in product(product((F(1,8),F(1),F(4)),repeat=2),product((0,1),repeat=2)):
            theta=tuple(initial)
            for (i,j),eta,label in zip(((0,1),(1,2)),rates,labels):
                p,g=forward_oracle(graph,cfg.semantics,theta,inputs(i,j))
                assert p==(F(1,2),F(1,2))
                theta=tuple(v-eta*dv for v,dv in zip(theta,g[label]))
                if min(theta)<0:
                    boundary+=1
                    break
            else:
                T=2+sum(theta[k]+theta[k]**2 for k in slots)
                S=sum((theta[k]+F(1,2))**2 for k in slots)
                R=S/T
                assert R>=min(F(9*K,8*(K+1)),F(1))>F(4,5)
                contrasts=[]
                for (i,j),label in zip(((0,1),(1,2),(0,2)),(*labels,labels[0]^labels[1])):
                    p=forward_oracle(graph,cfg.semantics,theta,inputs(i,j))[0][0]
                    contrasts.append((-1)**label*(2*p-1))
                assert contrasts[2]*R==contrasts[0]*contrasts[1]
                assert tuple(contrasts)!=(F(16,25),F(16,25),F(64,125))
                calibration+=1

    # At rate4 the third K8 forest update clips: the no-projection formula
    # must stop there, even though the new edge is still conditionally neutral.
    cfg,graph,theta,slots=fixture(4)
    inputs=lambda i,j:dict(zip((v.source_id for v in cfg.semantics.sources),experiment.rn1.context(4,i,j)))
    history=();S=F(18)
    for step,(i,j) in enumerate(((0,1),(1,2),(2,3))):
        T=2+sum(theta[k]+theta[k]**2 for k in slots)
        p,g=forward_oracle(graph,cfg.semantics,tuple(theta),inputs(i,j))
        assert p==(F(1,2),F(1,2))
        lam=4/T
        raw=tuple(v-4*dv for v,dv in zip(theta,g[0]))
        assert (min(raw)<0)==(step==2)
        theta=tuple(max(F(0),v) for v in raw)
        history+=((i,j,0,lam),);S*=1+4*lam*lam
    projected=forward_oracle(graph,cfg.semantics,theta,inputs(0,3))[0][0]
    invalid_forest_value=(1+path(4,history,0,3)[0])/2
    assert projected!=invalid_forest_value
    worlds=tuple((0,)+bits for bits in product((0,1),repeat=3))
    # A zero-field pairwise log density has zero four-spin coefficient.
    # This positive-weight product test avoids any logarithm approximation.
    four_spin_products=tuple(prod((theta[slot]+F(1,2))**2 for slot,z in zip(slots,worlds)
        if sum(z)%2==parity) for parity in (0,1))
    assert four_spin_products[0]!=four_spin_products[1]

    # Same all-pair forecasts AND same scale can still hide a usable moment.
    # These are free rational parameter states, not claimed RN-5 endpoints.
    hidden_moment=[]
    for orientation in (0,1):
        state=list(theta)
        for slot,z in zip(slots,worlds):
            state[slot]=F(3,2) if sum(z)%2==orientation else F(1,2)
        assert 2+sum(state[k]+state[k]**2 for k in slots)==20
        for i,j in combinations(range(4),2):
            assert forward_oracle(graph,cfg.semantics,tuple(state),inputs(i,j))[0]==(F(1,2),F(1,2))
        _,g=forward_oracle(graph,cfg.semantics,tuple(state),inputs(0,1))
        successor=tuple(v-dv for v,dv in zip(state,g[0]))
        assert min(successor)>=0
        hidden_moment.append(forward_oracle(graph,cfg.semantics,successor,inputs(2,3))[0][0])
    assert hidden_moment==[F(113,202),F(89,202)]

    # Closing a cycle destroys the neutral-query assumption before clipping.
    cfg,graph,theta,slots=fixture(3)
    inputs=lambda i,j:dict(zip((v.source_id for v in cfg.semantics.sources),experiment.rn1.context(3,i,j)))
    for i,j in ((0,1),(1,2)):
        p,g=forward_oracle(graph,cfg.semantics,tuple(theta),inputs(i,j))
        theta=[v-dv for v,dv in zip(theta,g[0])]
    p,g=forward_oracle(graph,cfg.semantics,tuple(theta),inputs(0,2))
    assert p[0]>F(1,2)
    T=2+sum(theta[k]+theta[k]**2 for k in slots)
    orientations=tuple((0,)+bits for bits in product((0,1),repeat=2))
    wrong=list(theta)
    for slot,z in zip(slots,orientations):
        wrong[slot]=(theta[slot]+F(1,2))*(1+2/T*(-1)**(z[0]^z[2]))-F(1,2)
    actual=tuple(v-dv for v,dv in zip(theta,g[0]))
    assert min(actual)>=0 and tuple(wrong)!=actual
    assert per_n=={2:6,3:62,4:1802,5:62} and 'torch' not in sys.modules
    return {'exact_prefix_states':states,'states_by_components':per_n,
        'native_shifted_amplitude_coordinates':coordinates,'native_forest_forecasts':forecasts,
        'native_gradient_successors':updates,'independent_full_posterior_forecasts':bayes_checks,
        'unrelated_component_dilution':dilution,
        'unequal_rate_calibration_obstruction_controls':calibration,
        'rate_pairs_outside_unprojected_hypothesis':boundary,
        'Bayes_matching_forecasts_after_two_edges':['41/50','41/50','189/250'],
        'projection_counterexample':{'actual_projected':str(projected),'invalid_unprojected_prediction':str(invalid_forest_value)},
        'projected_state_has_nonzero_four_spin_log_interaction':True,
        'same_scale_same_pair_predictions_different_next_prediction':list(map(str,hidden_moment)),
        'cycle_counterexample_forecast_before_update':str(p[0]),
        **general_factor_audit(),
        'scope':'exact unrounded general factors and forest path laws; explicit projection boundary; no grid/AMP or target-model score claim'}


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
