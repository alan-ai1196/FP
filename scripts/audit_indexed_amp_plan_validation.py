"""Complete typed AMP plan binding, independently of the returned helper plan."""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'scripts')]
from fp_reference import indexed_amp as amp
from fp_reference.indexed_count import CountState
from fp_reference.indexed_relation import IndexedRelation
from fp_reference.semantics import ArithmeticUnresolved
from audit_reference_construction import rejects


def audit():
    changed_fields = clones = typed = extras = budgets = 0
    fields = set()
    cases = ((2,(0,),(0,1)),(3,(0,0,1),(0,1)),
             (5,(0,0,0,0,1,0,0,0,0,-1),(2,4)))
    for n,values,query in cases:
        schema = IndexedRelation(n)
        height = sum(map(abs,values))
        state = amp.IndexedAmpState(CountState(n,values,None,height,height))
        rules,sources = schema.rules(),schema.source_row(query[0]*n+query[1])
        plan = amp.prepare_prediction(schema,state,rules,sources,output_cap=65536)
        def validate(value,cap=65536):
            return amp.check_prediction_plan(value,schema,state,rules,sources,output_cap=cap)
        def forbidden(*args,**kwargs):
            raise AssertionError('validation used the replaceable preparation helper')
        with patch.object(amp,'prepare_prediction',forbidden):
            validate(replace(plan))
            clones += 1
            changes = {
                'n':n+1,'query':query[::-1],
                'support':((0,1),) if not plan.support else ((1,0),)+plan.support[1:],
                'positions':(0,) if not plan.positions else (plan.positions[0]+1,)+plan.positions[1:],
                'nodes':plan.nodes[:2]+(('one',),)+plan.nodes[3:],
                'partitions':plan.partitions[::-1],
                'power_tags':(not plan.power_tags[0],)+plan.power_tags[1:],
                'table_shape':tuple((key,value+1 if k == 0 else value) for k,(key,value) in enumerate(plan.table_shape)),
                'output_cells':plan.output_cells+1}
            assert set(changes) == set(vars(plan))
            for name,value in changes.items():
                rejects(lambda: validate(replace(plan,**{name:value})))
                changed_fields += 1
                fields.add(name)
            for change in ({'n':float(n)},{'query':tuple(F(v) for v in query)},
                           {'power_tags':tuple(int(v) for v in plan.power_tags)},
                           {'positions':list(plan.positions)}):
                rejects(lambda: validate(replace(plan,**change)))
                typed += 1
            extra = replace(plan)
            object.__setattr__(extra,'undeclared_operand',(0,))
            rejects(lambda: validate(extra))
            extras += 1
            rejects(lambda: validate(plan,plan.output_cells-1),ArithmeticUnresolved)
            budgets += 1
    # Same-support plans can validly serve different count magnitudes. The
    # current input is checked again, and execution reads its current counts;
    # no gratuitous historical identity token is required for an equal plan.
    schema = IndexedRelation(3)
    a = amp.IndexedAmpState(CountState(3,(0,0,1),None,1,1))
    b = amp.IndexedAmpState(CountState(3,(0,0,2),None,2,2))
    plan = amp.prepare_prediction(schema,a,schema.rules(),schema.source_row(1),output_cap=65536)
    amp.check_prediction_plan(plan,schema,b,schema.rules(),schema.source_row(1),output_cap=65536)
    return {'status':'PASS_COMPLETE_AMP_PLAN_BINDING','complete_fields':sorted(fields),
        'valid_independent_reconstructions':clones,'individual_field_substitutions_refused':changed_fields,
        'equality_coercion_or_mutable_container_substitutions_refused':typed,
        'undeclared_field_substitutions_refused':extras,'insufficient_current_output_allowance_refused':budgets,
        'equal_plan_under_distinct_current_counts_validated':True,
        'replacement_helper_calls_during_validation':0,
        'scope':'complete typed registered plan relation; no numerical answer or ownership authority from the helper'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_INDEXED_AMP_PLAN_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
