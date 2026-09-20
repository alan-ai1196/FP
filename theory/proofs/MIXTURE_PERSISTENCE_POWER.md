# Finite power without a reciprocal-wealth assumption

Status: **SCOPED THEOREM; EXACT PRODUCTION-ARITHMETIC AND NATIVE AUDIT**.
This composes the [owned positive curve](OWNED_MIXTURE_PERSISTENCE.md) with
the native likelihood learner's pathwise loss bound. It changes no Runtime
rule, current experiment, validity null or physical resource declaration.
No model tape is used. A fine-precision fixed-bet control is included: power
alone does not establish that the larger adaptive state is necessary.

## 1. A pathwise comparison through rounded state

Consider one-event epochs through a finite horizon T. Each successful path i
supplies a lower score ell_(i,t) in[-B,B], with the same reference gain g_t
in[-B,B] and `ell_(i,t)>=g_t-rho`. Fix any analysis coefficient c with
`0<c*B<1`, and put

`r=1-c*rho/(1-c*B)>0`, `W_(c,t)=PRODUCT_(s<=t)(1+c*g_s)`.

This c does not change the Runtime's implicit adaptive fraction, allocate
another identity or select a component using a target. It is a comparator
for a pathwise inequality that holds for every such c. Since
`1+c*g_t>=1-c*B`, each score satisfies

`1+c*ell_(i,t) >= r*(1+c*g_t)`.

Let L_(i,t) be the exact readout of the q-bit rounded coefficient curve and
`epsilon_t=2^-q*(2^t-1)`. The earlier positive-state proof gives both the
uniform rounding bound and the classical arcsine comparison
`R_t=4^t/binomial(2t,t)<=2*sqrt(t)`. Evaluate the exact curve at b=c*B:

`L_(i,t) >= r^t*W_(c,t)/R_t - epsilon_t`.                 (1)

This is deterministic on every successful prefix. It neither divides by
previous wealth nor assumes control of its downward excursions. Different
physical score paths obey the same lower bound, without an independence
assumption or a union penalty for sharing the data. A previously crossed
statistic remains stopped; apply (1) only to a path that has not yet crossed.

With q=T+p, epsilon_t<2^-p for every t<=T. If alpha_i are the separately
spent path allocations, define `tau=max_i 1/alpha_i`. The condition

`r^T*W_(c,T) >= (tau+2^-p)*R_T`                          (2)

forces all paths to have crossed by T if their required calculations and
ordinary publication have remained available. A scalar helper satisfying
(2) does not grant an owned crossing, bridge, class certificate or install.

## 2. Native learning cost, for each fixed world

Start with any strictly positive normalized weights w_h on the finite
known-noise relation worlds. The candidate follows the existing complete
unit-rate simplex likelihood U; the baseline is uniform. The algebraic
identity, for every query/label sequence, is

`PRODUCT_t p_t(Y_t) = SUM_h w_h PRODUCT_t p_h(Y_t)`.

Here each expert p_h assigns9/10 to its relation and1/10 to the other label.
The learner's p_t need not be the true conditional label law in the argument
below. Put a=log(9/5), b=log5, and

`u=log(1+c*a)`, `v=log(1-c*b)`, `A=(u-v)/(a+b)>0`.

Concavity bounds log(1+c*g) below by its endpoint chord on[-b,a]. If N_h is
the number of labels disagreeing with world h, telescoping and the chord give

`log W_(c,T) >= (T-N_h)*u + N_h*v + A*log(w_h)`.          (3)

The last term is the cost of the learner's initial uncertainty. This is a
pathwise statement for every h with positive weight; no expectation under
the learner's posterior has been taken.

Now fix any actual world h. Assume fresh independent Bernoulli(1/10) label
noise, with each query selected before its current noise is revealed.
Queries can depend on earlier labels. Conditional on this fixed world and
the complete admission state, N_h has the Binomial(T,1/10) law. In particular
we need not assume that the actual world was drawn from w. This differs
from the old reciprocal-contraction argument, which did need that mixture
law and had an explicit fixed-world counterexample.

Let k_h be the largest integer in[0,T] satisfying

`(T-k_h)*u+k_h*v+A*log(w_h) >= log((tau+2^-p)*R_T)-T*log(r)`,

and put k_h=-1 if none qualifies. Write C_T(k) for the exact binomial CDF,
with C_T(-1)=0. Let F_T denote an operational, numerical, score-premise or
ordinary-publication failure before the required paired crossing/horizon.
Equations (1)-(3) imply

`P_h(F_T OR all required paths cross by T) >= C_T(k_h)`.   (4)

If failure is impossible under an independently established premise, (4)
is a crossing-probability bound. Otherwise a lower bound on crossing alone
subtracts P_h(F_T). We never condition on whichever runs happened to finish.
For an actual world law pi, average with pi, not automatically with w. A
worst-world bound takes the minimum over h. Uniform initial w makes (4) the
same for every supported fixed world and every mixture over those worlds.

## 3. Concrete finite bounds and the growing-horizon limit

Use B13/8, rho1/98 and alpha1/4 per path. The existing successful AMP and
12-term lower-log premises imply this rho; they still require execution and
checking. For the fixed analysis comparator c1/3, b=c*B=13/24 and r535/539.
These values are chosen without a retained model tape. The audit verifies

`(9/10)*u+(1/10)*v+log(r) > 0.07669`.

With a fixed finite positive initial weight vector and p fixed, the RHS
threshold grows only as O(log T), whereas the distorted typical log wealth
grows linearly. Equivalently, k_h/T tends to
`(u+log(r))/(u-v)>1/10`; the exact binomial law makes the lower bound in (4)
tend to one. This is a family of finite declarations q=T+p. It is not an
almost-sure theorem for one fixed-precision Runtime, free alpha on restarts,
or a physical completion guarantee. The curve's constructive work/payload
bounds remain polynomial in T and p; actual host and learner costs remain
separate. The analysis coefficient6/13 also has positive distorted growth,
above0.06120, despite its failed reciprocal-contraction lemma.

For p32, exact binomial sums give the following lower bounds, rounded down.
No training or evaluation tape enters these uniform-prior examples.

| Horizon | Initial worlds | Mixture bound | Fine-grid fixed control |
|---:|---:|---:|---:|
|64|2|0.692170|0.897213|
|64|128|0.372705|0.692170|
|128|2|0.947620|0.991712|
|128|128|0.861239|0.970213|

Each cell is a crossing-or-failure lower bound for every supported fixed
world under the stated noise law. The mixture uses coefficient grids96/160;
the fixed control uses scalar wealth grids96/160. None is an empirical
success frequency, a prediction for the fixed n8 tapes, or an installation.

## 4. Is the adaptive curve necessary for this power argument?

No. For a declared fixed factor1+c*ell, let S_t be scalar wealth rounded
down to q fractional bits. Its exact-product error satisfies

`0 <= PRODUCT(1+c*ell)-S_t <= 2^-q*(2^t-1)`,

because each nonnegative factor is at most1+c*B<2 and each floor loses less
than2^-q. Thus `S_t >= r^t W_(c,t)-epsilon_t`. The same proof applies with
R_T removed from (2) and from the noise cutoff. The last table column uses
this stronger matched-comparator lower bound and the actual existing
`next_wealth` arithmetic. It does not retain the old16-bit floor as a weak
comparison. The statistical state of the fixed procedure is one rational,
while the implemented mixture retains T+1 coefficient integers. This is
not a comparison of complete Compiler host/provenance costs.

The mixture's separate benefit is simultaneous pathwise comparison with
every fixed coefficient, at its explicit regret and state cost. Neither
these lower bounds nor the small CPU fixture prove that benefit is worth
the resources on a model task. The better control bound also does not order
the procedures' actual first-passage probabilities. Power-only reasoning
cannot select an adaptive curve as the uniquely necessary design.

## 5. Exact audit

Run `python -B experiments/joint_uncertainty/mixture_persistence_power.py --write`.
The [minimal evidence](../../evidence/minimal/FP_MIXTURE_PERSISTENCE_POWER.json)
contains2,430 production curve compositions and2,430 fine-grid fixed-control
compositions, with independent signed-monomial mixture readouts. The native
audit executes all64 six-label words from each of two initial world-weight
states, including a nonuniform one and queries that depend on earlier labels.
It checks768 complete native units,3,072 worldwise compositions and1,536
production lower-score/curve checks, with matching fixed-control checks.
The second score path is a rational pre-target probability perturbation
inside the error tube, explicitly not an actual AMP execution.

Threshold cutoffs use independently verified exact log intervals and96-bit
outward rational arithmetic; an overlapping sign would return unresolved.
The audit also checks positive distorted growth for6/13 without assuming
reciprocal contraction. No new Runtime path, GPU worker, model result,
Foundation rule or ERC-1 release is introduced.
