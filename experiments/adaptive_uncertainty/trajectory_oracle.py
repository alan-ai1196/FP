"""Independent one-hot v4 trajectory oracle and full-graph reduction checks.

This is post-analysis only. It constructs no Runtime state and supplies no
certificate or forecast to an experiment worker.
"""
from fractions import Fraction as F
from itertools import product
import sys

import run_adaptive as experiment
from adaptive_model import context
sys.path.insert(0, str(experiment.ROOT/'experiments/component_uncertainty'))
from analyze_study import component_model
from audit_cuda_learner import q, model_initial, model_predict, model_observe, model_commit
from audit_float64_runtime import cpu_initial, cpu_predict, cpu_observe, cpu_commit
from audit_reference_events import forward_oracle
from audit_balanced_uncertainty import observations
from fp_reference.relation_proposal import relation_proposal
from fp_reference.empirical_bound import empirical_upper
from fp_reference.native_search import GrammarLimits
from fp_reference.learner import LearnerSpec
HALF, SINGLE = experiment.rn1.HALF, experiment.rn1.SINGLE


def floor_grid(value):
    value=F(value)*(1 << 16)
    return F(value.numerator//value.denominator, 1 << 16)


class ScalarLearner:
    def __init__(self, n, counts, rate, path):
        assert path in ('reference', 'binary64', 'AMP')
        self.path, self.rate = path, F(rate)
        self.components, self.assignment, self.scale, self.initial_probabilities, self.likelihood = component_model(n, counts)
        self.component_of = {v:k for k, group in enumerate(self.components) for v in group}
        self.scale_slot = 0 if self.scale == 1 else 1
        prefix = [F(1), F(8)]+[F(1)]*(n*(n-1))
        units = iter(i for i,v in enumerate(prefix) if v == 1 and i != self.scale_slot)
        self.pair_slots = { (k,l): (next(units),next(units))
            for k in range(len(self.components)) for l in range(k+1,len(self.components)) }
        size=max([self.scale_slot]+[j for pair in self.pair_slots.values() for j in pair])+1
        self.theta = [self.cast(v) for v in prefix[:size]]
        self.pending = None

    def cast(self, value):
        return float(value) if self.path == 'binary64' else q(F(value)) if self.path == 'AMP' else F(value)

    def predict(self, i, j):
        assert self.pending is None
        k,l = self.component_of[i],self.component_of[j]
        parity = self.assignment[i]^self.assignment[j]
        slots = (self.scale_slot,None) if k == l and parity == 0 else (None,self.scale_slot) if k == l else tuple(self.pair_slots[tuple(sorted((k,l)))][y^parity] for y in (0,1))
        excess = [self.cast(0) if slot is None else self.theta[slot] for slot in slots]
        if self.path == 'AMP':
            excess = [q(v,HALF) for v in excess]
        masses = tuple(self.cast(1+v) for v in excess)
        total = self.cast(sum(masses))
        raw = tuple(self.cast(v/total) for v in masses)
        self.pending = (slots,masses,total)
        exact_masses = tuple(map(F,masses))
        return tuple(v/sum(exact_masses) for v in exact_masses), tuple(map(F,raw))

    def observe(self, label):
        assert self.pending is not None and label in (0,1)
        slots,masses,total = self.pending
        inv_t,inv_y = self.cast(1/total),self.cast(1/masses[label])
        seed = self.cast(inv_t-inv_y)
        gradients = [self.cast(0)]*len(self.theta)
        for y,slot in enumerate(slots):
            if slot is not None:
                assert not gradients[slot]
                gradients[slot] = seed if y == label else inv_t
        self.theta = [self.cast(floor_grid(max(0,self.cast(v-self.cast(self.cast(self.rate)*g)))))
                      for v,g in zip(self.theta,gradients)]
        self.pending = None


def reduction_audit():
    # Synthetic support/count fixtures only: no RN-4 new target tapes.
    comparisons=0
    for n,counts in ((4,((0,1,9,1),(2,3,1,9))),
                     (6,((0,1,8,2),(2,3,5,5),(4,5,1,9)))):
        cfg,old,*_=experiment.rn1.fixture_parameters(n)
        prefix=(F(1),F(8))+(F(1),)*(n*(n-1))
        grammar=GrammarLimits(2*n+n*n+2,2,n*n,4*n*n,len(prefix))
        from dataclasses import replace
        upper=empirical_upper(observations(cfg,counts),cfg.semantics,bit_limit=32768)
        proposed=relation_proposal(upper,cfg.semantics,grammar,prefix,
            replace(old.searches[0].relation_sources,solver=experiment.SOLVER),bit_limit=32768)
        graph=proposed.program
        assert graph is not None
        for rate in (F(1,8),F(4)):
            spec=LearnerSpec(1,rate,16)
            reference=tuple(prefix[:graph.slot_count])
            cpu=cpu_initial(graph,cfg.semantics,prefix,0)
            amp=model_initial(graph,cfg.semantics,reference)
            learners={p:ScalarLearner(n,counts,rate,p) for p in ('reference','binary64','AMP')}
            assert all(len(m.theta)==graph.slot_count for m in learners.values())
            for repeat in range(3):
                for i,j in product(range(n),repeat=2):
                    label=(i+j+repeat)%2
                    sources=dict(zip((s.source_id for s in cfg.semantics.sources),context(n,i,j)))
                    exact_p,gradients=forward_oracle(graph,cfg.semantics,reference,sources)
                    cp=cpu_predict(graph,cfg.semantics,cpu,sources)
                    ap=model_predict(graph,cfg.semantics,amp,sources)
                    assert learners['reference'].predict(i,j)==(exact_p,exact_p)
                    for path,prediction in (('binary64',cp),('AMP',ap)):
                        mass=tuple(map(F,prediction['masses']))
                        assert learners[path].predict(i,j)==(tuple(v/sum(mass) for v in mass),tuple(map(F,prediction['probabilities'])))
                    reference=tuple(floor_grid(max(0,v-rate*g)) for v,g in zip(reference,gradients[label]))
                    cpu=cpu_commit(cpu_observe(graph,cpu,cp,label),spec)
                    amp=model_commit(model_observe(graph,amp,ap,label),spec)
                    for path,state in (('reference',reference),('binary64',cpu.theta),('AMP',amp.theta)):
                        learners[path].observe(label)
                        assert tuple(learners[path].theta)==state
                        comparisons+=1
    assert comparisons==936 and 'torch' not in sys.modules
    return {'full_graph_forecast_and_successor_comparisons':comparisons,
        'paths':['exact forward derivatives','independent Python binary64','independent rounded graph AMP'],
        'rates':['1/8','4'],'synthetic_only':True}


if __name__=='__main__':
    import json
    print(json.dumps(reduction_audit(),indent=2))
