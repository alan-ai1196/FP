# What the declared token optimizer does below one grid step

Status: **SCOPED THEOREM, EXACT CAUSAL COUNTEREXAMPLE AND FULL-V FLOAT64
DIAGNOSTIC PASS, 2026-09-29; AUDIT CLOSED**. This analyzes the existing
floor-grid optimizer before selecting an ordinary-text learner. It changes
neither G/Gamma/U nor Foundation/ERC, and supplies no text score, new Runtime
authority or actual AMP result. The relation branch remains closed.

The conclusion is narrower than either “the model cannot learn” or “a smaller
learning rate fixes the update.” At fixed precision the declared parameter
update is discontinuous at learning rate zero. A reached causal example loses
likelihood and becomes trapped for arbitrarily small positive rates. The
existing full-vocabulary resource fixture has one-sided embedding steps in
its first unit, but substantial core/readout changes. Its trainability and
held-out quality remain unestablished.

Source: [token_native.py](../../src/reference_compiler/fp_reference/token_native.py),
[token_readout.py](../../src/reference_compiler/fp_reference/token_readout.py).
Audit: [audit_token_grid_dynamics.py](../../scripts/audit_token_grid_dynamics.py).
Evidence: [FP_TOKEN_GRID_DYNAMICS.json](../../evidence/minimal/FP_TOKEN_GRID_DYNAMICS.json).

## 1. Exact update cells and the small-rate limit

Fix a completed registered unit, including its original source points and
targets. Let Q=2^b, m>=0 be one integer master, G its accumulated exact loss
gradient, B the unit size, eta>=0 the learning rate, and a=eta Q G/B. Existing
U uses downward rounding after nonnegative projection:

    m' = max(0, floor(m-a)) = max(0, m-ceil(a)).

This is floor rounding, not nearest rounding. The integer identity proves
the following complete scalar classification, including the boundaries:

| Change | Necessary and sufficient condition |
| --- | --- |
| Increase | a <= -1 |
| Decrease | m > 0 and a > 0 |
| Unchanged, m > 0 | -1 < a <= 0 |
| Unchanged, m = 0 | a > -1 |

For any finite complete parameter vector, choose eta>0 small enough that
|eta Q G_i/B|<1 for every nonzero G_i. Every positive master with positive
gradient decreases by exactly one integer quantum. Every other master stays
unchanged, including zero masters with small negative gradients. Thus the
fixed-unit parameter update has a constant right-hand limit as eta decreases
to zero. That limit differs from the eta=0 identity whenever some positive
master has positive gradient. This is a statement about a fixed reached unit;
it does not hold its gradients fixed during later training.

For theta=m/Q and the unrounded projected step
theta_real=max(0,theta-eta G/B), the same identity gives the sharp one-step
error interval

    -1/Q < theta' - theta_real <= 0.

Consequently coordinate error tends to zero as Q grows, but need not tend to
zero as eta decreases at fixed Q. No universal beneficial or harmful loss
direction follows: the finite step can overshoot even when the unrounded
gradient points downhill. Neither SGD continuity nor nearest-rounding
dead-zone intuition can be assumed for this U.

## 2. A reached causal loss increase and absorbing state

Take the existing native token definition with V=2, context one, width one,
one input feature, no extra core nodes, positive bases (1,1), Q=1 and unit
B=6. Initialize the five masters in order

    (E_0, E_1, E_PAD, W_0, W_1) = (1,1,1,1,4).

The indexed input and output are ordinary positive SUMs. Run the contiguous
teacher-forced word (1,0,0,1,1,1), starting with PAD. No invented pending
gradient or supplied noncausal context is used. Before commit each forecast
is (2/7,5/7). Exact differentiation on the six retained source points gives

    G = (9/70, 3/70, -3/35, -1/7, 2/35).

For every 0<eta<1 all five scaled gradients lie strictly between -1 and 1.
The classification above gives the same endpoint

    (0,0,1,1,3).

Evaluate both parameter vectors on those same six original contexts. Their
exact likelihood products are

    before = (2/7)^2 (5/7)^4 = 2500/117649,
    after  = (2/3) (1/2)^5 = 1/48 < before.

The mean loss therefore increases by log(120000/117649)/6>0 for every rate
in that interval. At eta=0 the parameters and likelihood are unchanged.
The audit also checks that the explicitly counterfactual unrounded step
strictly improves this same-unit likelihood at eta=1/16 and eta=2^-32.
Those unrounded steps are not executions of the registered optimizer.

The endpoint is more than a one-step loss reversal. For all future ordinary
contiguous continuations over the same two-token alphabet, every context is
now token 0 or 1, so its feature is zero. All forecasts are (1/2,1/2), and all
readout gradients are zero. The embedding adjoint is +1 for target 0 and -1
for target 1. Each embedding's mean unit gradient is therefore in [-1,1].
Since 0<eta<1 and its master is zero, no embedding can cross the negative
one-quantum activation threshold. PAD is never read again. Induction over
the algebraic reference units proves that the parameters remain (0,0,1,1,3)
under every such ordinary continuation on which updates are admitted.
Sources, clocks and pending gradients still evolve.

This is a coarse-grid witness to a false general guarantee, not a prediction
that the full-V/grid16 fixture enters this trap. It is also not invariant
under arbitrary reinitialization, profile replay, changed U or graph
installation. It grants no permission to delete the zero coordinates or
their legal continuation information from complete state.

## 3. Absent labels and the positive readout

For the existing head m_y=b_y+sum_k W_yk f_k, the exact gradient is

    G_yk = sum_t f_tk/Z_t - sum_{t:y_t=y} f_tk/m_t,y.

An absent target label has only the common nonnegative term. For eta>0,
its positive master decreases by at least one quantum in any unit where
feature k is positive at least once, however small the rate. It is unchanged
if that feature is identically zero in the unit. Across a run of units in
which y never occurs, after A such active units

    m_yk <= max(0, initial_m_yk - A).

The bound follows by induction from ceil(a)>=1 for a>0; it permits changing
feature values and all other parameter updates. In particular, initial
masters at most seven reach zero within seven *active* absent-label units.
The theorem does not say that every column remains active or that a label
never occurs. Positive bases remain, and a later target correction can revive
a retained zero coordinate. The exact audit checks both inactive units and
revival on a separate reached readout trajectory.

This behavior already belongs to the chosen U. Calling it an added
regularizer would misdescribe the implementation; changing rounding or
carrying a hidden rounding residual would instead define another optimizer
and require an explicit registration with its complete state and bridge.

## 4. What the existing first full-V unit actually certifies

The passive audit reads only the already exposed original 1,024 training
bytes and reconstructs the original 512 targets/windows. It uses the unchanged
V=50,257, L=512, D=4, K=8 resource fixture, Q=65,536, eta=1/1024 and B=512.
Thus a=G/8. The existing outward binary64 solver resolves every endpoint grid
cell across all 603,092 native masters. The complete origin and all original
unit records are the reference representation; this is not an independent
full-unit rational materialization or a replay of a terminal device job.

| Block | Coordinates | Unchanged | Increased | Decreased | Newly zero |
| --- | ---: | ---: | ---: | ---: | ---: |
| Embedding E | 201,032 | 200,567 | 0 | 465 | 0 |
| Core C | 4 | 0 | 2 | 2 | 2 |
| Readout W | 402,056 | 0 | 1,992 | 400,064 | 185,752 |

The 250 active embedding rows contain 1,000 coordinates. All scaled gradients
are enclosed inside [-0.7943470729817026,0.8481923488218088], strictly within
(-1,1). Independent sign enclosures resolve 465 positive and 535 negative
coordinates; none straddles zero. The former decrease exactly one master
unit, and the latter stay unchanged. In real parameter units each decrease
is only 1/65,536; this observation alone is not a harmful-loss certificate.

Core masters change from (128,128,128,128) to (571,0,0,439). There are 249
observed target rows, and all their 1,992 readout coordinates increase. The
other 50,008 rows obey the common integer decrement

    (3,4,4,5,2,2,2,2), clipped at zero.

The retained evidence includes the outward endpoints for the core and common
terms and the complete per-block change counts. No corpus loss, held-out
information, later-unit dynamics, GPU trajectory or timing is measured here.
In particular, the fixture is not globally frozen, and the small causal
absorption witness cannot be transferred to it without further evidence.

## 5. Evidence and stopping decision

The finite exact audit covers all 720 one-unit histories formed from
b in {0,1}, eta in {0,1/16,1,2,8}, B in {1,2}, common embedding master in
{0,1,3}, head masters in {(0,0),(0,1),(1,0),(1,4)}, and every corresponding
binary word. Every forecast, pending gradient and commit agrees with the
independent literal DAG learner.
Its 3,600 coordinate decisions include both nonzero integer boundaries,
positive/negative subquantum steps and clipping. The loss witness additionally
checks all 64 next-unit words at each of its two positive audited rates; the
inductive proof, not that finite enumeration alone, establishes the infinite
ordinary-continuation invariant. No CERTIFIED_COMPLETE search class is added.

Close this optimizer diagnosis here. The existing resource fixture remains
unselected as a language model, for the already stated
[capacity reasons](FROZEN_READOUT_CAPACITY.md) as well as its unmeasured
learning quality. Use the update-cell law when specifying an actual learner;
do not append a rate/precision sweep or another static relation family.
The next objective remains an affordable, preregistered ordinary-text training
and frozen-reporting comparison with the strong baselines. Execution cost,
model capacity and update precision are separate questions; this result
neither solves affordability nor justifies relaxing complete-state checks.
