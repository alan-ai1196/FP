"""A paid proposal of native delayed syntax, never a posterior-state API.

Data gives descriptive likelihood guidance among actual initializer slots.
The ordinary constructor/profile path must create every value and state;
the existing empirical upper is the only bounded class-completion route.
"""
from dataclasses import dataclass,field
from fractions import Fraction as F
from functools import cmp_to_key

from .core import ContractError
from .data_usage import DataContract
from .empirical_bound import EmpiricalUpper
from .learner import LearnerSpec
from .native_search import GrammarLimits
from .numerics import compare_exact
from .profile import ProfileSpec
from .program import Binding,Product,Program,Source,State,Sum,Term
from .relation_proposal import RelationProposal,RelationSourceSpec
from .semantics import _guard,_operation

SOLVER='causal-binary-relation-window-posterior-v6'


@dataclass(frozen=True)
class CausalRelationProposal(RelationProposal):
    window: int = 0
    noise_slot: int | None = None
    guidance: tuple = ()
    state_assignment: tuple = ()
    causal_sources: tuple = ()
    scope: str = field(default='one native finite-window proposal under a fair latent-bit model; descriptive full-history noise guidance, not the empirical class objective or noise/population identification; no supplied learner state',init=False)


def proposal_work_bound(n,source_count,state_count,domain_count,grammar,pattern_count,observations,ordinary_cursor):
    """Conservative bounded scans, arithmetic and graph emission allowance.

    K is refused before expansion when it exceeds grammar.nodes. The loops
    below visit at most that many worlds, state_count stages/coordinates,
    pattern_count noise slots and observations likelihood factors per world.
    Constructor, actual profile, comparison and retained objects pay separately.
    """
    slots=min(pattern_count,grammar.slots)
    return 256*(1+source_count+ordinary_cursor+domain_count*(4*n+2)+state_count**2+
        grammar.nodes*(n*n+state_count+observations+1))*(slots+1)


def literal_counts(n,K,H,zero_types,slots):
    return {'nodes':4*n+2+zero_types+5+4*n*n+K*(4*H+5),
        'SUMs':zero_types+6+K*(2*H+4),'PRODUCTs':4*n*n+K*H+2*K-1,
        'edges':n+2*K*n*n+6*K*H+10*K+8*n*n+1,'slots':slots}


def causal_relation_proposal(upper,rules,grammar,pattern,registration,*,data,learner,
        source_domain,range_cap,profile,ordinary_cursor,bit_limit):
    if type(upper) is not EmpiricalUpper or type(registration) is not RelationSourceSpec or type(grammar) is not GrammarLimits:
        raise ContractError('registered causal relation sources and verified empirical data required')
    edges={};guidance=[];alignment=();selected=None
    def outcome(program=None,reason='',window=0,noise_slot=None,assignments=()):
        return CausalRelationProposal('PROPOSED_NATIVE' if program is not None else 'UNRESOLVED',
            tuple((i,j,c[0],c[1]) for (i,j),c in sorted(edges.items())),(),(),
            None if noise_slot is None else pattern[noise_slot],program,reason,
            window,noise_slot,tuple(guidance),tuple(assignments),alignment)
    if registration.solver!=SOLVER:
        return outcome(reason='wrong causal proposal registration')
    if rules.base!=(F(1),F(1)) or type(data) is not DataContract or type(learner) is not LearnerSpec:
        return outcome(reason='this causal emitter requires its base-one binary data/learner interface')
    if learner.learning_rate!=0:
        return outcome(reason='this initialized-noise posterior emitter requires the registered zero-rate learner')
    dtype=rules.readout_type
    zero_types=tuple(dict.fromkeys((dtype,)+tuple(s.type_id for s in rules.states)))
    if any(t not in rules.sum_types for t in zero_types) or (dtype,dtype,dtype) not in rules.product_rules:
        return outcome(reason='legal positive operations and zero bodies are missing from the registered types')
    atoms=registration.token_atoms;n=len(atoms)
    if n-1>=max(1,grammar.nodes).bit_length():
        return outcome(reason='even one node per latent orientation exceeds this emission budget; the native class remains unsearched')
    K=1<<(n-1)
    _guard(F(K),range_cap,bit_limit=bit_limit)
    available=pattern[:grammar.slots]
    if F(1) not in available:
        return outcome(reason='an actual initialized unit is required to construct constants and state transitions')
    unit=available.index(F(1))
    specs={s.source_id:s for s in rules.sources}
    reads={r.source_id:r for r in data.source_reads}
    by_read={}
    for read in data.source_reads:
        by_read.setdefault((read.kind,read.index,read.lag),[]).append(read.source_id)
    now=tuple(atom for side in (0,1) for pair in atoms for atom in (pair[side],))
    if any(a not in reads or reads[a].kind!='input' or reads[a].lag!=0 for a in now):
        return outcome(reason='the two token roles must be actual current input coordinates')
    if len({reads[a].index for a in now})!=2*n:
        return outcome(reason='the token roles alias ordinary input coordinates')
    old=[]
    for atom in now:
        choices=by_read.get(('input',reads[atom].index,1),())
        if not choices:
            return outcome(reason='a required previous token coordinate is absent from the information interface')
        old.append(choices[0])
    targets=[]
    for y in (0,1):
        choices=by_read.get(('target_atom',y,1),())
        if not choices:
            return outcome(reason='both previous target atoms must be registered causal sources')
        targets.append(choices[0])
    alignment=(now,tuple(old),tuple(targets))
    used=now+tuple(old)+tuple(targets)
    if len(set(used))!=4*n+2 or any(specs[a].type_id!=dtype for a in used):
        return outcome(reason='the causal token/target atoms need distinct compatible source coordinates')
    if not source_domain:
        return outcome(reason='this emitter needs a declared categorical source domain for its unit and match indicators')
    indices={s.source_id:i for i,s in enumerate(rules.sources)}
    for point in source_domain:
        current=tuple(point[indices[a]] for a in now)
        prior=tuple(point[indices[a]] for a in old)
        target=tuple(point[indices[a]] for a in targets)
        if (any(v not in (F(0),F(1)) for v in current+prior+target)
                or sum(current[:n])!=1 or sum(current[n:])!=1 or sum(target) not in (0,1)
                or sum(prior[:n])!=sum(target) or sum(prior[n:])!=sum(target)):
            return outcome(reason='the source domain does not establish one-hot current and causal previous observations')
    for cell in upper.cells:
        point=dict(cell.sources);positions=[]
        for side in (0,1):
            values=tuple(point[pair[side]] for pair in atoms)
            if any(v not in (F(0),F(1)) for v in values) or sum(values)!=1:
                return outcome(reason='revealed proposal inputs are outside the categorical relation scope')
            positions.append(values.index(F(1)))
        counts=edges.setdefault(tuple(sorted(positions)),[0,0])
        for y in (0,1):
            counts[y]+=cell.counts[y]
    # A depth-j state contains the last j replay source factors. Match their
    # original causal origins, including proven empty-prefix identities,
    # against the ordinary stream. Inspect only the needed bounded tail;
    # never expand an arbitrarily long multi-pass profile or supply its state.
    max_window=len(rules.states)//K+1
    positions={key:i for i,key in enumerate(data.active.observation_ids[:ordinary_cursor])}
    replay_count=profile.event_count if type(profile) is ProfileSpec else 0
    _guard(F(replay_count),bit_limit=bit_limit)
    for depth in range(1,max_window):
        origin=-1
        if depth<=replay_count:
            key=profile.observation_ids[(replay_count-depth)%len(profile.observation_ids)]
            origin=positions.get(key,-1)-1  # -2 is unavailable, never empty.
        expected=max(-1,ordinary_cursor-depth-1)
        if origin!=expected:
            max_window=depth
            break
    usable=tuple(s for s in rules.states if s.type_id==dtype and s.delay==1)
    for s in usable:
        _guard(s.upper,bit_limit=bit_limit)
    def add(a,b):return _operation(a,b,multiply=False,bit_limit=bit_limit)
    def mul(a,b):return _operation(a,b,multiply=True,bit_limit=bit_limit)
    def compare(a,b):return compare_exact(a,b,bit_limit=bit_limit)
    def order(a,b):
        return compare(a.upper,b.upper) or ((a.state_id>b.state_id)-(a.state_id<b.state_id))
    ordered=tuple(sorted(usable,key=cmp_to_key(order)))
    def choose_window(s,slots):
        pool=list(ordered)
        previous=[F(0)]*K;assignments=[];best=None
        for H in range(1,max_window+1):
            counts=literal_counts(n,K,H,len(zero_types),slots)
            if any(counts[k]>getattr(grammar,k) for k in counts):
                break
            weights=tuple(mul(add(s,F(1)),add(p,F(1))) for p in previous)
            total=F(0)
            for w in weights:total=add(total,w)
            if compare(mul(add(s,F(2)),total),range_cap)>0:
                break
            best=(H,tuple(assignments))
            if H==max_window:
                break
            next_bounds=[]
            for world,w in enumerate(weights):
                required=add(w,F(-1))
                at=next((i for i,st in enumerate(pool) if compare(st.upper,required)>=0),None)
                if at is None:
                    return best
                state=pool.pop(at)
                assignments.append((world,H,state.state_id))
                next_bounds.append(state.upper)
            previous=next_bounds
        return best
    # Retain every feasible initialized-noise score, including ties. This is
    # a static-latent full-history marginal, not the emitted sliding-window
    # trajectory objective or the registered frozen-endpoint class score.
    for slot,s in enumerate(available):
        _guard(s,bit_limit=bit_limit)
        # Zero learning rate still executes commit quantization. Only an
        # exactly grid-stable used noise slot retains this recurrence.
        grid=learner.commit_grid_bits
        if grid is not None and (s.denominator & (s.denominator-1) or s.denominator.bit_length()-1>grid):
            guidance.append((slot,s,None,0))
            continue
        slots=max(unit,slot)+1
        allocation=choose_window(s,slots)
        if allocation is None:
            guidance.append((slot,s,None,0))
            continue
        denominator=add(s,F(2))
        mismatch=F(denominator.denominator,denominator.numerator)
        _guard(mismatch,bit_limit=bit_limit)
        match=mul(add(s,F(1)),mismatch)
        score=F(0)
        for world in range(K):
            z=(0,)+tuple((world>>(n-2-i))&1 for i in range(n-1))
            weight=F(1,K)
            for (i,j),counts in edges.items():
                parity=z[i]^z[j]
                for y in (0,1):
                    for _ in range(counts[y]):weight=mul(weight,match if y==parity else mismatch)
            score=add(score,weight)
        guidance.append((slot,s,score,allocation[0]))
        if selected is None or compare(score,selected[2])>0:
            selected=(slot,s,score,allocation)
    if selected is None:
        return outcome(reason='no initialized-noise witness fits this categorical state/grammar/range envelope')
    noise_slot,s,_,(H,assignments)=selected
    slots=max(unit,noise_slot)+1
    nodes=[Source(a) for a in used];source_nodes={a:i for i,a in enumerate(used)}
    def emit(node):nodes.append(node);return len(nodes)-1
    def summation(parents,slot=unit,type_id=dtype):
        return emit(Sum(type_id,tuple(Term(parent,slot) for parent in parents)))
    def times(a,b):return emit(Product(dtype,a,b))
    zeros={t:summation((),type_id=t) for t in zero_types}
    one=summation(source_nodes[a] for a in now[:n])
    assignment={(world,depth):key for world,depth,key in assignments}
    state_nodes={key:emit(State(key)) for _,_,key in assignments}
    pairs={}
    for when,ids in (('now',now),('old',old)):
        for i in range(n):
            for j in range(n):pairs[when,i,j]=times(source_nodes[ids[i]],source_nodes[ids[n+j]])
    labelled={(i,j,y):times(pairs['old',i,j],source_nodes[targets[y]])
        for i in range(n) for j in range(n) for y in (0,1)}
    bodies={};excesses=[];head_terms=[[],[]]
    for world in range(K):
        z=(0,)+tuple((world>>(n-2-i))&1 for i in range(n-1))
        indicator=summation(labelled[i,j,z[i]^z[j]] for i in range(n) for j in range(n))
        for depth in range(1,H+1):
            previous=zeros[dtype] if depth==1 else state_nodes[assignment[world,depth-1]]
            gain=times(indicator,summation((one,previous)))
            body=emit(Sum(dtype,(Term(previous,unit),Term(gain,noise_slot))))
            if depth<H:bodies[assignment[world,depth]]=body
        excesses.append(body)
        weight=summation((one,body))
        for y in (0,1):
            chosen=[pairs['now',i,j] for i in range(n) for j in range(n) if z[i]^z[j]==y]
            if chosen:head_terms[y].append(times(weight,summation(chosen)))
    # K-1 is syntax made from repeated initialized-unit incidences, never a
    # numeric SUM literal or a fitted value. This keeps the registered base1.
    offset=summation((one,)*(K-1))
    common=summation((offset,*excesses))
    heads=tuple(emit(Sum(dtype,(Term(common,unit),Term(summation(head_terms[y]),noise_slot)))) for y in (0,1))
    bindings=tuple(Binding(st.state_id,bodies.get(st.state_id,zeros[st.type_id])) for st in rules.states)
    program=Program(tuple(nodes),slots,heads,bindings)
    program.validate(rules)
    counts=program.counts()
    assert all(counts[k]==v for k,v in literal_counts(n,K,H,len(zero_types),slots).items())
    assert grammar.admits(program)
    return outcome(program,'initialized-noise guidance selects one native emission; full grammar, latent uncertainty and fresh evidence remain separate',
        H,noise_slot,assignments)
