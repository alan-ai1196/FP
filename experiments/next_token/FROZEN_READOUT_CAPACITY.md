# What the current token model can express

Status: **PROVED SCOPED MODEL-CLASS BOUNDS; EXACT/CPU AUDIT PASS**. This
inspects the existing positive token head and resource-test graph before
selecting a language model. It changes neither that graph nor Gamma/U, opens
no corpus and supplies no model score, Runtime authority or Foundation change.
The rational/relation branch remains closed. Stop this scope audit here and
use it when preregistering the actual text comparison.

## 1. A frozen positive head is a finite mixture

The existing compact token readout has

    m_y(x) = b_y + sum_i W_yi f_i(x),
    p_y(x) = m_y(x) / sum_v m_v(x),

with b_y>0, W_yi>=0 and K nonnegative features. Fix the entire learner during
the reporting stream. Define B=sum_y b_y, c_i=sum_y W_yi, and distributions

    q_0(y)=b_y/B,     q_i(y)=W_yi/c_i for c_i>0.

Then p(x) is a convex combination of these fixed distributions, with weights
B/Z(x) and c_i f_i(x)/Z(x). Zero columns contribute no *current* mass; they
remain owned, individually decodable and trainable parameters. Removing a
zero column from this algebraic decomposition does not authorize pruning it
or its future gradients from a learner.

There are R<=K+1 components, regardless of the depth or PRODUCT count inside
the core. Hence any finite context-by-label matrix of these native forecasts
has nonnegative rank at most R. No latent variable or new execution action
is added: this is an algebraic identity of the existing normalized SUM heads.
It is not a rank bound on all FP programs, which need not use this particular
shared K-feature readout.

For a concrete scope check, native FP can instead place the lag1 token atom
directly in its matching label's SUM: m_y=b_y+s*1[x_1=y], with one shared
positive slot s and V readout edges. Across the V possible previous tokens,
the probability matrix is (s I + 1 b^T)/(s+B), with determinant
(s/(s+B))^(V-1)>0. It has full rank V. This does not contradict the lemma:
its distinct primitive head features are not an eight-feature shared bank,
and the native graph does not require a dense V-by-V parameter matrix.
This witness grants no new indexed Runtime lowering or language-model result;
it prevents mistaking the current backend's chosen family for all of FP.

## 2. A loss floor that can audit a reported result

Let M_y=max_j q_j(y), C=sum_y M_y and r_y=M_y/C. Then

    1 <= C <= R <= K+1,       p_y(x) <= M_y = C r_y.

For any fixed finite reporting tape, with empirical target distribution nu,
the mean native cross-entropy obeys

    mean[-log p_target(x)] >= sum_y nu_y[-log M_y]
                           = H(nu) + KL(nu || r) - log C
                           >= H(nu) - log C
                           >= H(nu) - log(K+1).

Take the maximum with zero if using the last coarse bound. The first inequality
is pointwise and the next is Gibbs' inequality; no stochastic law, independence,
causal inference or population generalization premise is needed. The first
bound even permits an oracle choice of mixture weights on every event, so it
is conservative for the actual core and its normalizer/range limits.

H(nu) is the entropy of the *reporting targets*, equivalently an empirical
oracle unigram loss. It is not a trained, resource-feasible baseline and must
not replace the tuned n-gram and competitive Transformer comparisons. No
reporting entropy is used here to select K, and no new reporting tape is read.
The bound is not a claim of learnability or optimizer reachability at equality.

The resource fixture has K=8. Every frozen native head in this class therefore
satisfies mean CE >= H(nu)-log 9, with log 9 approximately2.1972245773 nats.
For its *initial* W, a complete all-column calculation gives

    C = 8067382656276029006106288799 / 4910588715616804008951140238
      ~= 1.6428544770,
    log C ~= 0.4964352636 nats.

That initial constant is not a bound on a later learned head. Its small value
records overlap among the initialized output distributions, not measured
language quality. Corpus frequency, learned W and the actual attainable
feature gates still determine the eventual result.

## 3. What survives the actual half/single readout recipe

Do not transfer a real-arithmetic rank identity through arbitrary rounding.
For the registered token recipe there is, however, a uniform *loss* allowance.
The argument uses the actual frozen rounded readout weights and bases, not an
assumed equality between native and AMP learned masters.

Let w'_yi be the binary32 value obtained from the stored uint32 master with
grid p<=32, b'_y the actual positive binary32 base, and z_i the actual finite
nonnegative half feature. Define ideal masses A_y=b'_y+sum_i w'_yi z_i.
They have the same K+1-component mixture identity. Every nonzero w' is at
least2^-32 and every nonzero half feature is at least2^-24, so a nonzero
readout product is at least2^-56. It cannot underflow in binary32. These are
properties of this registered master/feature representation, not arbitrary
real operands or arbitrary floating models.

For gradual RNE32 and finite outputs, each product has relative error at most
u=2^-24. Each nonnegative addition has the same bound: below the smallest
normal value, two stored binary32 operands sum exactly on the subnormal grid.
The registered balanced reduction has at most h=ceil(log2 K) addition levels;
there is one multiplication and one final base addition on a term's path.
With d=h+2, alpha=(1-u)^d and beta=(1+u)^d, positivity gives

    alpha A_y <= m_y <= beta A_y.

The proper physical distribution uses S=sum_y m_y, so

    p_physical(y|x) <= (beta/alpha) A_y/sum_v A_v.

Apply section2 to the ideal head defined by the *actual* b' and w'. Its loss
floor weakens by at most

    delta_K = d log((1+u)/(1-u)).

For K=8, delta_K is approximately5.9604645e-7 nats. This does not compare the
physical predictor with the separately trained native predictor, authorize a
bridge, imply exact physical nonnegative rank, or normalize division by stored
Z. Proper normalization, frozen actual operands, finite outputs, the registered
recipe and its rounding behavior remain premises. The current CPU controls
check the extreme master/grid cases and a positive subnormal base; they are
not a new GPU execution result. No new Runtime solver is needed for this
model-scope consequence.

## 4. The resource fixture's actual context restriction

`text_model_fixture()` factors the existing model definition out of the
corpus-reading helper without changing a parameter. Write e_k(v) for its
declared embedding coordinate and x_l for lag l. Its eight selected features
are exactly

    h_k = c_k sum_(l=1)^512 e_k(x_l),
    g_k = h_k e_((k+1) mod 4)(x_1),       k=0,1,2,3.

Thus its core sees the newest token and a pooled multiset of the whole window,
including declared PAD. It is not purely a bag-of-tokens model: each PRODUCT
has a direct newest-token parent. But for every parameter value it is blind
at the current prediction to permutations of older tokens that keep x_1 and
the window multiset fixed. Its initial c_k=1/512 makes h_k a mean; learning
c_k can scale the pool but cannot untie the lags. Larger context does not
remove this restriction. Distinct lag-sensitive SUM slots already exist in
the native grammar; no semantic action is needed to express richer order.

This is not a sufficient-state quotient. Moving the oldest token within the
window can leave the current prediction unchanged and change the prediction
after the same next token is appended, because different tokens are evicted.
The exact full-V/context512 control demonstrates this in the actual initializer,
while retaining every original source coordinate. Keep the complete ordered
source history and all continuation information.

## 5. The frozen premise is essential

Even the coarse H(nu)-log(K+1) floor is false for an entire run whose head
updates over time. An exact native example uses K=1, constant feature1,
b=(1,1,1), zero Gamma, projected mean-CE SGD with eta16, unit1 and grid2^-16.
Its tape contains256 zeros, then256 ones, then256 twos. Each forecast precedes
its target and the ordinary U is applied after each target. The certified
prequential mean loss lies in

    [0.1900885702749, 0.1900885702759] nats (outward-rounded display),

below the invalid whole-run frozen floor log(3/2)~=0.4054651081. This is a
necessary-premise counterexample, not a new task experiment or a claim of
Runtime/GPU reachability. It uses the already refined exact native readout U.
The floor applies separately wherever the relevant head remains fixed, and
to the terminal frozen-reporting path; it cannot be pooled across changing
heads without a new argument.

## 6. Consequence for the next experiment

Do not turn the current resource fixture automatically into the selected
language model. A positive or negative result on it would concern its supplied
pooled/newest-token core, its narrow positive head and its declared U—not the
whole FP grammar. The first text preregistration must identify the actual
graph's context invariances, feature width, initialization, update schedule
and budget. Keep the full vocabulary and strong baselines. Choose those
coordinates from the measured feasible execution; do not use held-out results
to retrofit a favorable class or claim that a source interface alone supplies
a rich language representation.

The exact audit exhausts729 three-label/two-feature integer heads,19683
pointwise probability bounds and2187 empirical entropy inequalities. Sixty
CPU recipe controls check180 label bounds. The full resource fixture's shape,
initial column bound, newest-token dependence and future-visible ordered
history are checked without opening the corpus. The updating counterexample
uses768 exact native events and guarded logarithm enclosures. Minimal evidence:
`evidence/minimal/FP_FROZEN_READOUT_CAPACITY.json`; executable audit:
`scripts/audit_frozen_readout_capacity.py --write`.

This closes the present model-scope question. It does not add a precision
sweep, alternative architecture menu or further relation-task study. The live
resource run keeps its original contract and remains unscored. Actual token
reporting qualification and an affordable, preregistered text comparison are
the next experimental work.
