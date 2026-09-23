"""Exact native/RNE audit for the passive direct integer partition realization."""
from fractions import Fraction as F
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).parent)]
from fp_reference import indexed_amp as amp
from fp_reference.indexed_count import CountState
from fp_reference.semantics import ArithmeticUnresolved
from integer_partition import prepare, reference, rounded_prediction, precision_bound

from itertools import product
import json
import subprocess
from fp_reference.indexed_count import observe
from fp_reference.indexed_execution import IndexedState
from fp_reference.float64_bridge import Float64Contract
from fp_reference import packed_histogram_decoder as old_owned
sys.path[:0] = [str(ROOT/'experiments/joint_uncertainty'), str(ROOT/'scripts')]
from audit_count_histogram import oracle, state as count_state
import audit_packed_histogram_cuda as previous

class Audit:
    def __init__(self):
        self.predictions = self.observations = self.words = self.half = 0
        self.bound = precision_bound()
        self.maximum = {key:F(0) for key in ('native','normalizer','probability','proper_mass_division','gradient')}

    def check(self, before, query, exact):
        plan = prepare(before,query)
        assert plan.parts == exact
        reference_prediction = reference(plan)
        assert reference_prediction.probabilities == tuple((1+8*F(v,sum(exact)))/10 for v in exact)
        raw, trace = rounded_prediction(plan)
        tolerance = Float64Contract(F(1,100),F(1,1000))
        relation = amp.check_prediction(reference_prediction,raw,tolerance,
            normalizer_cap=F(18),activation_cap=F(8),bit_limit=32768)
        measured = dict(zip(('native','normalizer','probability','proper_mass_division'),
            (relation.native_error,relation.normalizer_error,relation.probability_error,relation.division_error)))
        measured['gradient']=F(0)
        self.predictions += 1
        self.words += len(trace)+7
        self.half += sum(width==16 for _,width,_ in trace)
        for target in (0,1):
            mass=reference_prediction.masses[target]
            expected=IndexedState(observe(before,*query,target),
                (1/mass-F(1,5),F(4,5)-8/mass,F(4,5)))
            arithmetic=amp._Arithmetic(32768)
            actual,_=amp._observation_schedule(amp.IndexedAmpState(before),raw,target,arithmetic)
            relation2=amp.check_state(expected,actual,tolerance,bit_limit=32768)
            assert actual.encoded == expected.encoded
            measured['gradient']=max(measured['gradient'],relation2.state_error)
            self.observations += 1
            self.words += len(arithmetic.trace)+3
        for key,value in measured.items():
            assert value <= self.bound[key], (key,before,query,value,self.bound[key])
            self.maximum[key]=max(self.maximum[key],value)
        return plan

def outward(value):
    scale=10**9
    top=(value.numerator*scale+value.denominator-1)//value.denominator
    return f'{top//scale}.{top%scale:09d}'

def run_audit():
    audit=Audit()
    states=0
    for n in (2,3,4):
        for counts in product((-1,0,1),repeat=n*(n-1)//2):
            before=count_state(n,counts)
            states += 1
            for query in product(range(n),repeat=2):
                audit.check(before,query,oracle(before,query)[1])
    assert states==759 and audit.predictions==11919
    small=audit.predictions
    rows=[]
    for name,before,query in previous.fixtures():
        exact=previous.oracle(before,query)[1]
        plan=audit.check(before,query,exact)
        rows.append({'case':name,'n':before.n,'span':plan.span,'integer_envelope':plan.integer_envelope,
            'maximum_integer_bits':plan.maximum_integer_bits,'floating_outputs':plan.output_cells})
    separation=[]
    for sign in (-1,1):
        n=256
        before=count_state(n,(sign*128,)+(0,)*(n*(n-1)//2-1))
        scale=1 << (n-2)
        exact=(scale*9**128,scale) if sign>0 else (scale,scale*9**128)
        plan=audit.check(before,(0,1),exact)
        try:
            old_owned.passive_plan(before,(0,1))
        except ArithmeticUnresolved:
            status='UNRESOLVED'
        else:
            raise AssertionError('old packed class unexpectedly admitted its excessive envelope')
        separation.append({'n':n,'single_count':sign*128,'query':(0,1),
            'direct_integer_envelope':plan.integer_envelope,'maximum_integer_bits':plan.maximum_integer_bits,
            'packed_integer_envelope':n*129,'same_integer_limit':32768,
            'old_carry_free_status':status,'new_passive_outputs':plan.output_cells})
    dense=count_state(16,(1,)*120)
    try:
        prepare(dense,(0,1))
    except ArithmeticUnresolved:
        dense_status='UNRESOLVED'
    else:
        raise AssertionError('dense geometry obstruction was silently bypassed')
    result={'status':'PASS_DIRECT_INTEGER_PARTITION_CPU',
        'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'scope':'passive exact integer construction and RNE full-coordinate arithmetic; no Runtime admission, owned memory or actual CUDA',
        'construction':'positive base9 variable elimination from complete native counts; half mantissas/single scaling and readout',
        'states':states,'small_ordered_queries':small,
        'predictions':audit.predictions,'both_target_observations':audit.observations,
        'floating_words_including_copies':audit.words,'half_words':audit.half,
        'uniform_bounds_outward':{key:outward(audit.bound[key]) for key in audit.maximum},
        'maximum_errors_exact':{key:str(v) for key,v in audit.maximum.items()},
        'larger_previous_fixtures':rows,'bit_envelope_separation':separation,
        'dense_n16_unchanged_width_refusal':dense_status}
    path=ROOT/'evidence/minimal/FP_DIRECT_INTEGER_PARTITION_CPU.json'
    if path.exists():
        prior=json.loads(path.read_text(encoding='utf-8'))
        assert {k:v for k,v in prior.items() if k!='base_commit'} == json.loads(json.dumps({k:v for k,v in result.items() if k!='base_commit'}))
    else:
        with path.open('x',encoding='utf-8') as stream:
            json.dump(result,stream,indent=2)
            stream.write('\n')
    print(json.dumps({'status':result['status'],'predictions':audit.predictions,
        'observations':audit.observations,'floating_words':audit.words,'half_words':audit.half,
        'bounds':result['uniform_bounds_outward'],'artifact_bytes':path.stat().st_size}),flush=True)

if __name__=='__main__':
    run_audit()
