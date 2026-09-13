"""Independent RN-4 dynamic rescore, conditional baseline and fresh decisions.

No Runtime or GPU worker is executed by this analysis. Failed attempts have
no reconstructed scores or imputed unexecuted tails.
"""
import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json
from math import fsum, isclose, log, prod
from pathlib import Path
from statistics import mean

import run_adaptive as experiment
from adaptive_model import data, counts_from_training, unseen_pairs, tasks
from trajectory_oracle import ScalarLearner, HALF, SINGLE, component_model
from fp_reference.numerics import log_enclosure

SOURCE='cffbadc'
OLD=experiment.previous.rn2_analysis
ROOT=experiment.ROOT
DEPENDENCIES=OLD.ANALYSIS_DEPENDENCIES+(
    'experiments/component_uncertainty/analyze_study.py',
    'experiments/component_uncertainty/study.py',
    'experiments/component_uncertainty/run_study.py',
    'experiments/adaptive_uncertainty/PROTOCOL.md',
    'experiments/adaptive_uncertainty/adaptive_model.py',
    'experiments/adaptive_uncertainty/run_adaptive.py')


def check_score(record, predictions, raw, hidden, pairs):
    ce,raw_ce,gaps=[],[],[]
    low=high=bits=0
    mistakes=F(0)
    for pair in pairs:
        p=predictions[pair][1]
        q=F(9,10) if hidden[pair[0]]^hidden[pair[1]] else F(1,10)
        assert 0<p<1
        ce.append(-float(q)*log(float(p))-float(1-q)*log(float(1-p)))
        if raw is not None:
            raw_ce.append(-float(q)*log(float(raw[pair][1]))-float(1-q)*log(float(raw[pair][0])))
        # Variance plus squared calibration error, independently expanded.
        loss=2*q*(1-q)+2*(p-q)**2
        bits=max(bits,loss.numerator.bit_length(),loss.denominator.bit_length())
        t=loss*2**48
        floor=t.numerator//t.denominator
        low+=floor;high+=floor+int(F(floor)!=t)
        gaps.append(float(abs(p-q)))
        mistakes+=F(1,2) if p==F(1,2) else int((p>F(1,2)) != (q>F(1,2)))
    count=len(pairs)
    assert record['contexts']==count and record['Brier_grid_bits']==48
    assert record['maximum_per_query_Brier_integer_bits']==bits<=32768
    assert tuple(map(F,record['expected_Brier_exact_enclosure']))==(F(low,count*2**48),F(high,count*2**48))
    assert F(record['latent_relation_error_with_half_ties'])==mistakes/count
    assert isclose(record['expected_CE_binary64'],fsum(ce)/count,rel_tol=0,abs_tol=2**-42)
    assert isclose(record['mean_true_probability_gap_binary64'],fsum(gaps)/count,rel_tol=0,abs_tol=2**-42)
    if raw is None:
        assert record['raw_division_expected_CE_binary64'] is None
    else:
        assert isclose(record['raw_division_expected_CE_binary64'],fsum(raw_ce)/count,rel_tol=0,abs_tol=2**-42)


@lru_cache(maxsize=4096)
def log_lower(probability):
    ratio=2*probability
    interval=log_enclosure(ratio,terms=12,bit_limit=32768)
    with localcontext() as c:
        # Grid16 learners can produce near-neutral gains whose exact
        # 12-term enclosure is narrower than 100 decimal digits.
        c.prec=256
        dec=lambda v:Decimal(v.numerator)/Decimal(v.denominator)
        value=dec(ratio).ln()
        assert -3<dec(interval.lower)<=value<=dec(interval.upper)<3
    return interval.lower


def crossing(predictions,evaluation):
    wealth=maximum=F(1)
    signs=Counter()
    for offset,(i,j,label) in enumerate(evaluation):
        gain=log_lower(predictions[i,j][label])
        signs['positive' if gain>0 else 'negative' if gain<0 else 'zero']+=1
        update=wealth*(1+gain/4)
        wealth=F((update.numerator*2**16)//update.denominator,2**16)
        maximum=max(maximum,wealth)
        if wealth>=4:
            break
    return {'first_crossing_fresh_offset':offset+1 if wealth>=4 else None,
        'exact_wealth_at_crossing_or_end':str(wealth),'maximum_exact_wealth':str(maximum),
        'signs_until_crossing_or_end':dict(signs)}


def check_fp(row, hidden, edges, train, evaluation):
    n=row['case'][0]
    assert row['training_events']==len(train) and row['evaluation_events']==n*n
    assert row['resources']['peak_packed_bytes']<=1<<30
    assert row['resources']['consumed_native_arena_extent']<=16<<20
    checked=row['phase_audit_status']=='ALL_EXECUTED_PHASES_CHECKED'
    if checked:
        cuda=row['independent_CUDA']
        assert cuda['phases']==row['independent_binary64_phases']
        assert cuda['actual_arena_bytes']==16<<20
        assert cuda['maximum_output_cells']<=4096 and cuda['largest_phase_frame_used']<=131072
    else:
        assert row['independent_CUDA'] is None and row['independent_binary64_phases'] is None
    complete=row['run_status']=='SEALED_CUDA_STREAM'
    if not complete:
        assert row['run_status']=='HALTED_UNRESOLVED' and row['halted'] is not None
        assert all(row[k] is None for k in ('candidate_stream_unseen','candidate_stream_full_domain','deployed_stream_unseen','deployed_stream_full_domain'))
        return 0,{'retained_halt':row['halted'],'no_imputed_tail':True}
    assert checked and row['halted'] is None and row['cursor']==len(train)+n*n
    counts=counts_from_training(n,train)
    components,h,scale,initial,likelihood=component_model(n,counts)
    candidate=row['native_candidate'] is not None
    upper=prod(F(a,a+b)**a*F(b,a+b)**b for _,_,a,b in counts)
    best=max(F(1,2)**len(train),likelihood if candidate else F(0))
    class_bounded=best==upper
    assert row['reference_proofs']==int(class_bounded)
    assert row['cutoff_search_status']==('REFERENCE_CLASS_BOUNDED' if class_bounded else 'UNRESOLVED')
    for decision in row['final_class_decisions']:
        assert decision['ordinary_cursor']==len(train)
        assert decision['status']==('HISTORICAL_REFERENCE_CLASS_BOUNDED' if class_bounded else 'UNRESOLVED')
        assert decision['has_proof']==class_bounded
        assert decision['grammar']==dict(nodes=2*n+n*n+2,SUMs=n*n+6,PRODUCTs=n*n+4,edges=4*n*n+2*n+12,slots=2+n*(n-1))
    assert len(row['final_class_decisions'])==1
    domain=tuple(product(range(n),repeat=2))
    unseen=unseen_pairs(n,edges)
    uniform={pair:(F(1,2),F(1,2)) for pair in domain}
    exact,amp,raw={},{},{}
    traces=None
    install=None
    if candidate:
        assert row['proposal_status']=='PROPOSED_NATIVE' and row['actually_compared']==1
        assert row['components']==[list(c) for c in components] and row['proposal_assignment']==h
        assert F(row['proposal_scale'])==scale and likelihood>F(1,2)**len(train)
        ref=ScalarLearner(n,counts,row['rate'],'reference')
        device=ScalarLearner(n,counts,row['rate'],'AMP')
        graph=row['native_candidate']
        assert tuple(graph[k] for k in ('nodes','sources','SUMs','PRODUCTs','edges','slots'))==(
            2*n+n*n+2,2*n,2,n*n,4*n*n-sum(len(c)**2 for c in components),len(ref.theta))
        assert F(row['alpha_spent'])==F(1,2)
        for i,j,label in evaluation:
            exact[i,j],_=ref.predict(i,j)
            amp[i,j],raw[i,j]=device.predict(i,j)
            ref.observe(label);device.observe(label)
        traces={path:crossing(pred,evaluation) for path,pred in (('reference',exact),('AMP',amp))}
        offsets=[t['first_crossing_fresh_offset'] for t in traces.values()]
        if all(v is not None for v in offsets):
            install=len(train)+max(offsets)
        check_score(row['candidate_stream_unseen'],amp,raw,hidden,unseen)
        check_score(row['candidate_stream_full_domain'],amp,raw,hidden,domain)
    else:
        assert row['candidate_stream_unseen'] is None and row['candidate_stream_full_domain'] is None
        assert F(row['alpha_spent'])==0
    assert row['install_cursor']==install
    if install is not None:
        assert row['final_policy_stage']=='INSTALLED_CUDA'
    deployed,deployed_raw={},{}
    for offset,(i,j,_) in enumerate(evaluation):
        active=install is not None and len(train)+offset>=install
        deployed[i,j]=amp[i,j] if active else uniform[i,j]
        deployed_raw[i,j]=raw[i,j] if active else uniform[i,j]
    check_score(row['deployed_stream_unseen'],deployed,deployed_raw,hidden,unseen)
    check_score(row['deployed_stream_full_domain'],deployed,deployed_raw,hidden,domain)
    return 2+2*int(candidate),{'recomputed_install_cursor':install,'fresh_trajectory':traces,
        'empirical_component_sizes':list(map(len,components)),
        'incorrect_strict_edge_majorities':sum(a!=b and int(b>a)!=(hidden[i]^hidden[j]) for i,j,a,b in counts),
        'tied_edge_counts':sum(a==b for _,_,a,b in counts)}


def posterior_predictions(n,counts,law,evaluation):
    # Explicit bit tuples and parity-consistency likelihoods. Each reference
    # forecast is normalized from unreduced joint weights before the label.
    family=tuple(product((0,1),repeat=n))
    if law.startswith('iid'):
        weights=[prod(9**(b if h[i]^h[j] else a) for i,j,a,b in counts) for h in family]
    else:
        weights=[int(all((h[i]^h[j])==int(b>a) for i,j,a,b in counts)) for h in family]
    result={}
    maximum_weight_bits=max(w.bit_length() for w in weights)
    maximum_payload_bytes=sum(max(1,(w.bit_length()+7)//8) for w in weights)
    for i,j,label in evaluation:
        likelihood=[9 if h[i]^h[j] else 1 for h in family]
        total=sum(weights)
        probability=F(sum(w*v for w,v in zip(weights,likelihood)),10*total)
        result[i,j]=(1-probability,probability)
        weights=[w*(v if label else 10-v) for w,v in zip(weights,likelihood)]
        maximum_weight_bits=max(maximum_weight_bits,max(w.bit_length() for w in weights))
        maximum_payload_bytes=max(maximum_payload_bytes,sum(max(1,(w.bit_length()+7)//8) for w in weights))
    return result,maximum_weight_bits,maximum_payload_bytes


def check_baseline(row,hidden,edges,train,evaluation):
    n,law,_=row['case']
    counts=counts_from_training(n,train)
    exact,weight_bits,payload=posterior_predictions(n,counts,law,evaluation)
    amp,raw=OLD.encode_posterior(exact)
    unseen=unseen_pairs(n,edges);domain=tuple(product(range(n),repeat=2))
    for subset,pairs in (('unseen',unseen),('full_domain',domain)):
        check_score(row['adaptive_exact_'+subset],exact,None,hidden,pairs)
        check_score(row['adaptive_AMP_'+subset],amp,raw,hidden,pairs)
    assert row['complete_domain_raw_predictions_checked']==n*n
    assert row['maximum_exact_probability_bits']==max(max(p.numerator.bit_length(),p.denominator.bit_length()) for pp in exact.values() for p in pp)
    assert F(row['maximum_AMP_mass_probability_error'])==max(abs(exact[p][y]-amp[p][y]) for p in exact for y in (0,1))
    resources=row['resources']
    assert row['maximum_exact_weight_bits']==weight_bits<=32768
    assert resources['maximum_integer_weight_payload_bytes']==payload<=1<<30
    assert resources['counted_assignment_visits']==(len(counts)+3*len(evaluation))*2**n
    assert resources['counted_assignment_visits']<=10**13
    assert resources['native_tensor_peak_bytes']<=16<<20 and resources['native_allocator_peak_reserved_bytes']<=32<<20
    return 4


def verify(*,partial=False):
    report=json.loads(experiment.OUTPUT.read_text(encoding='utf-8'))
    source=experiment.git('rev-parse',SOURCE)
    assert report['registration_source']==report['final_protocol_source']==source and report['experiment']=='RN-4'
    assert report['protocol_origin']==experiment.git('rev-parse',experiment.PROTOCOL_ORIGIN)
    assert not experiment.git('diff',source,'--',*DEPENDENCIES)
    old,reference=experiment.historical()
    assert report['historical_control']==json.loads(json.dumps(reference))
    workers=report['workers']
    assert [(w['kind'],tuple(w['case']),w['rate']) for w in workers]==list(tasks()[:len(workers)])
    if not partial:
        assert len(workers)==30 and report['status'] in ('COMPLETE_EXECUTION','COMPLETE_WITH_FAILURES')
    device=next(iter(old.values()))['device']
    checks=decisions=0;details=[]
    for row in workers:
        OLD.verify_job(row,source,device)
        if row['worker_status']!='EXECUTED':
            details.append({'case':row['case'],'kind':row['kind'],'rate':row['rate'],'worker_status':row['worker_status']})
            continue
        case=tuple(row['case'])
        hidden,edges,train,evaluation=data(case)
        assert row['counts']==[list(r) for r in counts_from_training(case[0],train)]
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
    summary={'journal_status':report['status'],'attempted_workers':len(workers),
        'executed_workers':len(executed),'sealed_FP':len(sealed),'unresolved_FP':len(fps)-len(sealed),
        'installed_sealed_FP':sum(w['install_cursor'] is not None for w in sealed),
        'independent_dynamic_score_checks':checks,'independent_fresh_decisions':decisions,
        'independent_CUDA_phases':sum(w['independent_CUDA']['phases'] for w in checked),
        'independent_binary64_phases':sum(w['independent_binary64_phases'] for w in checked),
        'adaptive_posterior_GPU_forecasts':sum(w['complete_domain_raw_predictions_checked'] for w in executed if w['kind']=='posterior'),
        'maximum_completed_job_bytes':max((w['completed_job']['peak_job_commit'] for w in workers),default=0)}
    groups=[]
    for n,law in ((8,'disconnected-a'),(8,'disconnected-b'),(8,'iid-c2'),(16,'iid-c2'),(8,'iid-c4'),(16,'iid-c4')):
        selected=[w for w in workers if tuple(w['case'][:2])==(n,law)]
        if not selected:
            continue
        rates={}
        for rate in ('1/8','4'):
            attempts=[w for w in selected if w['kind']=='FP' and w['rate']==rate]
            usable=[w for w in attempts if w.get('run_status')=='SEALED_CUDA_STREAM' and w['worker_status']=='EXECUTED']
            rates[rate]={'attempts':len(attempts),'scored':len(usable),
                'installed':sum(w['install_cursor'] is not None for w in usable),
                **{key:mean(w[key]['expected_CE_binary64'] for w in usable) if usable else None
                   for key in ('candidate_stream_unseen','deployed_stream_unseen','candidate_stream_full_domain','deployed_stream_full_domain')}}
        baselines=[w for w in selected if w['kind']=='posterior' and w['worker_status']=='EXECUTED']
        groups.append({'n':n,'law':law,'FP':rates,'posterior_cases':len(baselines),
            **{key:mean(w[key]['expected_CE_binary64'] for w in baselines) if baselines else None
               for key in ('adaptive_AMP_unseen','adaptive_AMP_full_domain')}})
    summary.update(groups=groups,
        FP_search_status=dict(Counter(w['cutoff_search_status'] for w in fps)),
        unresolved_reasons=dict(Counter(w['halted'][1] for w in fps if w['halted'] is not None)),
        maximum_FP_packed_bytes=max((w['resources']['peak_packed_bytes'] for w in fps),default=0),
        maximum_FP_native_extent=max((w['resources']['consumed_native_arena_extent'] for w in fps),default=0),
        maximum_checked_output_cells=max((w['independent_CUDA']['maximum_output_cells'] for w in checked),default=0),
        maximum_checked_phase_frame=max((w['independent_CUDA']['largest_phase_frame_used'] for w in checked),default=0),
        independently_checked_CUDA_error_maxima={k:float(max((F(w['CUDA_relation_maxima'][k]) for w in checked),default=0))
            for k in ('state_error','native_error','normalizer_error','probability_error','division_error')})
    return report,details,summary


def plot(report,preview=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from math import nan
    from adaptive_model import diagnostic_cases,new_cases
    cases=diagnostic_cases()+new_cases()
    rows={(w['kind'],tuple(w['case']),w['rate']):w for w in report['workers']}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
        'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,1,figsize=(11.6,7.3),sharex=True,sharey=True)
    labels=['known A','known B']+[f'n{n} / c{law[-1]}\nseed{seed}' for n,law,seed in new_cases()]
    highest=log(2)
    for ax,key,title in zip(axes,('candidate_stream_unseen','deployed_stream_unseen'),
            ('Continuously learning candidate','Actual deployed stream, including evidence wait')):
        for rate,color,marker in (('1/8','#1874A8','o'),('4','#CE7430','s')):
            values=[]
            for case in cases:
                row=rows['FP',case,rate]
                values.append(row[key]['expected_CE_binary64'] if row.get(key) is not None else nan)
            highest=max(highest,*[v for v in values if v==v])
            ax.plot(range(len(cases)),values,color=color,marker=marker,markersize=5,label='FP rate '+rate)
        values=[rows['posterior',case,'none']['adaptive_AMP_unseen']['expected_CE_binary64'] for case in cases]
        ax.plot(range(len(cases)),values,color='#247B58',marker='D',markersize=4,label='Adaptive AMP posterior')
        ax.axhline(log(2),color='#888888',linestyle=':',linewidth=1)
        ax.axhline(-.9*log(.9)-.1*log(.1),color='#aaaaaa',linestyle='--',linewidth=1)
        for at,case in enumerate(cases):
            if all(rows['FP',case,rate].get(key) is None for rate in ('1/8','4')):
                ax.axvspan(at-.42,at+.42,color='#dddddd',alpha=.35)
                ax.text(at,.79,'FP\nunresolved',ha='center',va='center',fontsize=8,color='#555555')
        ax.set_title(title,loc='left',pad=10)
        ax.set_ylabel('Expected unseen CE')
        ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    axes[0].legend(loc='upper left',ncol=3,frameon=False,fontsize=9)
    axes[0].set_ylim(.29,max(.86,highest+.10))
    axes[1].set_xticks(range(len(cases)),labels)
    fig.suptitle('Native uncertainty learns; execution remains a measured constraint',
        x=.075,ha='left',fontsize=13,y=.985)
    fig.text(.075,.022,'RN-4 / RTX 3090 / source '+SOURCE+
        '   |   every registered case retained; missing FP scores have no imputed tail.\n'
        'Dotted: uniform. Dashed: known-noise floor. Posterior uses the same revealed labels before each forecast. Fixed tapes imply no population rate.',
        fontsize=8.5,color='#444444')
    fig.tight_layout(rect=(.025,.09,.995,.955),h_pad=2.2)
    output=Path(__file__).with_name('adaptive_uncertainty.svg')
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
