# A finite-window posterior is a native delayed positive program

Status: **scoped exact construction theorem, small exhaustive native checks,
owned CPU functional execution and an independent rounded interpreter**.
This supplies a control for the [v5 calibration obstruction](JOINT_FACTOR_DYNAMICS.md),
using the existing typed sources, positive SUM/PRODUCT, delayed transition
bodies and final normalization. No Foundation definition or ERC-1 condition
changes. Actual CUDA execution and a completed source-bound host job are
not claimed by the initial functional evidence below.

## 1. The task and the information cut

There are n>=2 independent fair latent bits z_i. A one-hot ordered query
(i,j) produces label z_i XOR z_j, independently flipped with known probability
1/10. Queries may repeat or be diagonal. The generative prior, noise rate
and finite memory window H>=1 are model assumptions, not learned facts.

Before event t's forecast the native program receives the current two one-hot
query roles, the preceding query roles at lag1, and the preceding target's
two atoms at lag1. The missing previous observation at t=0 is all zero.
It never receives event t's target before forecasting. Runtime owns those
reads through DataContract/SourceRead and retains all ordinary observations.

For each representative z with z_0=0 let m_z count matches among the last
min(t,H) revealed labels. Its unnormalized posterior weight is w_z=9^m_z:
the common factor (1/10)^min(t,H) cancels only in this probability calculation.
Each representative has exactly two full assignments of the same likelihood
and every pair parity, so the forecast equals enumeration of all 2^n worlds.
This is an explicit value construction. It does not identify complete Runtime
states or discard the original observations or any provenance.

**Claim.** A finite native graph with initialized parameter slots Gamma=(1,8),
zero initial delayed coordinates and learning rate zero computes the exact
noisy-query posterior for this declared window, on every legal finite history
whose execution resources and exact arithmetic are sufficient. When t<=H
this is the whole-prefix posterior. After that it is a suffix posterior.

## 2. A positive excess update avoids normalized feedback

Let I_z be the indicator that the preceding revealed label agrees with z.
It is the positive sum of its selected lagged input/target atom products;
at the empty initial prefix it is zero. Let u_z=w_z-1. Starting from zero,

`u_next = u + 8*I_z*(1+u)`

implements multiplication of w by 9 on a match and by 1 on a mismatch.
This has no negative coefficient, internal division or normalized state
feedback. The subtraction in the definition of u is a proof coordinate;
the executable transition uses only the displayed positive operations.

The unit in the graph is the SUM of the current first query role's one-hot
atoms, with the unit slot. Empty SUM supplies zero. Coefficients 1 and 8
are the two actual initializer slots, not numeric SUM literals or fitted
posterior values. The existing LearnerSpec permits learning rate zero.
Its ordinary gradient and clock machinery still executes and remains owned;
commits leave these two parameters unchanged. Adaptation occurs in native
delayed values, not in a replacement optimizer or a callback supplying state.

An indefinitely self-feeding u coordinate has no finite invariant box for
this particular update: a legal match sends its upper endpoint U to 9U+8>U.
The construction does not ask the implementation to accept that false bound.
This is an obstruction to that literal self-loop and bound, not a general
impossibility theorem for other FP encodings or bounded prediction tasks.

## 3. Delayed stages give a valid finite-window invariant

For every world declare H-1 distinct lag1 state coordinates, indexed
1,...,H-1, with upper bounds 9^j-1. If H=1 no state coordinate is required.
On each current prediction construct H bodies. Body1 applies the positive
update to zero; body j>1 applies it to the old coordinate j-1. Store body j
in coordinate j for j<H. Use body H immediately for the readout; it need
not be persisted because no subsequent body reads it.

At a forecast, the old coordinate j-1 already summarizes a suffix ending
one observation earlier than the lagged label now being consumed. Thus
induction gives body j as 9^(matches in the last min(t,j) labels)-1.
This proves the claim, including the initial all-zero delayed state. The
ordinary observe transition commits the already computed delayed bodies;
the current label first affects the next forecast through its lag1 atoms.

For each stage the fixed interface bound is genuinely invariant, even when
old state coordinates are varied independently throughout their declared
box: the largest next body is

`(9^(j-1)-1) + 8*(1+9^(j-1)-1) = 9^j-1`.

This uses only I_z in {0,1} and the constant unit. The declared source domain
enumerates the current one-hot query times either an empty previous prefix
or a previous one-hot query with one target atom. It does not assert an
invariant for arbitrary soft inputs. Runtime must refuse inputs outside
its registered domain rather than inherit this proof there.

The resulting program uses K*(H-1) delayed coordinates, K=2^(n-1). This is
a literal upper construction, not a minimal-state lower law. All its source,
graph, intermediate, gradient, trace and complete Runtime costs remain due.

## 4. The positive base also has to represent diagonals correctly

Let u_z denote current body H, w_z=1+u_z, and G_zy the current one-hot query's
parity-y indicator in world z. Use fixed base (K,K) and native evidence

`E_y = SUM_z u_z + 8*SUM_z w_z*G_zy`.

The final masses are therefore

`M_y = SUM_z w_z + 8*SUM_z w_z*G_zy`,

with `M_0+M_1=10*SUM_z w_z`. Their normalized values are exactly the
posterior probabilities of the independently noisy next target. For a
diagonal query all G_z0=1, giving (9/10,1/10) under every history. No
input-dependent base or hidden output coefficient is supplied. A fixed
base chosen by assuming that half the worlds realize each query parity
would be wrong on diagonals; the shared positive excess above avoids that
assumption.

Since every w_z<=9^H, the finite bound 10*K*9^H covers the total mass and
all forward intermediates of the emitted graph on the stated domain and
state box. The initialized two slots are paid normally. This bound alone
does not bound every gradient, resource or numerical error: those are
checked by the ordinary Runtime and its bridge on actual execution.
Literal dynamic range is exponential in H, as are the represented likelihood
ratios. This short-window witness is not yet a practical long-history GPU
posterior, nor a new static resource/precision study.

## 5. Exact, functional and rounded evidence have separate scopes

Run `python -B experiments/joint_uncertainty/recurrent_control.py`.
The audit covers all ordered signed histories through length two for n2
at windows1/2 and n3 at window3, including diagonal queries, plus signed
three-edge triangles and explicit longer-window eviction controls. It
checks 3,487 full-prefix posterior endpoint forecasts, 264 suffix endpoint
forecasts and 969 intermediate forecasts. Its independent oracle enumerates
all 2^n assignments, without the native excess or staged-state recurrence.

`--cpu` uses the actual ReferenceCompilerRuntime with CompilerPolicy(()).
Its initial n3,H3 graph has123 nodes,14 sources,8 State reads,46 SUMs,
55 PRODUCTs,256 edges,two slots and eight bindings. Only ordinary contexts
and then labels are supplied. The sequence (01,0),(12,0),(02,1),(01,0)
has forecasts

`(1/2,1/2), (1/2,1/2), (189/250,61/250), (77/122,45/122)`.

It seals as SEALED_REFERENCE_STREAM; an independent binary64 replay checks
13 complete phases. Parameters remain (1,8), all delayed coordinates and
all four observations are retained, and every pending target is absent at
prediction. There is no supplied fitted theta or delayed state, installation
receipt, reference class proof or CERTIFIED_COMPLETE decision. This command
has no live host binding and explicitly reports its host scope UNRESOLVED.

`--rounded` checks192 predictions on48 four-label streams, with cycles,
repeated queries and diagonals, using the existing independent half/single
interpreter. Native masses and delayed states agree exactly on these cases;
the maximum gradient error is193741/255852544000 and maximum raw division
error is1/41943040. Both are below the declared binary64 functional tolerance
1/100, but that comparison is not an actual CUDA registration or audit.
The exact forward-gradient oracle is separate from the rounded interpreter;
Torch is never imported by any of these checks.

The source-bound CPU launcher `--bounded --write` fixes two fresh Windows
jobs before execution:512MiB process/job commit cap,120-second timeout,
256MiB packed payload cap and10^10 work per role. It binds unchanged source
dependencies and completed process identity, including post-run exit and
peak counters. The full-window case also runs the exact and rounded checks.
The second case has H2 and the repeated labels0,0,1: its next forecast is1/2,
whereas the whole-prefix posterior is41/50. Both retain the full history.
Only an actual completed journal can upgrade this registration to evidence.

## 6. What this resolves and what it leaves open

The earlier finite-update calibration failure belongs to v5's parameter
trajectory, rather than to positive FP semantics in this finite task. Native
delayed state can perform the required Bayesian update and noisy readout.
Forgetting in this declared model is observable and does not erase retained
data from the complete Compiler state. No prediction equality is promoted
to a continuation equivalence or a compiler certificate.

The model is registered initially, with known prior/noise and a finite window.
This proves neither that the existing proposer discovers it nor that it is
cheaper than a strong posterior baseline, useful over long histories, or
installable from current evidence. Actual owned AMP execution remains the
next numerical question. RN-5's matrix, data, model, source and budgets stay
unchanged; its failures remain failures. Foundation R4 and ERC-1 stay frozen.
