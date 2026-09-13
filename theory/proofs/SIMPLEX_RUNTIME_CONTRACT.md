# The registered normalized simplex learner and owned affine proposal

This is a distinct learner U under Foundation VII, not a change to the native
SUM/PRODUCT language, the frozen Foundation, ERC-1, or RN-5's SGD experiment.
The [affine gradient theorem](SIMPLEX_GRADIENT_POSTERIOR.md) motivates the rule;
this document fixes its operational and audit scope. A bounded whole-history
normalizer does not imply bounded precision or uniform future AMP accuracy.

## 1. The complete learner coordinate

`mean-ce-normalized-simplex-gradient-v1` registers an ordered nonempty tuple
of distinct `simplex_slots`, rate eta in[0,1], an ordinary update unit m>=1,
and no commit grid. Other parameter slots remain fixed. The actual native
reverse derivative is still computed and accumulated for **every** slot,
including fixed slots; delayed histories remain event-local stop-gradient
inputs. The full accumulator, delayed state, clock and optimizer step count
remain ordinary owned state. The old projected-SGD optimizer stays distinct.

Construction executes the actual cyclic initializer Gamma. Its selected
slots must exist and sum to exactly1 under the registered integer guard.
Otherwise the attempted value path remains unresolved. There is no supplied
posterior vector, renormalized initializer, inferred reset or hidden slot.

At a full update boundary, let G be the accumulated ambient native gradients.
The registered arithmetic uses the following order, summing selected slots
in their declared order:

```
s = eta / m
S = SUM_j w_j
mu = (SUM_j w_j G_j) / S
r_j = w_j * (1 - s * (G_j - mu))
R = SUM_j r_j
w_j_next = r_j / R
```

The exact path requires S=1, refuses any r_j<0, and requires positive
divisors. Algebra gives R=S=1, so its explicit final division is the identity
over exact arithmetic. The guarded implementation still performs it.
All unselected theta coordinates are preserved, all gradient accumulators
are cleared together, and the actual full-unit clock advances once.

Binary64 and CUDA execute the same normalized formula on their **own**
rounded states and gradients. Their S need only be positive; an independently
rounded simplex need not sum to exactly1. Every normalized nonnegative zero
is encoded as positive zero. This representation step follows the negative
and nonfinite checks; it cannot clip an invalid successor into validity.
All numerical uncertainty continues through the existing event-level bridge
and refusal path. No exact gradient or reference successor is cast into a
pretend physical update.

The binary64 commit has exactly `7+11*K` registered scalar operations for a
K-slot block. The CUDA commit materializes `7+15*K+2*N` output cells for N
total slots, including copies, ordered reductions and zero canonicalization.
These are counts for this lowering, not hardware-optimality lower bounds.
Reference commit work is prepaid by the declared conservative
`12*K+2*N+8` allowance; construction, range/bridge checks, stored evidence
and profile work remain separately charged by Runtime.

## 2. What one unit means

For the theorem's affine masses `M_y=b_y+SUM_j w_j a_yj` with equal expert
normalizers, each single-observation unit step has posterior
`B_y(w)_j=w_j*(b_y+a_yj)/M_y`.

During a larger event-local update unit, w is frozen and the gradients add.
Linearity of the tangent step in G therefore gives exactly

`w_next = (1-eta)*w + (eta/m)*SUM_s B_{y_s}(w)`.

This is a convex mean of the posteriors from the individual observations at
the common starting weights. It is generally **not** the posterior of their
joint likelihood. Two identical relation labels from equal weights give
weights(9/10,1/10) for a two-event unit, versus(81/82,1/82) for two sequential
unit events. A whole-history Bayesian interpretation requires m=eta=1 and
the stated affine/equal-normalizer model. With delayed features the formula
uses each event's actual frozen-delay feature values; it grants no recurrent
latent-model interpretation by itself.

The fixed feature slot is substantive: its initial diagonal-label native
gradient is-4/45. It is retained during observation, then the registered U
keeps that parameter fixed. For unequal expert normalizers, the known exact
counterexample has raw successor(27/20,-7/20) and remains unresolved.

## 3. Native construction, class scope and fresh installation

`native-binary-relation-simplex-posterior-v7` emits one literal native graph
for the known fair-prior, noise1/10 relation model. It receives the actual
source alignment, complete source domain, data reads, learner, initializer,
grammar and profile. It requires two current categorical query roles, every
one of the n^2 ordered pairs, static base-one heads, Gamma=(1,1/K,...,1/K),
the full selected block1..K, and m=eta=1. Here K=2^(n-1). Eight repeated
native incidences implement the declared known noise; no value is injected
through a fitted coefficient. This is a known-model proposal, not learned
noise/prior, model discovery or a graph-only reinterpretation of SGD.

The emitter checks the slot budget before exponentiating or allocating the
latent family. Literal costs are `2*n+n^2+2*K+2` nodes,
`2*K+2` SUMs, `n^2` PRODUCTs, `2*n^2+K*n^2+16*K` edges and K+1 slots.
Runtime prepays proposal work, constructs through Gamma, runs the actual
registered profile, and scores the retained complete endpoint. A profile
with two passes uses every replay twice. The emitter grants no value-path,
class, source, installation or future-state authority.

Each historical decision class remains the **full ordered native grammar
under the actual initializer/U/profile and logged fixed-state objective,
together with the deployed baseline**. Its identity includes these manifest
coordinates. A proposal does not exhaust that class. The independent universal
empirical upper retains its original completion meaning; otherwise the class
stays unresolved. Missing-block/unsupported values remain retained outcomes.
For example, a fully exhausted20-program tiny class compares5 endpoints and
retains15 missing-block failures under this U. It cannot issue a class proof.
The same syntax has20 compared endpoints under the distinct SGD contract.

The existing prospective policy may admit a compared improvement while the
class is unresolved. Fresh reference and physical evidence starts after that
comparison, uses each path's actual continuous learner, and must independently
cross before the actual resident installation. No old class proof, profile,
fresh wealth, transport record or lineage is inherited across the U change.
The Runtime extension adds no `CERTIFIED_COMPLETE` decision class.

## 4. Exact and physical audit registration

`scripts/audit_simplex_contract.py` checks603 exact complete commits against
the independent affine posterior mean, noncontiguous/fixed slots, zero weights,
larger update units,12 registration/initializer refusals,10 proposer refusals,
the20-member exhaustive classes and the policy's exclusive constructor port.
Independent binary64 and actual CUDA boundary checks cover rounded totals,
zero times a negative finite factor, negative nonzero refusal, full raw state
and exact scalar/output counts. These low-level checks have no install authority.

`scripts/audit_simplex_learner.py --matrix --write` registers eight complete
jobs: CPU and RTX3090 paths each run ordinary n2/n3 streams and an owned
n2 one-pass / n3 two-pass search-profile-fresh-install stream. Ordinary tapes
have six observations; profiled streams use their first two observations,
then forty(0,1,label0) observations, then the remaining four original records.
The source file fixes the exact tapes. All queries arrive before their labels.
An independent full2^n assignment posterior checks candidate forecasts using
the actual profile multiplicity plus subsequent ordinary history.

Each job declares32768 reference integer bits,512MiB packed state,10^11 work
per role, range caps16, binary64 tolerances10^-9, AMP state/native/normalizer
tolerance1/100 and probability tolerance1/1000. The target uses the existing
half-forward/single-readout-backward-master path,16MiB resident arena,32MiB
allocator allowance,4096 output cells and256KiB evidence frames. Whole-host
job caps are512MiB on CPU and4GiB on CUDA, with180-second timeouts.

The installed streams register one-event fresh epochs, gain bound6, bet3/4,
alpha1/4 per path, total alpha3/4 and40 possible epochs. The external
branch-invariant stochastic-law assumption is explicit; no audit tape proves
it. Every score and wealth update is independently recomputed. The initial
zero-head deployment is a protocol fixture, not a competitive model baseline.
This matrix cannot support a model-superiority or population-risk claim.

The parent binds the committed execution dependencies before and after each
job, including the final independent replay. Failed outcomes stay in the
minimal journal; caps and tolerances are not expanded after seeing outcomes.
The [completed journal](../../evidence/minimal/FP_SIMPLEX_LEARNER_AUDIT.json)
binds execution source b34bf7b: all eight jobs execute and seal, with four
installations at22 and four unresolved historical search classes. Audits
independently replay1,208 binary64 phases,604 CUDA phases,200 posterior
forecasts and160 fresh-score/wealth events. Maximum packed state is77,265,284
bytes and completed job commitment2,417,373,184 bytes. Maximum CUDA
state/native/normalizer errors are422861/188743680,3/640,1/256; the maximum
mass-normalized probability error is249137/1677721600. All stay within the
original caps and tolerances. No failure or resource enlargement is hidden.
The registered matrix does not freeze arbitrary-program, long-history or
large-n AMP accuracy. A useful resource-matched model comparison remains a
separate experiment, and RN-5 continues at its original source and limits.
