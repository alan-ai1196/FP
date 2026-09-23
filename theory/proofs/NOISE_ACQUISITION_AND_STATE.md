# Learning a common noise rate: acquisition and retained state

Status (2026-09-23): **PROVED UNDER THE DECLARED MODEL; EXACT AND FUNCTIONAL
REFERENCE/BINARY64 AUDITS PASS.** This addresses an assumption of the completed
relation experiments: they supply the noise rate. It gives a matching passive
acquisition law, a sufficient-state law and native continuations for a finite
noise prior. It changes no Foundation, ERC-1, production code or release claim.

The even-subgraph expansion used below is classical; see Jerrum and Sinclair,
[Polynomial-time approximation algorithms for the Ising model, section 2](https://people.eecs.berkeley.edu/~sinclair/ising.pdf).
We use its elementary signed form, not that paper's ferromagnetic algorithm.
The contribution here is the information/continuation boundary for FP's actual
relation task and its native learner. No new statistical estimator or graph
primitive is claimed. The earlier [forest result](RECURRENT_SELECTION_OBJECTIVE.md)
is a special case; the [finite likelihood law](LIKELIHOOD_INFORMATION_LAW.md)
already supplies the general native Bayesian construction.
The [earlier unknown-noise boundary](WHOLE_HISTORY_PREDICTIVE_STATE.md#6-rounded-confidence-and-unknown-noise-are-different-boundaries)
already identified the sufficient tuple (d,T,diagonal balance) and a future
distinction. Section 4 proves its injectivity and exact class count for a
nondegenerate finite prior; sections 5--6 supply a native execution and a
positive integer upper. The tuple itself is not a new discovery.

## 1. Declared observation law

Let Z_0,...,Z_(n-1) be independent fair bits, with the harmless common flip
anchored when representing worlds. One common unknown noise rate eta is
independent of these bits. Conditional on eta, every observed target is

    Y_t = Z_i XOR Z_j XOR E_t,       E_t ~ Bernoulli(eta),

with independent E_t. Every ordered pair, including a diagonal or repetition,
is a legal query. A causal query policy may use earlier observations and
independent randomness, but has no additional access to eta or Z. The law is
an explicit model assumption; it is not inferred from the two completed tapes.

First fix a query multigraph G with m edge occurrences. Repetitions remain
distinct edges, and a diagonal is a loop. Let B be its binary vertex-edge
incidence matrix, r=rank(B)=n-c(G), and k=m-r its cycle rank. A loop has a
zero column. Write rho=1-2 eta and sigma_e=(-1)^Y_e.

## 2. Exactly where noise information enters

Expanding the likelihood and averaging the independent vertex signs gives

    P_eta(Y=y | fixed G)
      = 2^(-m) SUM_(F subset E: B 1_F=0) rho^|F| PRODUCT_(e in F) sigma_e.  (1)

Only even-boundary edge sets survive: a product containing any vertex sign
an odd number of times has zero expectation. Loops and parallel edges obey
the same formula. The signed terms are a proof calculation, not negative
native activations or an alternative physical FP schedule.

Choose a binary matrix C whose rows form a basis of ker(B). The cycle parity
vector s=Cy determines every sign in (1). Its exact distribution is

    P_eta(s) = 2^(-k) SUM_(a in {0,1}^k) (-1)^(a dot s) rho^|C^T a|.     (2)

Every s has 2^r preimages y. Conditional on s, these labels are uniform,
independently of eta. Thus **(G,s) is sufficient for the current noise
posterior**. It is not asserted minimal: distinct s can have the same noise
likelihood. For any prior on eta,

    I(eta; Y | fixed G) = I(eta; s | fixed G) <= k log 2.                (3)

In particular a forest, with one off-diagonal observation per edge, supplies
exactly zero noise information. This is an information obstruction, even with
unlimited precision and computation.

There is also a causal version. Before each target, an edge that joins two
different existing components has a fair latent parity. The unobserved root
flip of either component remains independent and fair even conditional on
eta and the entire past. The new target is therefore fair under every eta.
Such an edge contributes zero conditional mutual information. Every other
edge contributes at most log 2. The query policy itself supplies no extra
conditional information by its premise. At a fixed finite horizon,

    I(eta; complete query/label transcript) <= E[k_final] log 2.         (4)

For an adaptive policy, do not apply (1) as an unconditional distribution of
labels given the selected final graph: that conditioning can select labels.
For the posterior of an actual full transcript, the policy's probability
factors are eta-independent and cancel in likelihood ratios; its observation
likelihood can still be evaluated by the even-subgraph sum for that transcript.

This noise-only sufficiency is **not a learner or Compiler quotient**. On the
forest 01,12, labels (0,0) and (1,0) have the same noise posterior and empty
cycle parity vector, but their next forecasts on 02 differ. With equal prior
on eta in {1/10,1/4}, their label-zero probabilities are respectively
2637/4000 and 1363/4000. Discarding forest labels loses a legal next response.

## 3. A matching acquisition law: cycle rank alone does not price learning

Consider R vertex-disjoint simple cycles of length L; L=2 can be represented
by parallel observations, and L=1 by a diagonal. The two hypotheses have
fixed rates 0<eta_0<eta_1<1/2 and equal prior. Each cycle supplies just its
parity, a Bernoulli variable with probability (1+rho_i^L)/2 of even parity.
The R parities are independent, and all other labels are noise-independent
conditional on them. Set

    a=rho_0^L, b=rho_1^L, Delta=a-b>0.

The one-cycle total variation is exactly Delta/2. More generally, if R_* is
the smallest cycle count permitting average testing error at most 1/4, then

    (1-b^2)/(2 Delta^2) <= R_* <= ceil(16/Delta^2).                       (5)

For the lower bound, the one-cycle chi-squared divergence is
c=Delta^2/(1-b^2). Independence gives chi-squared divergence (1+c)^R-1 for
all R parities. Cauchy-Schwarz implies TV <= sqrt(chi-squared)/2. If Rc<1/2,
the binomial/geometric-series bound gives

    (1+c)^R <= SUM_(j>=0) (Rc)^j = 1/(1-Rc) < 2.

Then TV<1/2, and the optimal equal-prior testing error (1-TV)/2 exceeds 1/4.
This proves the necessary lower in (5) without a numerical logarithm.

For the upper, threshold the sample mean of the even-parity indicators at
the midpoint of the two means. Under either hypothesis, variance is at most
1/(4R), while the distance to that threshold is Delta/4. Chebyshev gives
error at most 4/(R Delta^2), proving the sufficient upper.

Consequently, for fixed distinct positive rates,

    R_* = Theta(Delta^(-2)) = Theta(rho_0^(-2L)) as L grows.              (6)

The label cost is R_* L. This is a matching acquisition order for this
declared passive experiment, not a lower bound on policies allowed to choose
short cycles or direct diagonal probes. The vertex set grows to hold the
disjoint cycles. Repeated observations on the same cycle introduce additional
short cycles and do not satisfy this experiment's premise. Cycle rank R counts possible evidence
bits; it does not bound their usefulness below. In the exact audit at rates
1/10 and 1/4, L=32 needs at least 796547 cycles by (5), while the elementary
sample-mean upper is 25489486. These are rigorous conservative bounds, not
executed sample counts or sharp constants.

## 4. The sufficient native learner state changes with the model

Now register a fixed positive rational prior on a finite set of at least two
distinct rational rates in (0,1/2), and the fair anchored vertex prior.
There are finitely many rate/world pairs.
Let D=n(n-1)/2, T be actual candidate-executed observations, d_ij the signed
off-diagonal counts, and s the signed sum of all diagonal labels. Then

    m_z = [T+s+SUM_(i<j) d_ij (-1)^(z_i XOR z_j)]/2,
    w_(eta,z) proportional to pi_eta * eta^(T-m_z) (1-eta)^m_z.          (7)

Thus (T,d,s) determines the whole joint posterior and updates by one signed
counter increment per observation. No per-edge unsigned count is necessary.
Profile repetition contributes each actually executed event; T is the
optimizer-step count, not a substituted ordinary cursor.
For a profile that replays the same observation, (7) describes the algebraic
native endpoint. A replay is not an independent new noisy observation and
does not acquire fresh rate information. The calibrated posterior statement
uses ordinary observations under section 1's declared law.

At a known T this encoding is also injective on reachable posteriors. Equality
of two posteriors implies equality of their within-rate world odds at one
rate different from 1/2. The off-diagonal parity functions are distinct
nonconstant Walsh characters on anchored worlds, so their difference can be
constant only if every d_ij agrees. Comparing two distinct rates at a fixed
world then forces s to agree. Positivity of the fixed prior permits these
ratios. Complete likelihood signatures distinguish both the rate (by a
diagonal) and the anchored world (by pair queries); the finite likelihood
theorem therefore turns distinct posteriors into distinct legal future
prediction classes. Equality of current predictions alone is not used.
This quantifies over the mathematical query/label language; a fixed Runtime
budget can prevent executing a distinguishing suffix and must then report
its corresponding unresolved claim.

Put d_* = D+1. The exact reachable counter set at T is

    {x in Z^d_* : ||x||_1 <= T, ||x||_1 = T (mod 2)}.                  (8)

Every event makes one signed unit move. Conversely, execute each required
signed coordinate, then fill the remaining even number of steps with opposite
labels on one query. If shell(d,0)=1 and, for u>0,

    shell(d,u) = SUM_(j=1..min(d,u)) 2^j binom(d,j) binom(u-1,j-1),

then the exact class count is

    N(T) = SUM_(0<=u<=T, u=T mod 2) shell(d_*,u)
         = [2^(d_*-1)/d_*!] T^d_* + O(T^(d_*-1)).                     (9)

The isolated fixed-cut information requirement is therefore
(D+1) log2(T+1)+O(1) bits, matched in order by these signed counters when T
is known. At n=2 the count is exactly (T+1)^2. Complete source/program identity,
clocks, pending event/gradient, native caches, history, ownership and evidence
still have their separate costs. This is not compression of complete Omega.
This lower bound concerns exact forecasts. A fixed-error encoding needs its
own separation analysis; the earlier known-rate error lower is not transferred.

The old known-noise encoding is correct in its scope: it need not retain s in
theta. Both one-event histories (00,0) and (00,1) give the identical actual
`CountState`, including cursor/steps. In the new mixed-rate learner their
noise-1/10 posterior weights are 6/11 and 2/7, and their next diagonal-zero
forecasts are 183/220 and 111/140. Its statistic cannot omit s.

Nor may it reset when off-diagonal counts cancel. After (01,0),(01,1), d=s=0,
but T=2 and the noise-1/10 posterior is 12/37 rather than 1/2. The factor
eta*(1-eta) cancels within each fixed-rate world posterior yet is precisely
evidence between rates. These witnesses refute a reuse of the old statistic
for the new model, not an existing Runtime certificate or Foundation rule.
The complete existing Runtime retains the observations and actual clocks.

## 5. Native realization and the numerical boundary

For the audited prior on {1/10,1/4}, choose L0=20 and one selected simplex
slot per rate/world pair. For every label y and pair query, let ell_y be that
expert's declared noisy likelihood. A native feature SUM has L0*ell_y-1
copies of the corresponding pair PRODUCT, all on one fixed unit slot.
These multiplicities are respectively 17/1 or 14/4. The head weights these
features by the selected slots and adds its ordinary base one. Hence

    M_y = 20 SUM_(eta,z) w_(eta,z) ell_y(eta,z),    SUM_y M_y = 20.

The existing unit-rate, one-event simplex CE-gradient rule gives exactly (7).
It also computes the full fixed-slot derivative and complete native caches;
neither is deleted because the selected weights have a Bayesian description.
The initializer explicitly supplies a uniform joint prior. This is a new
registered G/Gamma with the existing U and source semantics, not an installed
transition from an old root or discovery of a prior from data.

The current single-rational-radix likelihood backend cannot encode this bank:
actual likelihood ratios 9 and 5/6 have independent prime-valuation vectors.
No rational radix can have both as integer powers. That is an implementation
class obstruction, not missing native expressivity or a new architecture act.

Even here an energy histogram is not mathematically necessary. For (7), put
H=SUM |d_ij|, A=(T+s-H)/2 and B=(T-s-H)/2. Reachability makes A,B nonnegative
integers. For each rate, use integer match/mismatch factors 20(1-eta),20 eta,
raise them to A,B, and multiply one |d_ij|-power edge factor selecting match
or mismatch according to the sign of d_ij. Their positive world sum is the
rate's *unnormalized* evidence. Summing the rate contributions before the final
normalization preserves the Bayes factors lost by separate normalization.
Positive elimination has the same support geometry for each rate. With this
two-rate uniform prior, the explicit total integer is at most 2^n 18^T, so
n+5T+1 bits suffice; a prospective label uses the T+1 envelope. This is an
explicit integer upper, not a universal encoding lower or an owned backend.
In particular, zero H does not remove the T-dependent rate evidence.

## 6. Minimal evidence and remaining claim

Run `python -X utf8 -B experiments/joint_uncertainty/noise_acquisition.py`.
The default compares an existing artifact without overwriting it; `--output`
can create a separate result. The [compact evidence](../../evidence/minimal/FP_NOISE_ACQUISITION.json)
checks 168 query multigraphs, 4155 exact label/rate likelihoods and their
cycle-parity fibers; 15 adaptive pre-target cuts include nine uninformative
bridges. There are 96 exact binomial testing checks, 928 full-history/count/
positive-integer comparisons, independently computed valuation ranks, and
996 complete native cache/gradient/successor checks. The small enumerations
test the derivation; proofs (1)--(9) establish the general statements.

Five ordinary Reference Runtime streams supply 13 actual observations and
44 independently replayed binary64 phases. They keep the complete categorical
pair interface, initializer slots, data and causal clocks. Their declared
normalizer/activation caps are 22/18 (the exact normalizer is 20), with 256-MiB
packed payload, 10^10 work per role and 32768-bit reference arithmetic.
They explicitly have unresolved whole-host scope: functional CPU evidence
does not establish a bounded host experiment, actual AMP or indexed release.
No search decision, fresh crossing or installation is issued.

The next experimental claim must distinguish learning a declared finite noise
prior from assuming one fixed true rate. It needs its own owned physical
realization and strong exact joint control. A forest-only interface cannot
supply that missing rate information; long-cycle passive data can require
exponentially many observations. More solver effort cannot erase either
information limit. Existing known-noise model results and their source-bound
resource outcomes retain their original meaning.
