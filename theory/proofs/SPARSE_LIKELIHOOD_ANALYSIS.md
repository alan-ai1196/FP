# Sparse exact affine derivation and an independent positivity verifier

Status: **PROVED EQUIVALENT EXACT DERIVATION; IMPLEMENTED; EXACT AND FUNCTIONAL AUDITS**.
This optimizes the analyzer of the [likelihood Runtime contract](LIKELIHOOD_RUNTIME_CONTRACT.md).
It leaves the admitted Program, full source domain, Gamma, U, physical decode,
resource ownership and constructor decision class unchanged. The old nine-job
source-bound evidence remains attached to08fa7bc.

## 1. What can safely be omitted from an analyzer

For one registered source row, represent a formal affine value as

`constant + SUM_(i in support) coefficient_i * w_i`.

Only an **identically zero formal coefficient** is absent. This is not a
threshold on a current learned or rounded weight. Every complete-domain row
is analyzed separately, with actual source values and fixed parameters.
Selected variables start with their unit coefficient; source values and fixed
parameters are constants. Nonnegative coefficients cannot cancel.

An exact zero form annuls any product, including a conservatively unsupported
nonlinear operand. Otherwise two variable-dependent operands are unsupported;
a constant times an affine form scales its constant and present coefficients.
A SUM accumulates each actual term in order into a fresh coefficient map.
Parent maps, variable forms and the shared zero form are never mutated.
Induction over the native DAG proves equality with the former dense formal
interpreter whenever both complete. Dense head rows are emitted at the same
boundary, so likelihood factors, rank and reconstruction are unchanged.

Every transported nonzero coefficient receives the same guarded rational
operation in the same per-coordinate order. Removed operations concern
proved-zero coefficients. A sparse pass can finish where dense zero overhead
would exhaust a tight work or conservative arithmetic allowance; this is a
solver improvement, not a stronger semantic certificate. The old conservative
prepaid work and scratch bounds remain in place. Sparse Python dictionaries
are not claimed to have smaller worst-case object overhead than tuples;
the enforced whole-host job remains responsible for actual heap usage.

No native node, forward cache, full ambient derivative, source row or future
continuation is removed. A fixed-zero multiplier can make a selected head
affine while its fixed-slot derivative remains nonzero. The existing exact
case with that derivative equal to-1/8 continues to pass.

## 2. A different proof for the passive verifier

Using the producer's factorization to manufacture its own expected bank
would not be an independent audit. The verifier instead uses this elementary
positive-polynomial fact: after fixing sources and unselected parameters,
a nonnegative-coefficient polynomial evaluates to zero at strictly positive
selected Gamma **if and only if** it is identically zero.

Evaluate the actual native graph exactly at Gamma. Mark a zero value with
degree-1, a positive source with degree0, a positive PRODUCT with the sum
of parent degrees, and a positive SUM with the maximum degree of its active
terms, adding1 when the term's parameter is selected. Cap positive degrees
at2. Positivity excludes cancellation; induction establishes the true degree
up to that cap. Every selected head must have degree at most1. This proves
affinity on the full selected orthant; it does not assume polynomial identities
valid only on the normalized simplex.

For each head, an independent exact reverse pass through the actual SUM and
PRODUCT tape obtains its mass derivatives A_yk at Gamma. Since affinity has
been proved, these are its coefficients, and

`B_y = M_y(Gamma) - SUM_k Gamma_k*A_yk`.

The passive verifier checks B_y>=base_y and A_yk>=0, constructs all expert
masses B_y+A_yk, and checks their equal normalizers. Its expected bank uses
neither the production sparse maps nor the likelihood-coordinate decoder.
It also retains all-slot derivatives while forming the selected submatrix.
This is an auditor algorithm, with no authority to initialize or update a
Runtime learner.

## 3. Vertex agreement alone is insufficient

Compare affine masses(1+8w1,1+8w2) with nonlinear masses(1+8w1^2,1+8w2^2).
They agree at both simplex vertices, have the same expert normalizers there,
and give the same normalized forecast(1/2,1/2) at Gamma=(1/2,1/2).
The nonlinear native CE gradient for label0 is(-4/3,4/3). Its raw unit tangent
step is(7/6,-1/6), so the actual registered U refuses it. A fitted vertex bank
would incorrectly predict a legal Bayesian step.

The new independent degree check refuses this alias. The existing production
analyzer already refused the nonlinear heads; this is an audit counterexample,
not a claim that an old Runtime issued a false certificate.

## 4. Minimal evidence

Run `python -B scripts/audit_sparse_likelihood_analysis.py`. It reads the old
dense function directly from08fa7bc for a passive differential test, never
patching a Runtime. The [minimal report](../../evidence/minimal/FP_SPARSE_LIKELIHOOD_ANALYSIS.json)
covers every three-slot graph in GrammarLimits(3,1,1,3,3), with the script's
fixed one-source semantics:3,184 graphs times three fixed parameters times
three source points, for28,656 exact comparisons. There are28,596 affine
results and60 nonlinear refusals. The independent verifier additionally
checks21,204 banks against actual native vertex evaluations and agrees on
7,452 degree/normalizer refusals.

All five complete relation-model descriptors at n2..6 are equal to the dense
version except for their recorded derivation-operation count:

| Entities | Rank | Dense exact operations | Sparse exact operations |
|---:|---:|---:|---:|
|2|1|1,078|734|
|3|3|8,459|4,103|
|4|6|59,072|19,008|
|5|10|393,077|79,077|
|6|15|2,536,316|304,892|

These are counted algorithm operations, not hardware timings or an optimal
complexity law. The existing958 exact relation transitions, eight additional
noncontiguous clocked updates and19 negative cases pass with the new verifier.

Two bounded **development** jobs also pass through the complete Runtime on
RTX3090: profile/install and100-label reversal. Their actual worker PIDs are
22568 and24360, both attached before execution, exit0, no timeout or host-limit
termination under the existing4GiB/180-second envelope. Together they replay
587 CUDA and587 binary64 phases,194 GPU commit tapes and40 fresh scores.
Installation remains at22; reversal recovers a positive subnormal at53 and
returns to1/2 at100. These runs validate the changed implementation; they are
not relabelled as the old source-bound matrix or a new full release. They
make no useful-scale model, whole-state compression or timing claim.
