# An owned likelihood-coordinate lowering of the unit simplex learner

This contract applies the [complete learner encoding](COUNT_LEARNER_ENCODING.md)
and [finite likelihood information law](LIKELIHOOD_INFORMATION_LAW.md) to a
declared physical backend. It keeps the registered unit simplex U and native
positive SUM/PRODUCT program. It introduces no semantic architecture action,
source, fitted parameter, reset, fresh-evidence shortcut or Foundation change.
The original [FP32 reversal failure](SIMPLEX_REVERSAL.md) remains valid for its
original backend. ERC-1 and the live RN-5 source are unchanged.

## 1. Exact scope and derivation

The numerical representation is
`finite-affine-commensurate-likelihood-coordinates-v1`. Its actual inputs are
the admitted Program, full SemanticRules, actual cyclic initializer Gamma,
registered learner U and **complete** finite source domain. The selected
slots must be strictly positive and sum to one at initialization. The actual
learner must have rate one, unit one and no grid. Delayed state is unsupported.
No API accepts a likelihood bank, posterior, trained endpoint or factorization
as a construction value.

At each legal source point, a bounded positive affine interpreter establishes

`M_y(w) = B_y + SUM_k A_yk w_k`,

where B_y includes the actual positive base and all fixed-slot contributions.
The sum over labels of A_yk must be the same for every selected k. A nonlinear
head or an unproved equality is unresolved. Nonlinear **interior** nodes may
remain when multiplication by an actual fixed zero makes their contribution
to a selected head affine. This does not remove the node, its native cache or
its ambient derivative. The exact audit has an interior square with current
head contribution zero and fixed-slot gradient -1/8.

The selected-slot tangent gradient satisfies

`G_k - SUM_j w_j G_j = (M_y - B_y - A_yk) / M_y`.

Consequently the already registered unit U has exactly

`w'_k = w_k * (B_y + A_yk) / M_y`.

Equal expert normalizers make this the normalized likelihood update. Thus
the exact transition is derived from the native graph and actual U, including
its fixed coordinates. It is not an interpretation attached to a graph while
leaving an incompatible optimizer in place.

Register one rational radix b>1. Every initial selected-weight ratio and
every event's expert-likelihood ratio to world zero must be an integer power
of b. Repeated exact division decides this within the integer/work allowance;
there is no floating logarithm or hidden prime factorization. This is a
commensurate subclass of the general rational-bank theorem. In particular,
the backend does not cover a bank requiring independent powers of 2 and 3.

Let v_a be the vector of these integer likelihood-ratio exponents for event
a=(actual source row, target). Choose the first registered event a0 and form
the integer matrix with columns D_a=v_a-v_a0. Retain an independent subset of
its original rows and guarded rational reconstruction coefficients. Every
input column is reconstructed exactly before the derivation succeeds. If
the rank is rho, the persistent coordinates at T commits are

`q_i = SUM_committed a D_a[selected_row_i]`.

The full exponent vector is

`z_k = prior_exponent_k + T*v_a0,k + SUM_i reconstruction_ki*q_i`.

The initial model retains the actual Program identity, full semantics/domain,
Gamma, U, radix/precision contract and complete reconstruction. The first
CUDA phase stores that descriptor in its owned packed evidence. Later raw
states carry its primitive content digest, q and the pending actual event.
The digest has a specific role: an aliased Python descriptor object alone
would let a later mutation change earlier in-memory phase records as well.
The original packed frame and primitive digest distinguish that mutation.

## 2. Complete phases and the numerical backend

`eager-cuda-half-forward-single-gradient-count-decode-v1` retains all resident
theta, gradient and delayed-state fields of the ordinary CUDA learner, its
absolute cursor and optimizer-step count. The extra state is the owned model,
rho integer coordinates and either no pending event or the actual current
source-row/label pair. Unsupported delayed rules are refused before this
representation is constructed; an empty delayed tuple is still explicit.

Initialization encodes actual Gamma by ordinary RNE32 ingress. Prediction
executes the entire native mixed-precision forward graph and records the
actual complete-domain query index before target revelation. Observation
requires that sealed prediction's predecessor and observation identity,
computes and accumulates the entire native AMP reverse derivative, and
retains the actual pending event. Fixed-slot gradients are not discarded.

At commit, the pending event updates q exactly and is cleared. The physical
theta is then decoded on the actual GPU from those coordinates. This is an
alternative lowering of the **exact** U; its floating commit intentionally
does not repeat the old weighted-gradient floating expression. The exact
simulation above licenses this alternative arithmetic. The observed native
gradient remains a checked, owned predecessor field, and is cleared together
with all other gradient coordinates only by the registered full-unit commit.
No exact reference successor is cast or copied into a pretend GPU update.

Set d_k=max(z)-z_k. In binary32, encode beta=1/b and constants one and zero,
build beta^(2^i) by positive repeated squaring, and multiply the selected
powers for each d_k. Sum the resulting nonnegative masses in slot order,
divide each by that sum, and copy only the selected theta coordinates. At
least one d_k is zero, so its unnormalized physical mass is exactly one;
underflow of other masses cannot destroy this denominator. Every produced
intermediate still receives the ordinary nonfinite/range/bridge checks.

A currently decoded zero is not the persistent posterior state. A future
opposite likelihood increment changes the retained q, so a later decode can
produce a positive representable value again. No threshold, revival action,
epsilon floor, injected gradient or retrospective target scan is involved.
This does not prove uniform accuracy for unlimited histories: counters,
exact guards, model size, work, device range and the actual per-phase relation
can all exhaust the declared envelope. Such a run must stop unresolved.

Profile repetition updates q and T once per actually replayed event. Attaching
a completed profile changes the absolute cursor without resetting q or T.
Ordinary continuation then uses that attached complete state. Installation
preserves the same resident learner objects, tensor leases, integer state,
descriptor identity, clocks and retained prefix. Fresh scoring accepts the
tagged full forecast only after the existing exact-checked pre-target lineage
test; its probability is formed from actual CUDA stored masses. Reference
wealth does not stand in for CUDA wealth.

## 3. Finite resources and authority

Counter precision is registered between 2 and 64 bits. Coordinates, decoded
signed exponents and T must satisfy abs(value)<2^(bits-1). A proposed update
outside that domain is refused before any new GPU power is materialized.
The pending observed gradient/event, spent resources and completed evidence
remain retained; there is no wrapped counter or erased failed label.

Before deriving a model, Runtime debits the bounded analyzer's conservative
work allowance, allocates a fixed phase frame and a shape/precision-dependent
scratch extent, and materializes that scratch as an owned host buffer. The
analyzer guards rational operations and exact divisibility steps. The scratch
is released only after the attempted phase's result has been retained or its
failure propagated. The initial frame retains the complete derived descriptor.
Subsequent phases prepay descriptor validation, exact coordinates, domain
matching and reconstruction as well as the ordinary native CUDA work.

For N total slots, K selected slots and L=max(d).bit_length(), a successful
decoded commit materializes exactly

`3 + max(L-1,0) + SUM_k popcount(d_k) + 3*K + 2*N`

GPU output cells. This includes constants, positive arithmetic, copies and
gradient reset. These are the registered schedule's costs, not optimality
lower bounds. The full graph, source domain, descriptor, native cache, raw
observations, provenance, gradients, audit frames and profile evidence are
still paid. The packed scratch formula is not a total CPython heap theorem;
the enforced whole-process host job separately bounds actual heap/temporary
storage, native allocations and audit overhead.

The immutable manifest identifies the alternative backend and work model.
Input binding, exact coordinate transitions and numerical closeness are
separate checks. A model with a substituted source subset cannot initialize
this backend. A private count or descriptor mutation cannot pass merely
because the visible theta is still close to the reference. Public snapshots
contain no device handles and cannot authorize a successor or installation.

The constructor grammar is not narrowed to this analyzer's support. A legal
program outside that support stays an unresolved member of the declared
class. The v7 proposal may construct a feasible member and earn fresh evidence,
but supplies no historical class-completeness certificate. Foundation R4 and
ERC-1 remain frozen.

## 4. Audit registration and evidence discipline

`scripts/audit_likelihood_encoding.py` independently evaluates actual native
graphs at every selected simplex vertex. It checks the derived factors and
rank against that bank and reconstructs complete ordered likelihood products.
The initial exact audit covers 958 native transitions and relation ranks
1,3,6, plus noncontiguous selected slots, nonuniform priors, rational radices,
fixed-zero nonlinear interiors and scope/resource refusals. It does not call
the production decoder to manufacture an expected GPU successor.

For actual GPU prefixes the auditor replays native AMP forward/gradient
operations with the independent exact RNE16/RNE32 interpreter. Each commit's
input comes from the replayed full likelihood word, not the production q.
Every positive commit operation tape, full raw state, query tag, coordinate,
clock, packed phase frame and output-cell count is checked. Binary64 phases
receive the existing independent replay. Attack cases preserve their failed
state; passive replay may use a descriptor copied before deliberate corruption
to check its unchanged original evidence frame, but never repairs the Runtime.

`experiments/joint_uncertainty/likelihood_lowering.py` registers nine fresh
owned jobs: the 100-event reversal; n3 two-pass profile/search/fresh install;
six-bit overflow; a count corruption at the underflow cut; descriptor
corruption at that same cut; insufficient work; insufficient scratch; and a
substituted incomplete source domain; and a complete 20-member tiny grammar.
Reversal/profile jobs must seal. Six attacks must preserve the prescribed
refusal with no seal or install. Tiny-grammar exhaustion must keep all 15
unsupported members unresolved, compare the five supported members, and
issue no class proof despite reaching the end of the syntactic enumeration.

Each job is attached before execution, with a 4GiB host cap and 180-second
timeout. Ordinary runs have 512MiB packed payload, 10^11 work per role,
32768-bit reference arithmetic, native caps16, binary64 tolerance10^-9,
AMP state/native/normalizer tolerance0.01 and probability tolerance0.001.
The GPU arena is16MiB, allocator cap32MiB, phase output cap4096 and fixed
phase frame262144 bytes. Overflow uses six-bit counters. The work/scratch
attacks lower only the relevant registered resource cap before construction.
The fresh case uses the already registered paired persistence rules and a
native v7 proposal; historical class status must remain UNRESOLVED.

Matrix execution requires a clean committed set of execution dependencies;
each minimal report binds source, actual process identity and counters to
the completed enforced job. All attempts are retained, including unexpected
failures. No weights, tensor cache or full raw tape is dumped. Development
checks are not source-bound matrix evidence, and this finite lowering audit
is not a new full Runtime release or a matched model comparison. Shared-board
VRAM is only the existing uniform physical upper bound, with no exclusivity
or performance claim. Execution outcomes will be recorded after registration.
