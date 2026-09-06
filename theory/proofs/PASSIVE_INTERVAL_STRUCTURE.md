# Structural certificates from finite information, not an exact-table oracle

Status: **PROVED under the declared interval and sampling contracts**, 2026-09-06.
This connects the static normalized-SUM/range results to a legal finite
information interface. It does not provide candidate persistence or install
authority, and it does not assume stochastic validity for a deterministic corpus.

## 1. Exact interval criterion for robust exclusion of SUM

Keep the binary 2x2 unary-source/readout class of XVII.1 and fixed positive
context weights `w_i`. The only available target information is a nonempty
closed box

\[
\mathcal H=\prod_i[\ell_i,u_i]\subseteq[0,1]^4.
\]

The interval bounds are part of the revealed information, not convenient
point estimates. Let `D={00,11}`, `O={01,10}`. The entire box is outside the
SUM prediction closure iff either

\[
\boxed{\max_{d\in D}u_d<\min_{o\in O}\ell_o,}
\]

or the reversed strict ordering `min_D ell_d>max_O u_o` holds.

**Proof.** The complement of the SUM closure has exactly two connected
components: all diagonal probabilities below all off-diagonal probabilities,
or the reverse. A box is connected. If it avoids the closure it lies wholly
in one component, giving the extreme-endpoint inequalities. Conversely either
strict ordering directly excludes intersection of the two target intervals
for every admissible table. If neither holds, the information admits a target
in the SUM closure, so a positive-margin universal exclusion is impossible.
Exact finite PRODUCT count at a touching boundary is a different question.

The worst-case excess of the SUM risk infimum over Bayes risk is also explicit.
For the first ordering, it is the least of the four weighted Bernoulli pooling
costs evaluated at `t_d=u_d`, `t_o=ell_o`. The pooling cost decreases when the
lower probability moves up, and increases when the upper probability moves
up: its derivatives are `w_d[logit(t_d)-logit(t_bar)]` and
`w_o[logit(t_o)-logit(t_bar)]`. Thus these closest endpoints minimize each cost.
Taking the minimum over four pairs commutes with taking the infimum over the
box. Endpoint values follow by continuity.

A simpler **rational** lower certificate, sufficient without evaluating logs, is

\[
\boxed{\inf_{p\in\mathcal H}\bigl[\inf_{SUM}L_p-L_{Bayes,p}\bigr]
\ge\min_{d,o}\frac{2w_dw_o}{w_d+w_o}(\ell_o-u_d)^2>0.}
\]

This follows by writing the pooling cost as weighted KL divergences and using
`KL(a||b)>=2(a-b)^2`. For uniform contexts it is one quarter the square of the
smallest endpoint gap. This excludes the whole SUM class, including every
unreached coefficient state; it is an optimistic control, not a granted
reachable Bayes witness or an installed model.

## 2. A finite-precision transcript can remain non-identifying forever

Consider the explicitly declared hypothetical query that returns only
`1[p_i>=1/2]` for each conditional probability. The constant table

\[
p^{SUM}=(3/4,3/4,3/4,3/4)
\]

and the table

\[
p^{PRODUCT}=(5/8,7/8,7/8,5/8)
\]

both return `1111`. The first has a finite SUM-only realization. The second
is separated from the SUM closure, with excess-risk lower bound `1/64` for
uniform contexts. Unlimited computation or repetition of this same deterministic
query cannot decide which structural situation holds. The query's actual
information class requires `UNRESOLVED`, even though both targets are finite,
strictly positive, and exactly representable by the full native grammar.

This is an information-model counterexample, not permission to query exact
conditional means in a passive next-token contract.

There is also a zero-error limitation for passive samples: any finite context/
label transcript has positive probability under both of these full-support
Bernoulli tables with the same full-support context law. A decision made on
such a transcript cannot be certainly correct under both hypotheses. For
zero-error universal classification, finite evidence must remain unresolved.
An error-controlled statistical claim needs its own explicit law/allocation.

## 3. A passive, anytime-valid alternative under a stated stochastic law

Assume the **actual registered law** produces iid context/label pairs. There
are `K=4` contexts with positive probabilities; conditional labels at context
`i` are Bernoulli with a fixed unknown `p_i`. Contexts are observed passively;
the algorithm cannot intervene on inputs or read latent group/conditional IDs.
At count `n>=1` for a context, let its revealed success fraction be `hat p`.

Preregister total error `alpha` and allocate

\[
\alpha_{i,n}=\frac{\alpha}{K n(n+1)}.
\]

Choose any predictable radius satisfying
`2 exp(-2n r_n^2)<=alpha_(i,n)` and use
`[max(0,hat p-r_n),min(1,hat p+r_n)]`. An unobserved context has interval `[0,1]`.
The bounded-variable tail inequality gives simultaneous coverage for all
contexts and all counts with probability at least `1-alpha`, since
`sum_n 1/[n(n+1)]=1`. Therefore the interval criterion can be checked after
every event and stopped adaptively without new alpha or an optional-stopping
loophole. The probabilistic ingredient is
[Hoeffding's bounded-sum inequality](https://www.cs.rpi.edu/academics/courses/spring06/random/hoefding.pdf).

The audit avoids floating-point confidence-bound decisions. Let `k_n` be the
least integer with `2^k_n>=2K n(n+1)/alpha`. Choose a rational dyadic `r_n`
rounded **upwards** so `2n r_n^2>=k_n`. Since `e>2`, this gives

\[
2e^{-2nr_n^2}\le2^{1-k_n}\le\alpha_{i,n}
\]

using exact rational/integer checks. Increase dyadic precision with `n` so
`r_n -> 0`; a fixed rounding floor must not be claimed to resolve arbitrarily
small gaps. Whenever the true two target intervals are strictly separated,
positive context probabilities and convergence of empirical means imply an
eventual finite certificate almost surely. Finite no-crossing is unresolved,
not rejection. The false positive probability over all stopping times is at
most the preregistered alpha.

This evidence is discovery/structural evidence. Its labels are already revealed
and cannot be recycled as fresh candidate persistence. A fresh-data lineage
test, event-level reference/AMP relation, ownership and installation are still
independent requirements. Restarting the process does not refund alpha.

## 4. Finite-information robustness of the two-PRODUCT range phase

The reference range-phase table `p^0=(1/2,1/2,3/4,1/4)` lies in the unbounded
SUM closure, so Section 1 cannot certify its finite-range two-PRODUCT property.
Use the stronger class separation of XVII.3 instead.

At cap `R=4`, every at-most-one-PRODUCT prediction has distance at least
`d=1/28` from `p^0`; a particular two-PRODUCT witness predicts `p^0` exactly.
Suppose the revealed information certifies `||p-p^0||_infinity<=r`. Every
excluded model then has excess risk over the true Bayes risk at least
`(d-r)^2/2` when `r<=d`. The witness's excess risk is at most `16r^2/3`, because

\[
KL(p_i\Vert p_i^0)\le\frac{(p_i-p_i^0)^2}{p_i^0(1-p_i^0)}
\le\tfrac{16}3r^2.
\]

The first inequality follows from `log u<=u-1`; no unobserved target table is
substituted for a reference/AMP trajectory. Thus every excluded model loses
to this **fixed, explicit witness** by at least

\[
\boxed{G(r)=\tfrac12(d-r)^2-\tfrac{16}3r^2.}
\]

For example `r=d/8=1/224` gives `G(r)=115/301056>0`, an exact rational margin.
A simultaneous passive confidence box entirely inside that ball therefore
certifies this population risk comparison at its allocated error level.
Checking only the center estimate is invalid. These radii can require expensive
acquisition; insufficient observations give `UNRESOLVED`, not a semantic change.

If the witness is constructively reachable and feasible, this margin excludes
every at-most-one-PRODUCT epsilon-optimal target for `epsilon<G(r)` under the
same fixed task/range contract. It does not claim the witness is true Bayes
optimal after perturbing the target, or that its coefficients were learned
by an arbitrary optimizer.

## 5. Evidence boundary

The exact interval-box audit compares the criterion to exhaustive box-corner
geometry, checks the non-identifying transcript, validates the dyadic
error allocation, and exercises a seeded passive count stream. That seeded
stream is an algorithm audit; it is not empirical validation of the probability
theorem or a GPU/model-science run. Minimal evidence contains counts, stopping
cursor and certificates, not a data dump. No runtime installation API is added.

Reproduction: `theory/numerical_checks/passive_interval_audit.py`.
