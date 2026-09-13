# Empirical sign obstruction in a joint orientation learner

Status: **scoped theorem about the v5 emitted family**, with an independent
exact scalar/graph audit. It is not an impossibility theorem for FP, its full
native grammar, or future legal reconstruction. Foundation R4 and ERC-1 do
not change. The [RN-5 protocol](../../experiments/joint_uncertainty/PROTOCOL.md)
uses the obstruction as a declared diagnostic, before target execution.

## 1. A wrong internal sign survives every parameter update

Fix the empirical components C and representative bits h used by the
[joint polynomial constructor](JOINT_POLYNOMIAL_PROPOSAL.md). Let s be the
actual latent bits and define residual signs `e_i=h_i XOR s_i`. The only
learned within-component parameter is the shared nonnegative scale t.
On a one-hot pair inside a component, the probability of the empirical
parity is `(1+t)/(2+t)`.

**Theorem.** Whenever e_i differs from e_j inside a component, the probability
of the true parity is `1/(2+t) <= 1/2` at every nonnegative learner state.
No legal positive-rate update, zero-weight revival or change to the joint
cross-component amplitudes corrects that sign within this emitted graph.

The formula is the proof. Quantized reference and actual AMP paths preserve
nonnegative parameters and the nonnegative native excess on the same head;
provided the phase completes its numerical contract, the same ordering holds
for its properly normalized masses. This says nothing about an unexecuted
or rejected phase.

Let epsilon in (0,1/2) be the later independent label-noise probability and
`H(q)=-q log(q)-(1-q) log(1-q)`. If a forecast gives the true parity probability
p, expected CE is `-(1-epsilon)log(p)-epsilon log(1-p)`. Its minimum over p>0
is H(epsilon); over p<=1/2 it is log(2).

For a component with residual-sign counts a_C and b_C, there are 2*a_C*b_C
wrong ordered within-component pairs. Therefore, over any stream presenting
every ordered pair once, even with different learner parameters at every cut,

`mean expected CE >= H(epsilon) + [2 SUM_C a_C*b_C / n^2] * [log(2)-H(epsilon)]`.

This is a prequential bound for this fixed emitted graph, allowing arbitrary
parameter updates between queries. It also holds if its deployment is
preceded by uniform predictions, since those cannot beat H(epsilon) elsewhere
or log(2) on the wrong pairs. It does not bind a deployment that switches to
a different graph capable of revising those empirical signs.

## 2. A stronger fixed-state obstruction across components

At one fixed learner state, write `w_H=a_H+a_H^2`, `Z=2+SUM_H w_H`. For distinct
components C,D, let

`Q_CD = [1+SUM_{H: flip_H(C)=flip_H(D)} w_H] / Z`.

For a pair i in C and j in D, the true-parity forecast is Q_CD when e_i=e_j
and 1-Q_CD otherwise. Thus all members of an empirical component share the
same cross relation up to its fixed representative sign. Recoverable and
transitive joint weights do not remove that internal identification.

Set `L_CD=a_C*a_D+b_C*b_D`, `m_CD=|C|*|D|`, and
`q_CD=epsilon+(1-2*epsilon)*L_CD/m_CD`. Averaging the expected loss over this
ordered block is exactly the binary CE with target q_CD and prediction Q_CD,
and is therefore at least H(q_CD).

Inside components the same t is shared. Let
`W=SUM_C |C|^2`, `L=SUM_C (a_C^2+b_C^2)`, and
`q_in=epsilon+(1-2*epsilon)*L/W`. The within-block mean loss is the CE between
q_in and `(1+t)/(2+t)`, hence at least H(q_in). In particular q_in>=1/2.
Combining the blocks gives the following bound on the **fixed-state uniform
full-domain risk**:

`risk >= [W*H(q_in) + SUM_{C!=D} m_CD*H(q_CD)] / n^2`.

The proof relaxes the shared orientation weights to independent Q_CD values,
so no claim of joint attainability or architectural optimality is required.
This also bounds a next query sampled uniformly from the full domain
independently of the history, conditional on the current learner state.
It must not be used for the aggregate of a fixed permutation's forecasts at
different evolving states; those queries need not have one common Q_CD.

## 3. Registered wrong-majority diagnostic

RN-5's selected n8,c4 tape has one incorrect internal sign in a size-two
component, with all actual latent bits zero. The residual counts are (1,1)
in that component and (2,0) in each of the other three. Thus W=16, L=14,
q_in=4/5 at noise 1/10. Ordered cross blocks involving the damaged component
contain 24 pairs with q_CD=1/2; the other cross blocks contain 24 pairs with
q_CD=9/10. The fixed-state lower bound is

`H(4/5)/4 + 3*[log(2)+H(1/10)]/8`.

The valid evolving-stream lower bound is weaker:

`H(1/10) + [log(2)-H(1/10)]/32`.

Report these scopes separately. A measured prequential score below the first
expression would not refute the theorem. The selected tape has positive
likelihood under IID noise, but its deliberate selection establishes no
frequency or population-risk claim. The adaptive full-assignment posterior
retains both signs after these finite counts and is a strong comparator;
it is not asserted to be the Bayes oracle of the hand-selected distribution.

The original observations and full native decision class remain owned by
Runtime. V5's one proposed family and the one-search experimental policy can
be inadequate while the Foundation information principle remains satisfied.
A later lawful construction may use the retained evidence to change the
within-component relation; no new semantic architecture action is necessary.

## 4. Evidence boundary

`experiments/joint_uncertainty/joint_trajectory.py` independently reduces
actual native forward/reverse graph interpreters on one-hot inputs. It checks
1,224 forecast/successor combinations across exact reference, binary64 and
rounded AMP, rates 1 and 4, including a unit-valued fitted scale, tied counts,
and changing parameter states. Its extra 64 exact fixed-state controls check
the wrong internal probability bound and complementary cross forecasts.
These are synthetic algebraic audits; they inspect no new RN-5 seed labels
and supply no Runtime state, prediction, evidence or installation authority.
The proof precedes new target-model results.
