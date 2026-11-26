# Cold attention: learned witness composition and finite certificates

## Sources and actual coverage

- Mostafa 'Neo' Mohsenvand, **Attention at Absolute Zero**, MIT Media Lab author affiliation.
- Primary edition: [arXiv 2611.11937v3](https://arxiv.org/abs/2611.11937v3), submitted November 9 and revised November 19, 2026. [PDF](https://arxiv.org/pdf/2611.11937v3) and [complete source](https://arxiv.org/src/2611.11937v3).
- Pro-B, November 26, 2026, Shanghai. **Fully read:** all 51 physical pages, main Sections 1–9, Methods, Supplementary Notes 1–6, all proofs and scientific footnotes, nine main figures and Extended Data Figure 1, four named supplementary tables, five unnumbered tables and all 62 printed references. Read the complete active `main.tex`, including the 213-entry forecast table. Visually inspected every figure-bearing PDF page: 4, 5, 8, 10, 11, 14, 15, 16, 19 and 26.
- The four named tables appear in order 1, 2, 4, 3. There are five independent numbered mathematical results, namely Propositions 1, 3, 4 and Theorems 2, 5. Theorem 5 uses manual headings rather than a theorem environment. The source contains no numbered algorithm. The ten figure insertions use ten distinct assets.
- V1 had the title *Attention Is Only as Good as Its Witnesses*. V3 corrects Supplementary Table 4's shared-block column to the final 97.20% result. V1 is not separately credited as a full read and its experiments reused in v3 are not new independent replications.
- Author-listed code: [cold-attention](https://github.com/NeoVand/cold-attention), with the earlier [witnesses repository](https://github.com/NeoVand/witnesses). Code, model archives and Lean proofs were not executed or audited here. This is an ordinary preprint, not an official OpenAI or Anthropic result. The author discloses extensive AI assistance with implementation, proof and manuscript preparation.
- The main reader read the entire paper. Bounded support covered the mathematical interfaces, empirical/version distinctions and visual inventory. Historical theorem dependencies were checked only at the specific scope recorded below. Full reading, source-grounded analysis, author-reported certification and independent formal verification are distinct.

**Assessment.** The strongest construction combines three choices: relational witnesses are joined explicitly, numerical quantities enter a restricted block through comparisons, and recurrent state can be rebuilt from discrete decisions. For a small monotone subclass, a trained network becomes a finite local rule table that supports a proof for every graph size and an explicit loop budget. These are useful computational and certification mechanisms. The paper does not prove that answer supervision reliably finds them. Its general CLRS model, fully cold models, hybrid model and language reader are different systems with different claims.

## 1. The computational object is a pair state and a middle witness

For every ordered pair of items \((i,j)\), retain a state \(z_{ij}\). A channel learns two tests on the legs through a possible middle item \(k\):

\[
A_\ell(i,k)=[a_\ell^\top\operatorname{norm}(z_{ik})+\alpha_\ell>0],
\qquad
B_\ell(k,j)=[b_\ell^\top\operatorname{norm}(z_{kj})+\beta_\ell>0].
\]

Its count is

\[
N_\ell(i,j)=\sum_k A_\ell(i,k)B_\ell(k,j).
\]

This is a join of two binary relations on their shared middle variable. It can test existence, compare two families of witnesses, or select an optimal admitted witness. A count-channel pair returns two bits, \([N_{2r-1}>N_{2r}]\) and \([N_{2r-1}=N_{2r}]\). It does not return the complete count as recurrent numeric state. With numeric registers, channels compare the best admitted value and its multiplicity lexicographically. [Sections 3–4, Methods, Extended Data Figure 1]

The useful representational change is from a single item's summary to a table of relationships that can be composed. The recurrent weights are shared across loops. For fixed channel count the pair table costs \(O(n^2)\) storage and a direct join costs \(O(n^3)\) per channel per loop. Exact counts can require \(O(\log n)\) bits even if only comparison bits are returned. The paper does not supply input-size-independent total memory or a constant-bit implementation of arbitrarily large exact counts.

### Four systems that must remain separate

| System | Recurrent information and number access | Main evidence |
|---|---|---|
| General block | Embedded numbers, continuous carried pair state, count/compare bits and real best-witness strengths | Broad CLRS-30 accuracy |
| Full cold block | Exact numeric registers accessed through comparisons, state rebuilt from input and bits, with kept or free bits according to task | Exact controlled extrapolation, recoding invariance and conditional termination |
| General-and-cold hybrid | Two complete blocks, cold-to-general coupling and two readouts | Shared multi-task and deep-graph experiments |
| Language-task monotone block | Three kept bits per mention pair, tied-leg tests with nonnegative bit weights, positive-only readout | Learned relation composition and finite all-size certificates |

The general block's 128 channels comprise 64 count channels yielding 64 verdict bits and 64 real best-witness channels. It has 146,552 shared parameters. The two-block hybrid has 293,104. Its best-witness half in the general setting returns a continuous strength, interpolating between a minimum of two leg strengths and their product. Thus the general model already uses exact comparisons in one half, but is not the fully cold bit-rebuilt model. [Figure 4, Methods, Supplementary Note 2]

## 2. The zero-temperature limit retains an optimum and its multiplicity

For a finite nonempty witness family, let

\[
Z_T=\sum_w e^{s(w)/T},\qquad
s^*=\max_w s(w),\qquad
g^*=\#\{w:s(w)=s^*\}.
\]

Proposition 1 gives

\[
T\log Z_T\longrightarrow s^*,\qquad
e^{-s^*/T}Z_T\longrightarrow g^*.
\]

The resulting interface retains \((s^*,g^*)\). Independent composition adds scores and multiplies multiplicities. Disjoint alternative families select the larger score and add multiplicities on a tie:

\[
(s,g)\otimes(t,h)=(s+t,gh),
\]

\[
(s,g)\oplus(t,h)=
\begin{cases}
(s,g)&s>t,\\
(t,h)&t>s,\\
(s,g+h)&s=t.
\end{cases}
\]

The empty family is represented by \((-\infty,0)\). This is a concrete algebra for composing optimal witnesses with multiplicity, related to the cited layered tropical structures. For strict lexicographic inequality between two limit pairs, the warm sums have the same ordering at sufficiently small temperature. The required temperature can depend on the particular witness families. [Methods Proposition 1, Supplementary Note 1]

Equal limit pairs do not identify the complete finite-temperature sum. The source's families with scores \(\{0,-1\}\) and \(\{0,-2\}\) have the same cold pair and different warm sums. Likewise, a product or union counts the witnesses supplied by that construction. Without a uniqueness or disjointness argument it need not count distinct semantic paths. The cold interface intentionally discards suboptimal-score information.

The paper separates three mechanisms behind failures at increased input size: mass dispersed over more competitors, insufficient learned score resolution between nearly tied items, and continuous recurrent errors carried through more loops. These are supported by different controlled examples, not proved as an exhaustive classification of attention failures. Direct comparison removes a learned numerical-ranking problem from the relevant block. It is a stronger primitive that must be counted as part of the architecture. [Section 3, Figures 1–3]

## 3. Invariance can be built into the interface before training

Theorem 2 restricts numerical access: learned state receives only comparison bits. If every pair of compared quantities transforms by the same strictly increasing map, all these bits are invariant. Induction then preserves the rebuilt states, the readout and the stopping decision for every choice of learned weights. It proves invariance whether or not the model answers correctly. [Methods Theorem 2, Supplementary Note 1]

For ordered keys, any strictly increasing recoding preserves order and ties. For route sums, a positive rescaling and vertex potential give

\[
W'(u,v)=\gamma\bigl(W(u,v)+\phi(u)-\phi(v)\bigr),\qquad\gamma>0.
\]

Every route from \(u\) to \(v\) then has transformed value

\[
R'(u,v)=\gamma\bigl(R(u,v)+\phi(u)-\phi(v)\bigr).
\]

Only comparisons between routes with the same endpoints cancel the potential. This symmetry therefore constrains which registers may meet at a comparison. It is a constructive wiring principle, rather than an empirical hope that data augmentation teaches numerical invariance.

The result uses exact arithmetic. A floating-point recoding that collapses two ordered values or changes a route-sum comparison need not satisfy the premise. The reported orbit tests changed none of 5,303,808 answers across 41 models, while a general Bellman–Ford model changed up to 636 of 2,048. These are finite numerical checks of selected transformations, not a proof that arbitrary finite-precision transformations preserve all comparisons. [Section 5, Supplementary Note 2]

## 4. Rebuilding discrete state gives a termination argument with explicit feedback limits

The cold architecture distinguishes kept bits, comparison bits and improving numeric registers. Kept bits only turn on. Register updates lower a route or bottleneck value when an admitted witness improves it. Learned comparison bits are withheld from the state used by the next comparison half and the register-grow step. A separate rebuild still exposes them to the best-witness half and readout. The delay structure matters. Merely rounding an arbitrary recurrent network does not give the stated theorem. [Section 4, Methods, Supplementary Note 1]

For the register-free kept-bit case, the source bounds rest by the available number of bit additions plus two loops. With registers and the source's no-negative-cycle conditions, only finitely many improving route values occur below the current bound. Let \(M\) bound the total possible changes of kept bits and registers. Three consecutive quiet loops force a full fixed point, yielding the reported \(3M+3\) bound. The Prim variant additionally accounts for hop-count resets when its bottleneck registers change. [Proposition 3]

There are two qualifications that preserve the construction's meaning:

1. A kept-bit update is **inflationary**, but arbitrary learned tests need not be monotone as functions of the other bits. A newly set bit can close a test with a negative coefficient. The least-fixed-point interpretation applies directly to the nonnegative-test subclass and to the explicit CSP construction.
2. Finite termination is not a uniform small polynomial loop bound for arbitrary real input weights. The experimental fallback at \(4n\) was not triggered on the reported tests, which is narrower than a worst-case theorem.

DFS, topological sorting and strongly connected components use free-bit loops without kept bits, and are read after \(n\) loops in the relevant cold experiments. Proposition 3 does not certify their convergence. Proposition 4 uses a parallel-circuit simulation and P-completeness to rule out an all-graph DFS solver with polylogarithmically many loops unless \(\mathrm{NC}=\mathrm P\), under its circuit and precision assumptions. It does **not** establish an \(\Omega(n)\) lower bound or prove that each DFS step requires one loop. [Methods Proposition 4, Supplementary Note 1]

## 5. A constructive compiler for bounded-width constraint propagation

Theorem 5 studies a fixed finite constraint language \(\Gamma\) on a fixed finite domain \(D\), with no positions or unique identifiers supplied to break graph symmetries. The positive construction is particularly concrete for binary constraints. Store the value pairs already excluded:

\[
F_{xy}\subseteq D^2.
\]

Increasing knowledge then corresponds to setting more bits. A value pair \((a,b)\) is excluded at \((x,y)\) if some variable \(z\) leaves no compatible middle value:

\[
\exists z\ \forall c\in D:\quad
(a,c)\in F_{xz}\ \lor\ (c,b)\in F_{zy}.
\]

The universal condition can be compiled into two separately testable legs:

\[
\forall c\,[P(c)\lor Q(c)]
\iff
\exists U\subseteq D:
\left(\bigwedge_{c\notin U}P(c)\right)
\land
\left(\bigwedge_{c\in U}Q(c)\right).
\]

For every \((a,b,U)\), one channel tests the first conjunction on \((x,z)\), the second on \((z,y)\), and keeps a bit when a witness exists. This needs \(|D|^2 2^{|D|}\) channels, independent of the instance size but exponential in the fixed domain size. A per-pair network merges channels into the excluded-pair set. [Supplementary Note 6, State and Update]

A useful implementation detail is the Boolean code \((+1,-1)\) versus \((-1,+1)\). Each logical bit contributes the same mean and squared norm, so normalization has a fixed scale on the constructed states. Conjunctions remain exact thresholds rather than being distorted by a varying normalization denominator. The proof uses expressive finite Boolean/ReLU maps to establish the existence of weights, not their acquisition by gradient descent.

The update is monotone and inflationary. At rest its surviving pairs form the appropriate local-consistency reduct. For a bounded-width binary template, the cited collapse theorem makes nonemptiness sufficient for satisfiability. Rejection occurs when every value of a variable is ruled out. The source bounds rest by \(n^2|D|^2+2\) loops. For two-valued implications, splitting a path at its middle shows that loop \(t\) composes paths up to length \(2^t\). Contradictions of depth \(L\) are consequently detected within the corresponding \(\lceil\log_2L\rceil\) propagation depth. [Supplementary Note 6, Correctness and Loops]

Higher-arity constraints require more than pair projections. The source introduces a token for each constraint \(C\) and copies its excluded tuples on incidence pairs \((C,x)\). The storage and loop count include \(\sum_C r_C|D|^{r_C}\), with \(r_C\) the constraint arity. The claimed bound is

\[
n^2|D|^2+\sum_C r_C|D|^{r_C}+2.
\]

This is not the binary construction operating on unchanged pair-only inputs. Allowed-tuple labels and incidence places are part of the supplied representation.

The converse uses a fixed-dimensional Weisfeiler–Leman/counting-logic ceiling. A position-free block whose output depends only on the stable fixed-dimensional refinement cannot decide every instance of a template outside bounded width. The paper imports the relevant counting-logic and CSP theorems. Its transfer through the higher-arity incidence interpretation is explicitly a sketch, requiring a fixed-dimensional finite-copy interpretation without added input order. Merely calling an architecture position-free does not establish the refinement bound. Position features, task-specific numeric primitives or a growing refinement dimension change the premise. The main CLRS network has position inputs, so the converse cannot be imposed on it without checking the encoding. [Supplementary Note 6, Setting and Ceiling]

**What is obtained:** an explicit implementation of a known consistency algorithm in the witness architecture, a source-conditional characterization of the position-free CSP interface, and empirical learning of two bounded-width examples. The construction does not prove that answer-only training learns all bounded-width templates or provide a sample-complexity guarantee.

## 6. Trained finite rules can support a proof for every size

The strongest certificate applies to the small language-task subclass. For a pair's finite input pattern \(p\) and set \(S\) of kept bits, a learned test has the form

\[
T_c(p,S)=\left[b_{c,p}+\sum_{j\in S}w_{cj}>0\right],\qquad w_{cj}\ge0.
\]

The pattern records the relation of the two mentions, same-person information and question membership. With tied legs, a loop has the form

\[
S^{t+1}_{ij}=S^t_{ij}\cup
\left\{c:\exists k,
T_c(p_{ik},S^t_{ik})\land T_c(p_{kj},S^t_{kj})\right\}.
\]

The readout is also monotone in the kept bits. The complete local table has size controlled by the number of patterns, channels and \(2^m\), where \(m\) is the fixed kept-bit count. Its enumeration does not depend on the number of graph items. This practicality relies on the very small \(m\) used here. [Section 8, Supplementary Note 5]

### 6.1 Safety by a finite abstract template

For a no-instance, classify people according to whether they are reachable from the question's first person \(X\). The second person \(Y\) is unreachable, and no parent edge runs from a reachable person to an unreachable one. A fixed template contains the possible mention roles in the allowed statement types and the question. Run it to rest.

Map every concrete mention to its template role. The finite rule table is checked for each input-pattern change that this mapping can create. Together with nonnegative bit weights, this establishes a simulation invariant:

\[
S^t_{ij}\subseteq S^*_{f(i)f(j)}.
\]

If the template still answers no, every simulated no-instance answers no. The required pattern-transfer check is substantive. A generic homomorphism slogan would be false because the source's same-person feature excludes the same mention and can change when two mentions are merged. [Supplementary Note 5, Never a false yes]

### 6.2 Completeness and speed by splitting chains

For an acyclic yes-context, select a parent chain from \(X\) to \(Y\). Its mentions preserve the bare-chain patterns, while additional items can only add bits. Seek a kept-bit set that appears on a single link after \(t_0\) loops and propagates across two halves in one loop. Induction gives

\[
t(L)\le t_0+\lceil\log_2L\rceil+1,
\]

including the question attachment. This proves both correctness and a read-time bound. A wider finite chain-class argument handles self-pair activation and endpoint cases missed by the simplest induction. The certificate conditions are sufficient, not a demonstrated complete decision procedure for arbitrary correct trained networks. [Supplementary Note 5, Every yes in time]

The author reports certificates for all 23 successful blocks among 28 starts, with 1–3 loops to spare against the registered budgets. Nine runs representing five distinct tables also have author-reported Lean proofs. Extraction of the table from network weights occurs outside Lean. The author reports agreement of table signs in float32, float64 and 50-digit arithmetic. This reading did not replay either the extraction or Lean.

The certificate assumes correct input bits, distinct people within each statement and question, and an acyclic context for yes-completeness. The safety argument is broader. It does not certify the language reader, arbitrary self-ancestor conventions, the general CLRS block or the CLUTRR cost-based reader. The author widened the certificate three times after inspecting missed models. This limits claims of a prospectively fixed checker, while the resulting valid sufficient proofs remain useful.

The rejected walker is informative: it answered all 3,000 sampled contexts correctly when run to rest, but took roughly \(2L\) loops on a chain of length \(L\) and failed the logarithmic registered budget. A certificate of eventual correctness is different from a certificate of reusable fast composition.

### 6.3 Independent consequence: preserve a rule table and reuse its certificate

This is a direct conditional deduction from the finite interface, not an additional source theorem or an implemented method.

Suppose every entry of the entire admissible finite local table, over all admissible patterns and kept-bit subsets, has nonzero margin at least

\[
\eta=\min_{c,p,S}
\left|b_{c,p}+\sum_{j\in S}w_{cj}\right|>0.
\]

If effective-coefficient perturbations satisfy

\[
\max_{c,p}\left(|\Delta b_{c,p}|+\sum_j|\Delta w_{cj}|\right)<\eta,
\]

every test sign stays unchanged, by the triangle inequality. If the readout table is preserved too, induction on loops shows identical discrete runs on every admissible graph of every size. The existing certificate can therefore be reused without testing larger graphs. This also permits changes that preserve the table even if their real-valued implementations differ substantially.

The bound is on the effective finite-pattern biases and bit coefficients. It is not automatically a bound on all upstream neural parameters. Floating-point evaluation errors must be included in the perturbation budget. The author's smallest reported used-entry margin is 0.0006. That reported subset margin cannot be substituted for the full-table minimum without checking coverage, and is not a universal deployment tolerance. A zero-margin table entry would invalidate this simple robust-neighborhood argument. Preserving only selected certificate entries does not by itself imply identical complete runs. [Source ingredients: Supplementary Note 5 and Table 3]

## 7. Learning mechanisms and the empirical evidence they support

Training uses hard tests in the forward pass from the first update and smooth straight-through derivatives. Count comparisons use a sigmoid-shaped surrogate and equality a bump-shaped surrogate. Some gates pass gradients only in directions that could flip the wanted bit. These are biased optimization choices. There is no unbiased-gradient or convergence theorem. Randomized thresholds help avoid channels that admit everything and receive uninformative count gradients. [Methods and Supplementary Note 2]

### 7.1 CLRS and the stronger primitives supplied to some tasks

The principal training pools contain 80,000 examples at each of the sizes 4, 7, 11, 13 and 16. Training uses final answers without intermediate algorithmic hints. Main general-block comparisons use three seeds. [Methods, Supplementary Tables 2 and 4]

| Reported result | Correct interpretation |
|---|---|
| 97.04% CLRS-30 mean | One separately trained general block per task, three seeds |
| 97.20% | Final shared general block, three seeds, DFS read after \(n\) loops and other tasks after eight |
| 96.92% | The same final shared model read after eight loops on every task |
| 96.55% | General-and-cold hybrid at its registered read |
| 97.98% | Taskwise cold/general selection on standard benchmark inputs |
| 98.35% | The selection using task-scheduling and quickselect inputs as actually trained |
| 98.44% | A ceiling also using fixed route arithmetic on six graph tasks |
| 94.77% | The taskwise column with all choices as first registered, before results |

The final shared general model differs from the earlier 96.87% model in deadline units and DFS reading depth. On a fresh 64-node split the final model scores 97.06% against 96.65%. The 97.20% figure is not a pure parameter-sharing ablation under unchanged inputs and read depth.

The published FloydNet mean 96.64% mixes ten hinted runs. Its no-hint mean is 94.81%. These are published comparator values, not models retrained here with matched compute. Earlier designs inspected the official test, and the paper reports that development history and fresh tests. The internal forecast register lists 213 forecasts, with 110 hits, 75 misses and 28 unscored. Such disclosure is useful but does not erase adaptive design choices or turn all final configurations into untouched holdouts.

On twelve tasks without built route arithmetic, the full cold setting is exact on every official test input and every seed for nine tasks. Weighted shortest-path and tree tasks can receive fixed addition or bottleneck recurrences, and Prim receives extra hop counts. Floyd–Warshall exposes a winning-middle-node bit to the readout. These are admitted computational primitives. Their success does not establish that the network discovered the arithmetic recurrence itself.

### 7.2 Controlled size and depth experiments

- **Maximum retrieval:** train on 5–16 items, test to 16,384, ten seeds and 10,240 sets per size and seed. Exact pair comparisons and a cold count read score at least 99.95% on every seed. Errors involve floating-point top-priority ties. A warm reader using the same comparisons falls to about 42% at 4,096, while a cold read of its weights restores near-exact answers. The author's softmax reproduction misses published results by up to 18.5 points, so it is a diagnostic control rather than a matched best-baseline result. [Figure 3]
- **Deep Bellman–Ford:** at 256 nodes a single general model scores 77.3%, two general halves 85.5%, general+cold 94.2%, and a tied-leg hybrid 98.2%. This is one seed per design. Prim does not show the same ordering, with two general halves stronger than the hybrids in that comparison. The result supports a task-dependent role for direct relational composition. [Figure 7]
- **Constraint problems:** three seeds of the final 2-SAT and two-colouring recipes extrapolate from at most 16 and 32 variables to 500. One 2-SAT seed makes one error at 500, while the others are exact on the sampled tests. Figure 7's initial-to-final comparison changes both learning rate and loop budget, but Supplementary Table 1 also reports a lower-learning-rate-only arm at 67.97% and the added tight-budget arm at 100% on 500 variables. This local comparison supports a role for the budget, without supplying a complete multi-seed factorial experiment. Logarithmic growth of the required loop count is measured on deep contradictions. The parity indistinguishability panel uses 20 random weight settings and no training. It illustrates the structural theorem rather than establishing a universal empirical training failure. [Figure 7, Supplementary Tables 1 and 4, Supplementary Note 4]

### 7.3 A learned executor beside a language reader

On templated kinship, the block trains on 1–16 statements and tests to 1,000. All six 7B runs and three 1.5B runs answer every registered question correctly with the pooled reader. The read-in includes name matching from input embeddings, two extra LM calls per sentence to read direction, and majority pooling by wording over the text. The two held-out wordings reuse known words and test the reader rather than a new relation symbol learned by the cold block. The LM-alone baseline has none of these extra interfaces. [Section 8, Figure 9, Methods]

Without pooling, the 7B per-sentence reader gets 24,190 of 24,192 sentence directions right and the complete system remains at 98.96% on 1,000-statement questions. The residual errors traverse misread sentences. Thus the controlled compositional result has substance, while exact system-level performance still depends on the measurement interface. The all-size proof starts after this interface, with its bits given.

### 7.4 Natural text needs uncertainty rather than irrevocable guessed relations

CLUTRR makes the input-boundary issue concrete. With supplied relation graphs, six runs learn exactly the benchmark's 62 composition rules, and all 826 stories of lengths 5–10 are answered correctly. Four earlier graph-trainer designs were evaluated on test stories before the final configuration. With raw text, the frozen reader gets about 88.6% of stated relations right and produces many spurious relations. Turning these guesses into monotone bits gives only 34.6% story accuracy, against 33.3% for the LM step-by-step baseline. [Section 8, Supplementary Note 4]

Retaining costs \(-\log p\) and reading the cheapest derivation instead gives 56.5% or 60.6%, depending on the training split. Learning a 75,285-parameter linear read-in from frozen LM states and story answers raises these to 64.6% and 66.6%, with three block seeds. The relation-composition table is fixed in that read-in stage. Literal relation-reading accuracy then falls to 76.5–79.1%, and some relation names serve as task-useful internal codes rather than faithful extracted facts.

This supports learning a useful interface for an existing compositional executor. It does not identify the learned internal symbols with ground-truth semantics. The kinship all-size certificate does not cover this cheapest-derivation system. CLUTRR tests only up to ten relations, so its text results cannot be combined with the templated 1,000-statement test into a claim about unrestricted thousand-step natural-language reasoning.

## 8. Improving acquisition without changing the executor

The strong-components experiment supplies a constructive data-selection method. A committee of saved models perturbs small graphs and selects examples on which the models disagree. An algorithmic label oracle supplies the correct final answers. One round raises the cold model from 90.02% to 97.12% on the official test, over three seeds. Hand-designed examples rich in multiple component entry points reach 98.21%. At 96 and 128 nodes the committee model scores 89.0% and 80.0%, below the hand-designed pool. The remaining large-graph mistakes rarely appear among disagreements on 16-node graphs, so a second round is stopped. [Figure 8]

The result separates an executor's ability to represent a correction from the data's ability to expose it. It is not an unlabeled discovery procedure and does not guarantee that a small-instance disagreement curriculum finds every large-instance failure.

For optimal binary search trees, enumerating 219,672 programs from a small supplied grammar finds a recurrence matching 200 training inputs and all 66,560 test pairs. A wider enumeration gives the same program. The grammar was written knowing the desired algorithm. This establishes a representation-and-search ceiling, not general autonomous program induction. Fixed count programs similarly repair the string tasks, but are reported as diagnostics rather than learned headline results. [Section 7, Supplementary Note 2]

## 9. What can be reused, and what has not been established

The most useful source-grounded tools are:

1. **Relation composition through explicit witnesses.** A shared pair operator can double the represented reach of an already learned relation in one loop.
2. **Invariance through controlled numerical access.** A declared recoding symmetry determines which comparisons and arithmetic operations an executor may use.
3. **Excluded-value state for monotone constraint propagation.** Complementing allowed sets aligns consistency algorithms with kept-bit updates.
4. **Finite local tables plus global induction.** A trained low-state rule system can be certified across sizes, including a speed bound, without treating finite extrapolation tests as proof.
5. **Learning the interface or the training examples.** The CLUTRR read-in and disagreement curriculum give concrete, limited mechanisms for improving what an existing executor receives.

The independent margin argument adds a simple way to preserve an already obtained certificate through table-preserving numerical changes. None of these results alone establishes that predictive training creates its own state space, primitive operation set, complete program grammar or uniquely identifiable semantic representation. The present note proposes no FP core change and no compulsory transfer. Astra can use the mathematical instruments without accepting the paper's broader explanatory framing.

## 10. Verification and remaining scope

### Scoped primary dependencies of Theorem 5

These historical sources were consulted because the selected recent paper depends on their exact statements. None receives full-reading credit.

| Source and edition actually consulted | Main-reader coverage | Additional bounded support |
|---|---|---|
| Barto, [June 18, 2014 author manuscript](https://www.karlin.mff.cuni.cz/~barto/Articles/CollapseBW.pdf), later [2016 journal article](https://doi.org/10.1093/logcom/exu070) | Definitions 4.1–4.2, minimality procedure, Corollary 4.8 and Corollaries 6.6–6.7, PDF pp.5–6,10,15–16 | Definitions and theorem statements in pp.4–12 and the core/singleton reduction |
| Atserias–Bulatov–Dawar, [ICALP 2007 author copy](https://www.cl.cam.ac.uk/~ad260/papers/abd-icalp07.pdf) | Abstract, Theorem 4 and Theorem 15/Corollary 16 with their surrounding reduction statements, pp.7,10–11 | Definition of the finite group-equation template on p.4 |
| The same authors, [February 19, 2009 long author version](https://www.cs.upc.edu/~atserias/papers/abd07-affine/abd07-affine.pdf) | Theorems 11,27 and Corollary 28, pp.9,24, also visually inspected because extracted symbols were corrupted | Singleton-expansion statement on p.20 |
| Barto–Kozik, [author manuscript](https://marcinkozik.staff.tcs.uj.edu.pl/Constraint.Satisfaction.Problems.Solvable.by.Local.Consistency.Methods.pdf), associated with [JACM 2014](https://doi.org/10.1145/2556646) | Abstract, finite-language setup, classification statement and reduction start, Theorem 1, pp.1–2,7,10 | Core/width definitions and preceding reductions in pp.4–7 |

Barto's result concerns **relational** width \((2,3)\). It retains original high-arity constraints and synchronizes their projections by deleting tuples. For ordinary consistency width the cited consequence is \((2,\max\{3,r\})\), where \(r\) is the maximum arity. This distinction explains why the cold construction needs incidence tuple state for higher-arity relations.

The cold paper cites the 2009 ABD work but uses the 2007 short version's theorem numbers 4,15,16. In the inspected 2009 long author version these are 11,27,28. The journal typeset numbering was not checked. The algebraic condition is precisely about the **variety generated by** the polymorphism algebra admitting or omitting unary and affine types. With the finite-template/core reduction, the inherited results support the fixed-WL ceiling. They do not supply the recent paper's sketched higher-arity interpretation automatically.

### Evidence boundary

The source proofs, architecture definitions, all empirical tables and figures were read, and the principal distinctions above were checked against the complete v3 rather than its abstract. The independent margin consequence uses an elementary triangle-inequality and induction argument. No training was reproduced, no author code was audited, no Lean result was replayed, and no blanket theorem certification is claimed.

The known limitations are concentrated at real interfaces: exact arithmetic versus floating evaluation, existence of an implementation versus learning it, bit-level certification versus correct language grounding, fixed domain versus scalable domain, and size-general behavior versus total pairwise resource cost. They delimit the useful constructions rather than negating them.
