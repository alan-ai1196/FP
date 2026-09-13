"""Independent one-hot v5 trajectories; no Runtime or certificate construction."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import sys

import run_joint as experiment
from joint_model import context
from analyze_study import component_model
from audit_cuda_learner import q,model_initial,model_predict,model_observe,model_commit
from audit_float64_runtime import cpu_initial,cpu_predict,cpu_observe,cpu_commit
from audit_reference_events import forward_oracle
from audit_component_symmetry import observations
from fp_reference.relation_proposal import relation_proposal
from fp_reference.empirical_bound import empirical_upper
from fp_reference.native_search import GrammarLimits
from fp_reference.learner import LearnerSpec
HALF,SINGLE=experiment.rn1.HALF,experiment.rn1.SINGLE


def floor_grid(value):
    scaled=F(value)*65536
    return F(scaled.numerator//scaled.denominator,65536)


class JointLearner:
    def __init__(self,n,counts,rate,path):
        assert path in ('reference','binary64','AMP')
        self.path,self.rate=path,F(rate)
        self.components,self.assignment,self.scale,_,self.likelihood=component_model(n,counts)
        self.component_of={v:k for k,c in enumerate(self.components) for v in c}
        c=len(self.components)
        self.members=tuple(tuple(self.assignment[i]^flips[self.component_of[i]] for i in range(n))
            for flips in ((0,)+bits for bits in product((0,1),repeat=c-1))) if c>1 else ()
        self.scale_slot=0 if self.scale==1 else 1
        prefix=[F(1),F(8)]+[F(1)]*(n*(n-1))
        self.slots=tuple(i for i,v in enumerate(prefix) if v==1 and i!=self.scale_slot)[:len(self.members)]
        assert len(self.slots)==len(self.members)
        self.theta=[self.cast(v) for v in prefix[:max((self.scale_slot,)+self.slots)+1]]
        self.pending=None

    def cast(self,value):
        return float(value) if self.path=='binary64' else q(F(value)) if self.path=='AMP' else F(value)

    def half(self,value):
        return q(F(value),HALF) if self.path=='AMP' else value

    def predict(self,i,j):
        assert self.pending is None
        coefficients=tuple(self.half(v) for v in self.theta)
        cross=self.component_of[i]!=self.component_of[j]
        parity=self.assignment[i]^self.assignment[j]
        excess=[self.cast(0),self.cast(0)]
        if cross:
            active=tuple((slot,member[i]^member[j]) for slot,member in zip(self.slots,self.members))
            for slot,y in active:
                a=coefficients[slot]
                excess[y]=self.cast(excess[y]+a)
                excess[y]=self.cast(excess[y]+self.half(a*a))
        else:
            active=((self.scale_slot,parity),)
            excess[parity]=coefficients[self.scale_slot]
        masses=tuple(self.cast(1+self.half(v)) for v in excess)
        total=self.cast(sum(masses))
        raw=tuple(self.cast(v/total) for v in masses)
        self.pending=(cross,active,coefficients,masses,total)
        exact=tuple(map(F,masses))
        return tuple(v/sum(exact) for v in exact),tuple(map(F,raw))

    def observe(self,label):
        assert self.pending is not None
        cross,active,coefficients,masses,total=self.pending
        inverse_t,inverse_y=self.cast(1/total),self.cast(1/masses[label])
        target=self.cast(inverse_t-inverse_y)
        gradient=[self.cast(0)]*len(self.theta)
        for slot,y in active:
            seed=target if y==label else inverse_t
            if cross:
                # Direct head edge, outer weighted inner SUM, then the inner
                # SUM in reverse traversal. Round each primitive separately.
                repeated=self.cast(seed*coefficients[slot])
                gradient[slot]=self.cast(self.cast(seed+repeated)+repeated)
            else:
                gradient[slot]=seed
        self.theta=[self.cast(floor_grid(max(0,self.cast(v-self.cast(self.cast(self.rate)*g)))))
            for v,g in zip(self.theta,gradient)]
        self.pending=None


def reduction_audit():
    checked=0
    for n,counts in ((4,((0,1,9,1),(2,3,1,9))),
                     (4,((0,1,4,6),(2,3,6,4))),
                     (6,((0,1,8,2),(2,3,5,5),(4,5,1,9)))):
        cfg,old,*_=experiment.rn1.fixture_parameters(n)
        prefix=(F(1),F(8))+(F(1),)*(n*(n-1))
        grammar=GrammarLimits(2*n+n*n+18,n*n+18,n*n+4,18*n*n+16,len(prefix))
        upper=empirical_upper(observations(cfg,counts),cfg.semantics,bit_limit=32768)
        proposed=relation_proposal(upper,cfg.semantics,grammar,prefix,
            replace(old.searches[0].relation_sources,solver=experiment.SOLVER),bit_limit=32768)
        graph=proposed.program
        assert graph is not None
        for rate in (F(1),F(4)):
            spec=LearnerSpec(1,rate,16)
            reference=tuple(prefix[:graph.slot_count])
            cpu=cpu_initial(graph,cfg.semantics,prefix,0)
            amp=model_initial(graph,cfg.semantics,reference)
            learners={path:JointLearner(n,counts,rate,path) for path in ('reference','binary64','AMP')}
            assert all(len(m.theta)==graph.slot_count for m in learners.values())
            for repeat in range(3):
                for i,j in product(range(n),repeat=2):
                    label=(i+j+repeat)%2
                    sources=dict(zip((v.source_id for v in cfg.semantics.sources),context(n,i,j)))
                    p,gradients=forward_oracle(graph,cfg.semantics,reference,sources)
                    cp=cpu_predict(graph,cfg.semantics,cpu,sources)
                    ap=model_predict(graph,cfg.semantics,amp,sources)
                    assert learners['reference'].predict(i,j)==(p,p)
                    for path,prediction in (('binary64',cp),('AMP',ap)):
                        mass=tuple(map(F,prediction['masses']))
                        assert learners[path].predict(i,j)==(tuple(v/sum(mass) for v in mass),tuple(map(F,prediction['probabilities'])))
                    reference=tuple(floor_grid(max(0,v-rate*g)) for v,g in zip(reference,gradients[label]))
                    cpu=cpu_commit(cpu_observe(graph,cpu,cp,label),spec)
                    amp=model_commit(model_observe(graph,amp,ap,label),spec)
                    for path,state in (('reference',reference),('binary64',cpu.theta),('AMP',amp.theta)):
                        learners[path].observe(label)
                        assert tuple(learners[path].theta)==state,(n,rate,repeat,i,j,path,learners[path].theta,state)
                        checked+=1
    assert checked==1224 and 'torch' not in sys.modules
    return {'independent_forecast_and_successor_checks':checked,
        'paths':['reference','binary64','rounded AMP'],'rates':['1','4'],'synthetic_only':True}


def sign_obstruction_audit():
    # Fixed learner-state identities, not scores aggregated across changing
    # states. No RN-5 target data or generated evaluation tape is consumed.
    learner=JointLearner(4,((0,1,4,6),(2,3,9,1)),F(1),'reference')
    count=0
    for values in product((F(0),F(1,2),F(1),F(2)),repeat=3):
        theta=list(learner.theta)
        for slot,v in zip((learner.scale_slot,)+learner.slots,values):
            theta[slot]=v
        learner.theta=theta
        def predict(i,j):
            p,_=learner.predict(i,j)
            learner.pending=None
            return p
        assert predict(0,1)[0]<=F(1,2)
        for j in (2,3):
            assert predict(0,j)[0]+predict(1,j)[0]==1
            assert predict(j,0)==predict(0,j)
            assert predict(j,1)==predict(1,j)
        count+=1
    assert count==64
    return {'fixed_state_wrong_sign_controls':count,'no_prequential_cross_query_lower_bound':True}


if __name__=='__main__':
    import json
    print(json.dumps({'reduction':reduction_audit(),'sign_obstruction':sign_obstruction_audit()},indent=2))
