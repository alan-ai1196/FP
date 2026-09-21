"""A conditional RNE interpreter does not bind a helper's operand addresses.

This passive counterexample changes no numerical answer supplied to CUDA.
The source-bound actual worker lives in audit_indexed_amp.py.
"""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/reference_compiler'))
from fp_reference import indexed_amp as amp
from fp_reference.core import ContractError
from fp_reference.float64_bridge import Float64Contract
from fp_reference.indexed_count import CountState
from fp_reference.indexed_execution import IndexedState, IndexedReferenceMachine
from fp_reference.indexed_relation import IndexedRelation, DecodeAllowance


def raw_operations(arithmetic):
    return tuple(('host-RNE32-ingress' if tag == 'constant' else
        'cast-float'+str(width) if tag == 'cast' else tag,width,(word,))
        for tag,width,word in arithmetic.trace)


def evaluate_plan(plan,state):
    arithmetic = amp._Arithmetic(32768)
    raw,_ = amp.execute_prediction(plan,state,arithmetic)
    return raw,raw_operations(arithmetic)


def audit():
    schema = IndexedRelation(3)
    count = CountState(3,(0,0,1),None,1,1)
    state = amp.IndexedAmpState(count)
    sources = schema.source_row(1)
    plan = amp.prepare_prediction(schema,state,schema.rules(),sources,output_cap=65536)
    assert plan.support == ((1,2),) and plan.positions == (2,)
    altered = replace(plan,positions=(0,))
    honest,expected = evaluate_plan(plan,state)
    actual,operations = evaluate_plan(altered,state)
    assert actual.words == honest.words and expected != operations
    checked = amp.check_prediction_execution(altered,state,actual,operations,bit_limit=32768)
    try:
        amp.check_prediction_execution(plan,state,actual,operations,bit_limit=32768)
    except ContractError as error:
        original_refusal = str(error)
    else:
        raise AssertionError('the declared factor-address trace unexpectedly matched')
    machine = IndexedReferenceMachine(3,DecodeAllowance())
    reference_plan = machine.prepare_prediction(schema,schema.rules(),IndexedState(count),sources,bit_limit=32768)
    machine.prediction_execution_work(reference_plan)
    reference = machine.execute_prediction(reference_plan)
    relation = amp.check_prediction(reference,actual,Float64Contract(F(0),F(0)),
        normalizer_cap=F(10),activation_cap=F(8),bit_limit=32768)
    assert relation.state_error == relation.probability_error == relation.division_error == 0
    difference = next((k,a,b) for k,(a,b) in enumerate(zip(expected,operations)) if a != b)
    return {'status':'PASS_PASSIVE_PLAN_BINDING_COUNTEREXAMPLE',
        'scope':'conditional interpreter accepts a different factor-address plan with an identical complete readout; actual owned acceptance is a separate audit',
        'native_vertices':3,'reachable_prefix':[[1,2,0]],'current_query':[0,1],
        'complete_counts':list(count.counts),'declared_support':[list(e) for e in plan.support],
        'declared_factor_positions':list(plan.positions),'substituted_factor_positions':list(altered.positions),
        'unchanged_complete_readout_words':list(actual.words),'native_probability':'1/2',
        'native_state_error':str(relation.state_error),'native_probability_error':str(relation.probability_error),
        'native_division_error':str(relation.division_error),'conditional_operations_checked':checked,
        'output_cells':plan.output_cells,'first_operation_difference':difference,
        'declared_plan_refusal':original_refusal,
        'false_statistical_or_class_complete_certificate':'NOT_CLAIMED'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_INDEXED_AMP_PLAN_BINDING.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
