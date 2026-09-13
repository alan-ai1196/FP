"""Independent RN-5 forecast/decision reconstruction; never runs a target worker."""
import argparse
from collections import Counter
from decimal import Decimal,localcontext
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json
from math import log,prod
from pathlib import Path
from statistics import mean

import run_joint as experiment
from joint_model import data,counts_from_training,unseen_pairs,tasks,cases,diagnostic_cases,RATES,STRESS
from joint_trajectory import JointLearner,component_model
from analyze_adaptive import check_score,check_baseline,DEPENDENCIES as PRIOR_DEPENDENCIES
from fp_reference.numerics import log_enclosure

SOURCE='38b27b3'
ROOT=experiment.ROOT
DEPENDENCIES=PRIOR_DEPENDENCIES+(
    'experiments/joint_uncertainty/PROTOCOL.md',
    'experiments/joint_uncertainty/joint_model.py',
    'experiments/joint_uncertainty/run_joint.py')


@lru_cache(maxsize=4096)
def log_lower(probability):
    ratio=2*probability
    interval=log_enclosure(ratio,terms=12,bit_limit=32768)
    with localcontext() as ctx:
        # Grid16 quadratic masses can make a nonzero near-neutral gain's
        # 12-term enclosure narrower than 256 decimal digits. This is only
        # an independent post-analysis check, not the worker's arithmetic.
        ctx.prec=512
        dec=lambda v:Decimal(v.numerator)/Decimal(v.denominator)
        value=dec(ratio).ln()
        assert -6<dec(interval.lower)<=value<=dec(interval.upper)<6
    return interval.lower


def crossing(predictions,evaluation):
    wealth=maximum=F(1)
    signs=Counter()
    for offset,(i,j,label) in enumerate(evaluation):
        gain=log_lower(predictions[i,j][label])
        signs['positive' if gain>0 else 'negative' if gain<0 else 'zero']+=1
        update=wealth*(1+gain/8)
        wealth=F((update.numerator*65536)//update.denominator,65536)
        maximum=max(maximum,wealth)
        if wealth>=4:
            break
    return {'first_crossing_fresh_offset':offset+1 if wealth>=4 else None,
        'exact_wealth_at_crossing_or_end':str(wealth),'maximum_exact_wealth':str(maximum),
        'signs_until_crossing_or_end':dict(signs)}


def verify_job(row,source,device):
    assert row['execution_source']==source
    job=row['completed_job']
    assert job['commit_limit']==experiment.HOST_CAP and job['attached_before_resume']
    if row['worker_status']!='EXECUTED':
        return
    assert row['device']==device and job['exit_code']==0 and not job['timed_out']
    assert job['limit_terminated_processes']==0
    assert max(job['peak_process_commit'],job['peak_job_commit'])<=experiment.HOST_CAP
    if row['kind']=='FP':
        host=row['host']
        assert (host['process_id'],host['creation_100ns'])==(job['process_id'],job['process_creation_100ns'])
        assert host['lifetime_process_commit_peak']<=job['peak_process_commit']
    else:
        assert row['process_id']==job['process_id']


def worker_failure(row):
    for key in ('reason','validation_error','traceback'):
        if row.get(key):
            return row[key].strip().splitlines()[-1]
    return 'failed without a reported reason'


def sign_bounds(components,h,hidden):
    entropy=lambda q:-float(q)*log(float(q))-float(1-q)*log(float(1-q))
    residual=[(sum((h[i]^hidden[i])==0 for i in group),sum((h[i]^hidden[i])==1 for i in group)) for group in components]
    n=len(h);W=sum((a+b)**2 for a,b in residual);L=sum(a*a+b*b for a,b in residual)
    inside=F(1,10)+F(4,5)*F(L,W)
    fixed=W*entropy(inside)
    for k,(a,b) in enumerate(residual):
        for l,(c,d) in enumerate(residual):
            if k!=l:
                m=(a+b)*(c+d)
                fixed+=m*entropy(F(1,10)+F(4,5)*F(a*c+b*d,m))
    wrong=2*sum(a*b for a,b in residual)
    sequential=entropy(F(1,10))+wrong/n**2*(log(2)-entropy(F(1,10)))
    return {'residual_sign_counts':residual,'wrong_ordered_internal_pairs':wrong,
        'prequential_expected_CE_lower_binary64':sequential,
        'fixed_state_uniform_risk_lower_binary64':fixed/n**2,
        'fixed_state_bound_is_not_a_prequential_bound':True}


def check_fp(row,hidden,edges,train,evaluation):
    n=row['case'][0]
    assert row['training_events']==len(train) and row['evaluation_events']==n*n
    assert row['resources']['peak_packed_bytes']<=experiment.PACKED_CAP
    assert row['resources']['consumed_native_arena_extent']<=experiment.ARENA
    checked=row['phase_audit_status']=='ALL_EXECUTED_PHASES_CHECKED'
    if checked:
        cuda=row['independent_CUDA']
        assert cuda['phases']==row['independent_binary64_phases']
        assert cuda['actual_arena_bytes']==experiment.ARENA
        assert cuda['maximum_output_cells']<=experiment.CELLS and cuda['largest_phase_frame_used']<=experiment.FRAME
    else:
        assert row['independent_CUDA'] is None and row['independent_binary64_phases'] is None
    if row['run_status']!='SEALED_CUDA_STREAM':
        assert row['run_status']=='HALTED_UNRESOLVED' and row['halted'] is not None
        assert all(row[k] is None for k in ('candidate_stream_unseen','candidate_stream_full_domain','deployed_stream_unseen','deployed_stream_full_domain'))
        return 0,{'retained_halt':row['halted'],'no_imputed_tail':True}
    assert checked and row['halted'] is None and row['cursor']==len(train)+n*n
    counts=counts_from_training(n,train)
    components,h,scale,initial,likelihood=component_model(n,counts)
    candidate=row['native_candidate'] is not None
    upper=prod(F(a,a+b)**a*F(b,a+b)**b for _,_,a,b in counts)
    best=max(F(1,2)**len(train),likelihood if candidate else F(0))
    bounded=best==upper
    assert row['reference_proofs']==int(bounded)
    assert row['cutoff_search_status']==('REFERENCE_CLASS_BOUNDED' if bounded else 'UNRESOLVED')
    for decision in row['final_class_decisions']:
        assert decision['ordinary_cursor']==len(train)
        assert decision['status']==('HISTORICAL_REFERENCE_CLASS_BOUNDED' if bounded else 'UNRESOLVED')
        assert decision['has_proof']==bounded
        assert decision['grammar']==dict(nodes=2*n+n*n+18,SUMs=n*n+18,PRODUCTs=n*n+4,edges=18*n*n+16,slots=2+n*(n-1))
    assert len(row['final_class_decisions'])==1
    domain=tuple(product(range(n),repeat=2));unseen=unseen_pairs(n,edges)
    exact,amp,raw={},{},{}
    traces=None;install=None;obstruction=None;scale_dynamics=None
    if candidate:
        assert row['proposal_status']=='PROPOSED_NATIVE' and row['actually_compared']==1
        assert row['components']==[list(c) for c in components] and row['proposal_assignment']==h
        assert F(row['proposal_scale'])==scale and likelihood>F(1,2)**len(train)
        ref=JointLearner(n,counts,row['rate'],'reference')
        device=JointLearner(n,counts,row['rate'],'AMP')
        K=len(ref.members);W=sum(len(c)**2 for c in components)
        nonempty=sum(len({member[i]^member[j] for i,j in domain if ref.component_of[i]!=ref.component_of[j]}) for member in ref.members)
        graph=row['native_candidate']
        assert tuple(graph[k] for k in ('nodes','sources','SUMs','PRODUCTs','edges','slots'))==(
            2*n+n*n+nonempty+2,2*n,nonempty+2,n*n,2*n*n+2*K*(n*n-W)+nonempty+W,len(ref.theta))
        assert F(row['alpha_spent'])==F(1,2)
        mass=lambda:2+sum(ref.theta[k]+ref.theta[k]**2 for k in ref.slots)
        initial_mass=mass();changes=[];amp_normalizers=[]
        for i,j,label in evaluation:
            before_mass=mass()
            exact[i,j],_=ref.predict(i,j)
            amp[i,j],raw[i,j]=device.predict(i,j)
            if ref.component_of[i]==ref.component_of[j] and (h[i]^h[j])!=(hidden[i]^hidden[j]):
                assert exact[i,j][hidden[i]^hidden[j]]<=F(1,2)
                assert amp[i,j][hidden[i]^hidden[j]]<=F(1,2)
            is_cross=ref.component_of[i]!=ref.component_of[j]
            if is_cross:
                amp_normalizers.append(F(device.pending[4]))
            ref.observe(label);device.observe(label)
            if is_cross:
                changes.append(mass()-before_mass)
            else:
                assert mass()==before_mass
        scale_dynamics={'scope':'post hoc descriptive grid16 scale trace, not an unrounded/AMP monotonicity theorem',
            'orientation_members':K,'cross_updates':len(changes),
            'initial_reference_cross_polynomial_mass':str(initial_mass),
            'final_reference_cross_polynomial_mass':str(mass()),
            'reference_cross_mass_increases':sum(v>0 for v in changes),
            'reference_cross_mass_decreases':sum(v<0 for v in changes),
            'reference_cross_mass_unchanged':sum(v==0 for v in changes),
            'minimum_reference_cross_mass_change':str(min(changes)) if changes else None,
            'maximum_actual_AMP_cross_forward_normalizer':str(max(amp_normalizers)) if amp_normalizers else None}
        traces={path:crossing(pred,evaluation) for path,pred in (('reference',exact),('AMP',amp))}
        offsets=[t['first_crossing_fresh_offset'] for t in traces.values()]
        if all(v is not None for v in offsets):
            install=len(train)+max(offsets)
        check_score(row['candidate_stream_unseen'],amp,raw,hidden,unseen)
        check_score(row['candidate_stream_full_domain'],amp,raw,hidden,domain)
        obstruction=sign_bounds(components,h,hidden)
        assert row['candidate_stream_full_domain']['expected_CE_binary64']+2**-42>=obstruction['prequential_expected_CE_lower_binary64']
    else:
        assert row['candidate_stream_unseen'] is None and row['candidate_stream_full_domain'] is None
        assert F(row['alpha_spent'])==0
    assert row['install_cursor']==install,(row['case'],row['rate'],row['install_cursor'],install,traces)
    if install is not None:
        assert row['final_policy_stage']=='INSTALLED_CUDA'
    deployed,deployed_raw={},{}
    for offset,(i,j,_) in enumerate(evaluation):
        active=install is not None and len(train)+offset>=install
        deployed[i,j]=amp[i,j] if active else (F(1,2),F(1,2))
        deployed_raw[i,j]=raw[i,j] if active else (F(1,2),F(1,2))
    check_score(row['deployed_stream_unseen'],deployed,deployed_raw,hidden,unseen)
    check_score(row['deployed_stream_full_domain'],deployed,deployed_raw,hidden,domain)
    return 2+2*int(candidate),{'recomputed_install_cursor':install,'fresh_trajectory':traces,
        'empirical_component_sizes':list(map(len,components)),
        'incorrect_strict_edge_majorities':sum(a!=b and int(b>a)!=(hidden[i]^hidden[j]) for i,j,a,b in counts),
        'tied_edge_counts':sum(a==b for _,_,a,b in counts),'sign_obstruction':obstruction,
        'scale_dynamics':scale_dynamics}


def verify(*,partial=False):
    report=json.loads(experiment.OUTPUT.read_text(encoding='utf-8'))
    source=experiment.git('rev-parse',SOURCE)
    assert report['registration_source']==report['final_protocol_source']==source
    assert report['protocol_origin']==experiment.git('rev-parse','e3df252')
    assert report['prior_auditor_failures']==experiment.prior_failure()
    assert report['experiment']=='RN-5'
    assert not experiment.git('diff',source,'--',*DEPENDENCIES)
    old,references=experiment.historical()
    assert report['historical_control']==json.loads(json.dumps(references))
    workers=report['workers']
    assert [(w['kind'],tuple(w['case']),w['rate']) for w in workers]==list(tasks()[:len(workers)])
    if not partial:
        assert len(workers)==31 and report['status'] in ('COMPLETE_EXECUTION','COMPLETE_WITH_FAILURES')
    device=next(iter(old.values()))['device']
    checks=decisions=0;details=[]
    for row in workers:
        verify_job(row,source,device)
        if row['worker_status']!='EXECUTED':
            details.append({'case':row['case'],'kind':row['kind'],'rate':row['rate'],
                'worker_status':row['worker_status'],'retained_worker_failure':worker_failure(row),
                'no_imputed_tail':True})
            continue
        hidden,edges,train,evaluation=data(tuple(row['case']))
        assert row['counts']==[list(r) for r in counts_from_training(row['case'][0],train)]
        if row['kind']=='FP':
            count,detail=check_fp(row,hidden,edges,train,evaluation)
            checks+=count;decisions+=row['run_status']=='SEALED_CUDA_STREAM' and row['native_candidate'] is not None
        else:
            checks+=check_baseline(row,hidden,edges,train,evaluation);detail={}
        details.append({'case':row['case'],'kind':row['kind'],'rate':row['rate'],**detail})
    executed=[w for w in workers if w['worker_status']=='EXECUTED']
    fps=[w for w in executed if w['kind']=='FP']
    sealed=[w for w in fps if w['run_status']=='SEALED_CUDA_STREAM']
    checked=[w for w in fps if w['phase_audit_status']=='ALL_EXECUTED_PHASES_CHECKED']
    summary={'journal_status':report['status'],'attempted_workers':len(workers),'executed_workers':len(executed),
        'failed_workers':len(workers)-len(executed),
        'failed_worker_reasons':dict(Counter(worker_failure(w) for w in workers if w['worker_status']!='EXECUTED')),
        'sealed_FP':len(sealed),'unresolved_FP':len(fps)-len(sealed),
        'installed_sealed_FP':sum(w['install_cursor'] is not None for w in sealed),
        'independent_dynamic_score_checks':checks,'independent_fresh_decisions':decisions,
        'independent_CUDA_phases':sum(w['independent_CUDA']['phases'] for w in checked),
        'independent_binary64_phases':sum(w['independent_binary64_phases'] for w in checked),
        'new_adaptive_posterior_GPU_forecasts':sum(w['complete_domain_raw_predictions_checked'] for w in executed if w['kind']=='posterior'),
        'maximum_completed_job_bytes':max((w['completed_job']['peak_job_commit'] for w in workers),default=0),
        'prior_auditor_failures':report['prior_auditor_failures']}
    groups=[]
    for n,law in ((8,'disconnected-a'),(8,'disconnected-b'),(8,'iid-c2'),(16,'iid-c2'),(8,'iid-c4'),(16,'iid-c4'),STRESS[:2]):
        selected=[w for w in workers if tuple(w['case'][:2])==(n,law)]
        if not selected:
            continue
        rates={}
        for rate in RATES:
            attempts=[w for w in selected if w['kind']=='FP' and w['rate']==rate]
            usable=[w for w in attempts if w.get('run_status')=='SEALED_CUDA_STREAM' and w['worker_status']=='EXECUTED']
            rates[rate]={'attempts':len(attempts),'sealed':len(usable),
                'installed':sum(w['install_cursor'] is not None for w in usable)}
            for key in ('candidate_stream_unseen','deployed_stream_unseen','candidate_stream_full_domain','deployed_stream_full_domain'):
                values=[w[key]['expected_CE_binary64'] for w in usable if w.get(key) is not None]
                rates[rate][key]=mean(values) if values else None
                rates[rate][key+'_scored_cases']=len(values)
        baselines=[w for w in selected if w['kind']=='posterior' and w['worker_status']=='EXECUTED']
        if law.startswith('disconnected'):
            baselines=[old['posterior',(n,law,0),'none']]
        groups.append({'n':n,'law':law,'FP':rates,'posterior_cases':len(baselines),
            'posterior_reused_from_RN4':law.startswith('disconnected'),
            **{key:mean(w[key]['expected_CE_binary64'] for w in baselines) if baselines else None
               for key in ('adaptive_AMP_unseen','adaptive_AMP_full_domain')}})
    summary.update(groups=groups,FP_search_status=dict(Counter(w['cutoff_search_status'] for w in fps)),
        unresolved_reasons=dict(Counter(w['halted'][1] for w in fps if w['halted'] is not None)),
        maximum_FP_packed_bytes=max((w['resources']['peak_packed_bytes'] for w in fps),default=0),
        maximum_FP_native_extent=max((w['resources']['consumed_native_arena_extent'] for w in fps),default=0),
        maximum_checked_output_cells=max((w['independent_CUDA']['maximum_output_cells'] for w in checked),default=0),
        maximum_checked_phase_frame=max((w['independent_CUDA']['largest_phase_frame_used'] for w in checked),default=0),
        independently_checked_CUDA_error_maxima={key:float(max((F(w['CUDA_relation_maxima'][key]) for w in checked),default=0))
            for key in ('state_error','native_error','normalizer_error','probability_error','division_error')})
    return report,details,summary


def plot_score(row,key):
    # A failed job may retain scores from an otherwise completed worker.
    # Those values have no accepted full execution and must stay unavailable.
    if row.get('worker_status')!='EXECUTED':
        return None
    if row['kind']=='FP' and row.get('run_status')!='SEALED_CUDA_STREAM':
        return None
    return row[key]['expected_CE_binary64'] if row.get(key) is not None else None


def plot(report,preview=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from math import nan
    matrix=cases()
    rows={(w['kind'],tuple(w['case']),w['rate']):w for w in report['workers']}
    old,_=experiment.historical()
    rows.update({key:row for key,row in old.items() if key[0]=='posterior'})
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
        'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,1,figsize=(12.6,7.5),sharex=True,sharey=True)
    labels=['known A','known B']+[f'n{n} / c{law[-1]}\nseed {seed}' for n,law,seed in matrix[2:-1]]+['selected\nwrong sign']
    highest=log(2)
    for ax,key,title in zip(axes,('candidate_stream_unseen','deployed_stream_unseen'),
            ('Continuously learning candidate','Actual deployed stream, including evidence wait')):
        for rate,color,marker in (('1','#1874A8','o'),('4','#CE7430','s')):
            values=[]
            for case in matrix:
                row=rows['FP',case,rate]
                value=plot_score(row,key)
                values.append(value if value is not None else nan)
            highest=max(highest,*[v for v in values if v==v])
            ax.plot(range(len(matrix)),values,color=color,marker=marker,markersize=5,label='FP rate '+rate)
        values=[]
        for case in matrix:
            row=rows['posterior',case,'none']
            value=plot_score(row,'adaptive_AMP_unseen')
            values.append(value if value is not None else nan)
        ax.plot(range(len(matrix)),values,color='#247B58',marker='D',markersize=4,label='Adaptive AMP posterior')
        ax.axhline(log(2),color='#888888',linestyle=':',linewidth=1)
        ax.axhline(-.9*log(.9)-.1*log(.1),color='#aaaaaa',linestyle='--',linewidth=1)
        for at,case in enumerate(matrix):
            if all(plot_score(rows['FP',case,rate],key) is None for rate in RATES):
                ax.axvspan(at-.42,at+.42,color='#dddddd',alpha=.35)
                ax.text(at,log(2)+.03,'FP unavailable',ha='center',va='bottom',fontsize=8,color='#555555',rotation=90)
        ax.set_title(title,loc='left',pad=10)
        ax.set_ylabel('Expected unseen CE')
        ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    axes[0].legend(loc='upper left',ncol=3,frameon=False,fontsize=9)
    axes[0].set_ylim(.29,max(.85,highest+.12))
    axes[1].set_xticks(range(len(matrix)),labels,fontsize=9)
    fig.suptitle('Joint native uncertainty: candidate quality and deployment delay',
        x=.07,ha='left',fontsize=13,y=.985)
    fig.text(.07,.025,'RN-5 / RTX 3090 / source '+SOURCE+
        '   |   unavailable scores have no imputed tail; prior auditor failures remain separate.\n'
        'Dotted: uniform. Dashed: known-noise floor. Same revealed labels at each forecast. The selected stress tape is not an IID population sample.',
        fontsize=8.3,color='#444444')
    fig.tight_layout(rect=(.02,.09,.995,.955),h_pad=2.2)
    output=Path(__file__).with_name('joint_uncertainty.svg')
    fig.savefig(output)
    output.write_text('\n'.join(line.rstrip() for line in output.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    if preview:
        fig.savefig(preview,dpi=150)
    plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--partial',action='store_true')
    parser.add_argument('--details',action='store_true')
    parser.add_argument('--plot',action='store_true')
    parser.add_argument('--preview')
    args=parser.parse_args()
    assert not (args.partial and (args.plot or args.preview))
    assert args.plot or args.preview is None
    report,details,summary=verify(partial=args.partial)
    if args.plot:
        plot(report,args.preview)
    print(json.dumps({'summary':summary,**({'details':details} if args.details else {})},indent=2))
