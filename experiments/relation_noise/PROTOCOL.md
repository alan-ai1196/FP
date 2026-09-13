# RN-1: ordinary-data relation inference under conditioned and IID noise

Preregistered before target execution. This experiment follows the completed
[resource experiment](../erc1_rtx3090/RESULTS.md). Foundation/ERC-1 and the
scoped Runtime remain frozen. It studies the existing empirical-relation
solver on a changed **data law**, not a new static resource family.

## Scientific questions and fixed comparisons

Does the current Runtime propose/select/deploy a useful relation model from
ordinary noisy labels? Does successful training closure generalize to
previously unobserved relations? Keep these as different questions.
Neither train optimality nor installation is population identification.

Token counts are 8 and 16, seeds 0,1,2,3. Hidden token bits are independent
fair bits in the ideal generative model. Only the external producer and
post-prediction evaluator receive them. Training presents the oriented path
(0,1),...,(n-2,n-1), ten labels per edge. Two training laws are compared:

* `conditioned`: exactly one uniformly positioned label flip per edge.
* `iid`: independent label flips with probability 1/10.

There are 16 main cases. Two additional n=8 conditioned cases delete the
edge (3,4), and flip all hidden bits in the second component between cases.
They have exactly the same training observations and opposite unobserved
cross-component relations. They extend the existing identification control
into this evaluation, not a new Foundation case.

Evaluation visits every ordered token pair once, in a seeded permutation,
with future label-flip probability 1/10. The main generalization metric
excludes diagonal pairs and **both orientations** of every trained edge.
Thus it cannot be improved just by recognizing self-pairs or reversing a
known pair. Scores use the external world's exact 9/10 versus 1/10 target
probabilities, after actual predictions have been retained. We report
expected CE in binary64, and exact rational Brier/probability diagnostics.
No Monte Carlo label loss is substituted for this full-domain calculation.

The native candidate, when actually built, has fixed post-training values:
the registered learning rate is zero. Its gradients and clocks still run.
Compare this frozen candidate to a posterior predictor frozen at the same
training cutoff. Deployment is a **separate** prequential policy diagnostic:
the owned policy may use subsequent labels for persistence/installation.
No unavailable candidate receives an imputed score or an invented install.

## A strong implemented statistical baseline

The baseline knows the same token correspondence and the registered noise
law. It receives only revealed training contexts/labels, never hidden bits.
For IID noise, each tree edge has posterior sign mean

`r_e = (9^c0 - 9^c1) / (9^c0 + 9^c1)`.

The prior's root sign and tree-edge signs are independent. Likelihood
factorizes over observed edges, so the posterior mean relation between i,j
is the product of r_e along their path; it is zero between components and
one on the diagonal. Future label-one probability is

`q1(i,j) = (1 - (4/5) product_path r_e) / 2`.

For the **conditioned** training law, a 9:1 majority identifies the edge
sign exactly: r_e is +1 or -1. Applying the IID posterior to this different
law would weaken the baseline. Component-relative root signs remain unknown.
This posterior predictive distribution is the conditional expected-CE
minimizer under the stated prior/law. Its algorithm is an ordinary exact
forest inference control, not a new FP theorem or a target oracle.

The baseline is also executed as a finite AMP table model in a separate
fenced worker. From the computed posterior, floor each positive excess
`10*q_j - 1` to a representable nonnegative half value. Store those values
on the GPU, add base one in single, and divide by the ordered single total.
Training and evaluation use the same complete one-hot input encoding as FP;
the baseline explicitly validates/decodes it and performs an actual GPU
table gather in evaluation order. Table, addresses and batch temporaries
all contribute to its native allocator peak.
Downward value encoding makes the exact stored-mass total <=10; the
representable cap ten also bounds its rounded total. Every actual half
word, single mass/total and final division is checked independently.
This model pays for its materialized table and preprocessing; its value
constructor is declared separately from FP's local initializer (1,8).
It grants no FP search, bridge, installation or class-completeness authority.

The exact CPU posterior supplies a stronger precision control alongside
the actual AMP baseline. It is neither an untrained neural network nor an
independent-pair baseline that discards the known shared-token structure.
No claim of novelty or superiority to standard Bayesian inference is planned.

## Runtime and physical registration

Reuse the complete broad native grammar from `fixture_parameters`, including
unary SUM and direct pair-lookup competitors. Initial deployed model is
uniform, initializer (1,8), base (1,1), T cap ten, activation cap eight,
complete n-squared source domain, update unit ten, rate zero, commit grid16.
At the training boundary, one owned CUDA policy step runs the existing
empirical-upper/relation solver, then existing paired reference/CUDA
persistence and resident installation. It receives no callback or supplied
grouping, fitted coefficient, baseline forecast or external posterior.

Use the existing exact-reference integer limit 32,768, packed cap 1 GiB,
work cap 10^13 per role, CPU state/probability tolerances 2^-24, CUDA
tolerances 1/100, 4,096 output cells and 131,072 evidence bytes per phase.
FP keeps its 16 MiB arena and separate 24 GiB board envelope. Both FP and
baseline workers have a 4 GiB Windows process/job cap before entry and a
20-minute observation timeout. The baseline's measured tensor peak must
fit 16 MiB and allocator reservation 32 MiB; those are tensor quantities,
not a whole-board peak. Retain actual device/build and job identities.
No latency, speedup, all-instruction or per-model total-memory claim is
made from whole-worker CPU ticks or the board envelope.

The persistence rules use bound3, epoch1, max_epochs=n^2, alpha1/4 per
reference/CUDA path, fixed bet3/4 and the existing log/wealth precision.
Every root has its own alpha ledger. No cross-root significance claim or
familywise guarantee is inferred from repeated runs.

The ideal generative law is explicit above. Seeded Python PRNG tapes make
the executed experiment reproducible; they are finite empirical evidence,
not proof of ideal independence or of a fresh stochastic-law premise.
Runtime's stochastic law object remains an explicitly conditional external
assumption. The producer's hidden bits/tape/seed do not enter Runtime.

## Analysis fixed before execution

Retain all 18 cases and both implemented paths, including unresolved search,
absent candidates, failed persistence and any numerical/resource failures.
Record cutoff counts, proposal reason, class status, native counts, candidate
and deployed unseen-context scores, baseline exact/AMP scores, install
cursors, independent phase checks, separate resources and terminal jobs.
Do not infer population guarantees from a small seed sample.

Before target runs, exhaustively check the posterior against enumeration of
all hidden assignments on small forests, and the existing proposal gate on
all two-edge count patterns. For ten IID labels per edge and a connected
tree with e edges, the data can pass the current categorical-upper gate
only through all 9:1 splits (candidate) or all 5:5 splits (uniform baseline).
Thus the arithmetic eligibility probability is `p9^e+p5^e`, where
`p9=P(Binomial(10,1/10) in {1,9})` and `p5=P(Binomial(10,1/10)=5)`.
Resource admission and persistence can only add further failures. This
formula concerns the current solver, not information-theoretic impossibility
or the full native class. Verify its premises rather than treating the
previous conditioned tape as evidence about IID data.

Commit the protocol and code before GPU runs. Keep compact outcomes,
reproducible generators and small witnesses; no datasets, weights, full
phase logs or cache files. Any reporter correction preserves already
completed results and their original source revisions.
