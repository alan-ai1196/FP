# Macfarlane et al. (2026): learned operation vocabularies and differentiable program search

## Edition, sources and actual coverage

**Selected edition:** Matthew V. Macfarlane, Clément Bonnet, Herke van Hoof and Levi H. S. Lelis, *Gradient-Based Program Synthesis with Neurally Interpreted Languages*, ICLR 2026, official 26-page conference PDF. The proceedings BibTeX assigns pp. 124292–124317, while the PDF numbers its pages 1–26. A precise conference publication day is not asserted.

Primary sources:

- [Official proceedings record](https://proceedings.iclr.cc/paper_files/paper/2026/hash/c9cde817d04811ba28e44071bd9f76a5-Abstract-Conference.html), [selected PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/c9cde817d04811ba28e44071bd9f76a5-Paper-Conference.pdf) and [official BibTeX](https://proceedings.iclr.cc/paper_files/paper/6656-/bibtex).
- [arXiv 2604.18907v1](https://arxiv.org/abs/2604.18907v1), submitted April 20, 2026 at 23:14:48 UTC, [PDF](https://arxiv.org/pdf/2604.18907v1) and [complete TeX](https://arxiv.org/src/2604.18907v1). Only v1 appeared in the inspected primary history.
- [OpenReview forum](https://openreview.net/forum?id=NAORIWBaoO), identified but not fully inspected because the page required verification and API access returned 403. No claim about unseen attachments or complete forum revision history is made.

**Fully read by Pro-E on November 27, 2026, Shanghai:** all 26 official PDF pages, main Sections 1–6, Appendices A–I, all seven numbered and all unnumbered equations, Algorithm 1, six figures, eight tables, Listing 1, the author footnote, acknowledgments, all 30 references and the LLM-use disclosure. There are no named theorem or proof environments. Continuous extracted text was read in large page blocks. All figure/table-bearing pages, the algorithm, listing and the two regularizer formula layouts were visually inspected. Recovered TeX was consulted for the objectives, search procedure, appendix loss and gradient-routing details.

A support reader compared all 26 arXiv pages with the official PDF. Twenty-one pages match normalized word sequences. Remaining differences are six appendix/section cross-reference words and one mathematical extraction-spacing difference. This is text alignment, not binary or rendered-symbol identity, and the arXiv edition receives no second full-reading credit. The proceedings landing-page abstract has somewhat different wording, so the selected PDF governs scientific claims.

Support readers separately examined metadata, formal interfaces and experimental resources. Their bounded work did not replace main-reader coverage. No author-owned implementation link or separate supplement archive was authenticated in the inspected proceedings, article or source files. The verified appendices are part of the same 26-page paper. This does not prove that code is unavailable elsewhere. No implementation audit, training reproduction or formal verification was performed.

Appendix I states that LLMs were used for grammar and spelling polishing, without research ideation or other significant scientific contributions. This is the authors' disclosure, not independently verified provenance. No FP core files were changed.

## 1. What the construction learns

The Neural Language Interpreter, NLI, learns a codebook and an interpreter jointly from programming-by-example tasks. A task supplies several input/output pairs from a hidden program and asks for its output on a new input. During ordinary NLI training, the model does not receive the generating program's symbolic representation. It must infer a program representation from some pairs and predict a held-out pair. [Sections 1–3]

The resulting construction has three parts:

1. A permutation-invariant **inductor** maps the I/O specification to a sequence of code distributions.
2. A shared **interpreter** applies one code at a time to a state represented through I/O-token probabilities.
3. At test time, **latent optimization** changes the program representation while holding the learned interpreter fixed.

The codebook size, skip instruction, recurrent execution interface, transformer networks, example grouping and training losses are supplied design choices. The meanings attached to the ordinary code entries are learned. In the synthetic experiments, a known generator DSL creates the tasks, but its symbolic programs are withheld from ordinary NLI. Thus the claimed learned operations have an explicit origin in prediction across related I/O tasks, without implying that the whole computational substrate was autonomously invented.

The important reuse mechanism is concrete: the same trained execution network and code entry can act at different positions in different inferred programs. This is stronger structure than assigning a separate unconstrained latent vector to every whole task. Whether those reusable transitions implement a particular intended primitive, and whether they remain accurate on new intermediate states, are additional questions.

## 2. Architecture and objective

### 2.1 Leave-one-out induction

For task b with m pairs, write S_(b,i) for its specification with pair i removed. The reconstruction objective predicts y_(b,i) from x_(b,i) using a code sequence inferred from S_(b,i):

\[
\mathcal L_{\mathrm{rec}}
=-\log p_\theta(y_{b,i}\mid x_{b,i},q_\phi(S_{b,i})).
\]

The loss averages over task batches and held-out pairs, with an additional token-reuse regularizer. This trains within-task prediction, rather than merely copying the exact examples provided to the inductor. It does not by itself establish generalization to a new task distribution. [Equations (1)–(3)]

The inductor independently applies a transformer to each I/O pair and mean-pools the resulting embedding at each program position. Mean pooling is exactly invariant to permutation of the specification pairs. A shared map converts each positional mean to K logits, followed by a Gumbel-Softmax relaxation. The model therefore receives a sequence z_t in the K-simplex. The source's dedicated skip code allows fewer effective steps than the allocated T positions. [Section 3.2]

### 2.2 The recurrent state is explicit

Let pi_t be the interpreter's I/O probability state. With code embedding E_v, I/O embedding E_io and a shared execution network d, Algorithm 1 computes a candidate distribution and then applies a skip gate:

\[
\widetilde\pi_t
=\operatorname{softmax}
\left(\frac{d(E_{io}^{\mathsf T}\pi_{t-1},E_v^{\mathsf T}z_t)+h_t}{\tau_d}\right),
\]

\[
\pi_t=z_{t,\mathrm{skip}}\pi_{t-1}
+(1-z_{t,\mathrm{skip}})\widetilde\pi_t.
\]

Initialization embeds the query input and starts pi_0 at its one-hot representation. The gated output is re-embedded for the next step. Thus intermediate probability states, rather than an independently growing hidden workspace, mediate the published recurrence. The execution network itself can process an entire encoded sequence. A single learned instruction is not necessarily a constant-cost elementary symbolic operation. [Section 3.3, Algorithm 1]

Weight sharing makes repeated application possible. It does not prove that code k means the same human-readable primitive on every input, or that its errors remain small under arbitrary composition. The source presents an architectural mechanism and experiments, not a compositional generalization theorem.

### 2.3 Test-time adaptation remains relaxed

The inductor gives an initial sequence of latent embeddings. The search perturbs it with multiple Gaussian initializations, then ascends the expected specification log-likelihood through the interpreter. Both program and interpreter Gumbel temperatures are annealed. The weights of the learned execution model remain fixed. [Section 3.4]

**The final predictor uses the optimized soft representation.** The paper explicitly avoids hard sampling at the end because it could change the optimized behavior. Training hyperparameters also end at temperature 0.5 and disable straight-through estimation. Consequently the reported system should not be treated as a search restricted to exactly K^T hard words.

For a soft code z, the non-skip execution network is evaluated at the mixed embedding E_v transpose z. Because the network and softmax are nonlinear, its result is generally not the mixture of the results for the individual hard codes. The skip gate has an exact mixture form, but that does not make the entire relaxed language a probabilistic choice among a finite set of symbolic programs.

This distinction preserves the positive result: differentiable program representations support useful adaptation. It limits stronger interpretations about exact discrete program recovery, description length or a finite installed program alphabet.

## 3. Constructive mathematical consequences

The following deductions are independently derived from the published interface. They are conditional mathematical tools, not author theorems, training guarantees, novelty claims or proposed FP architecture.

### 3.1 Hard tokens define composable operators

Freeze the interpreter parameters and temperature, restrict each program token to a one-hot code, and suppose each execution step draws fresh Gumbel noise independently of the past from the same law. A code k then defines a Markov kernel K_k on the common probability-state space. For a word w=k_1...k_T, execution is exactly successive kernel composition:

\[
\mu_w=\mu_0K_{k_1}\cdots K_{k_T}.
\]

If uv denotes concatenation, the corresponding transition is execution of u followed by execution of v. The skip token is the identity kernel because its gate is exactly one. Thus the free monoid of code words acts by state-transition kernels, with relations identifying words that happen to have the same induced transition.

The proof is conditional independence and the published recurrence: given pi_(t−1) and code k_t, no earlier program token is an additional argument to the transition. With Gumbel noise disabled, the same statement uses deterministic maps. Fixing a different noise realization at every position instead produces time-indexed maps, which must not be silently identified with one stationary map per token.

This makes structural reuse exact under the stated restriction. It does not identify the learned kernel with a generating DSL primitive, establish successful search for a desired word, or certify that the paper's soft final programs lie in this finite hard-token family. Relaxed codes also induce composable transitions, but their alphabet is continuous.

### 3.2 A source-state condition for transferring primitive accuracy

Suppose a reference meaning G_k has been proposed for each code on a common metric state space (S,d). Let learned execution be

\[
S_t=F_{k_t}(S_{t-1},H_t),
\qquad s_t=G_{k_t}(s_{t-1}),
\]

with the same initial state. Assume:

- The learned transition is L_k-Lipschitz in state for each noise realization, on all relevant learned and reference states.
- On every reference state reachable immediately before code k in the programs under consideration,

\[
\mathbb E_H d(F_k(s,H),G_k(s))\le\epsilon_k.
\]

- Fresh step noise has the law used in these bounds and is independent of previous execution.

Writing e_t=E d(S_t,s_t), insert F_(k_t)(s_(t−1),H_t) between learned and reference states. The triangle inequality gives

\[
e_t\le L_{k_t}e_{t-1}+\epsilon_{k_t},
\]

and therefore

\[
e_T\le
\sum_{t=1}^{T}\epsilon_{k_t}
\prod_{j=t+1}^{T}L_{k_j}.
\]

The reference maps need not be defined on arbitrary off-manifold learned states. Only the learned map's comparison and the reference trajectory are used. Under the added nonexpansiveness condition L_k≤1, errors accumulate at most additively. Exact skip has L=1 and epsilon=0.

This is a practical condition for reusing a learned primitive: accuracy must cover the **pre-token states reached by the new compositions**. A small average error on isolated primitive inputs does not supply that coverage. Weight sharing alone does not bound the L_k or epsilon_k. The NLI experiments do not measure these quantities.

For a probability-state tensor with distance equal to the sum of coordinatewise L1 distances, a one-hot terminal target gives an additional conditional consequence. If a per-position argmax readout makes any output error, at least one target position has probability at most one half, so the total L1 distance is at least one. Hence the probability of any such output error is at most min(1,e_T). This converts a verified state-error bound into a prediction guarantee under that readout, without assuming that soft and one-hot state distributions are close in total variation. Comparing a continuous soft-state law with a point mass in total variation could instead be vacuous.

### 3.3 A precise hardening condition

For a fixed input and fixed execution noise, consider a soft code sequence z_t and its hard choices a_t. Suppose the common transition F(s,z,h) obeys

\[
d(F(s,z,h),F(s',z',h))
\le L_t d(s,s')+M_t\lVert z-z'\rVert_1
\]

on the compared runs. Since ||z_t−e_(a_t)||_1=2(1−z_(t,a_t)), their terminal state distance is bounded by

\[
\eta_T
\le\sum_{t=1}^{T}
2M_t(1-z_{t,a_t})\prod_{j=t+1}^{T}L_j.
\]

This follows from the same one-step insertion argument. If the metric controls every final probability coordinate by eta_T and every soft output position has a winning-probability margin greater than 2 eta_T, hardening preserves all argmax outputs on that input. The margin must be verified where the conclusion is wanted. A sample-local check does not prove uniform population equivalence.

This supplies a concrete route to certifying when a relaxed program can be replaced by a hard word. The source does not provide these sensitivity or margin bounds and deliberately retains soft execution. No hardening experiment was run here.

### 3.4 The vocabulary regularizer is an occupancy objective

Appendix H defines an interpretable smooth quantity. Suppose categorical token draws at distinct batch/position slots a are conditionally independent with probabilities p_(a,k). If U counts distinct token identities used at least once, then

\[
\mathbb E U
=\sum_{k=1}^{K}\left[1-\prod_a(1-p_{a,k})\right].
\]

For a fixed k, the product is its absence probability. Linearity of expectation then sums presence indicators. No independence between different token identities within a slot is needed for this expectation. The important independence is across slots conditional on their probabilities. This gives an exact occupancy interpretation under that sampling model, even though Appendix H describes it as an approximation to the learned relaxed system.

Let s_k=sum_a p_(a,k). The elementary product bound and union bound give

\[
1-e^{-s_k}
\le 1-\prod_a(1-p_{a,k})
\le\min(1,s_k).
\]

Thus the regularizer behaves like a smooth count of identities once their total probability mass is appreciable. It is not a charge for all stored codebook parameters or for program execution time. The source acknowledges that this term alone prefers collapse and relies on reconstruction to make a useful language.

There is a material formula distinction. Main equation (3) sums over program position **outside** the absence product, while Appendix H includes positions **inside** it. The former counts occupied token-position pairs across examples, whereas the latter counts token identities across all positions. For deterministic repetition of one token in T positions, the former gives T and the latter gives one. More generally, for the same slot draws, identity occupancy is no larger than position-specific occupancy, which is no larger than T times identity occupancy. The inequality follows by taking a union over positions for each token.

Both are well-defined regularizers, but they encourage different reuse. The implementation was not authenticated, so this note does not decide which was used. Their difference does not erase the empirical recurrence/search result, but it prevents assigning a uniquely specified global-vocabulary cost to equation (3).

## 4. What the experiments establish

### 4.1 Deliberately withheld compositions

The custom benchmark uses fixed input-sequence length 20 and the following distributions. [Section 4, Appendix A.1]

| Split | Training transformations | Test transformations |
|---|---|---|
| Shift-L | Left shifts 1–5 | Left shifts 6–10 |
| Shift-P | Left shifts 7–9 | Left shifts 1–3 |
| Comp-I | Single operations from a generator library of over 20 primitives | Compositions of two or more primitives |

Appendix A gives two million training tasks and ten thousand test tasks for the custom setup. The article does not give a complete Comp-I primitive inventory or composition-length sampling distribution. The generator's library is not a supplied semantic label for NLI code entries.

The material OOD accuracies from Table 1 are:

| Method | Shift-L | Shift-P | Comp-I |
|---|---:|---:|---:|
| NLI direct induction | 0.00 | 0.00 | 0.17 |
| NLI prior sampling | 0.10 | 0.00 | 0.23 |
| NLI gradient search | **0.99** | **1.00** | **0.91** |
| LPN gradient search | 0.03 | 0.00 | 0.29 |
| Discrete LPN gradient search | 0.01 | 0.00 | 0.20 |

This supports a large tested benefit from **searching the learned recurrent language**. Direct induction is not sufficient for these OOD tasks. Several baselines have nonzero Comp-I accuracy, so the table should not be compressed into a universal claim that all alternatives cannot generalize.

Figure 2 and Appendix G interpret learned token 231 as one left shift and token 476 as two. The illustrated eight-shift result uses four copies of the former and two of the latter. These examples show interpretable operation reuse, but do not identify token semantics uniformly across all seeds and inputs. The appendix examples use ten-element lists, while the benchmark description specifies twenty-element inputs.

Shift-L extrapolates shift magnitude, not input length. Table 4 allocates ten training latent slots for the shift tasks. The six-code OOD illustration therefore does not exceed that allocated slot budget, although it uses more active codes than the illustrated training solutions. A recurrent decoder can be unrolled further in principle, but the experiment does not prove arbitrary computational-depth generalization.

### 4.2 Search resources and interventions

Table 4 specifies 100 search gradient steps and 1,024 initializations for both shift tasks and DeepCoder. Comp-I uses **8,192 initializations**, giving 819,200 start-step pairs per task before pricing specification evaluation and recurrent forward/backward work. For s starts, L updates, m specification pairs and T recurrent positions, a direct evaluation pattern entails work proportional to sLmT execution steps, each with its own neural cost. Parallel hardware changes latency rather than removing this work.

The custom models train for 100,000 batches of size 512. DeepCoder models train for 200,000 such batches. NLI's model dimension is 128, compared with 512 for several baselines. Extra deeper-decoder baseline experiments intended to match compute reportedly performed worse, and Table 1 reports the stronger two-layer variants. The main comparison therefore should not be represented as a fully documented equal-inference-cost contest. Numerical baseline search/restart budgets, total FLOPs, wall-clock costs and the specification-size setting are not fully supplied in the article. [Section 4.1, Appendix C]

Figure 4 shows an overall gain from more starts and steps on Comp-I, with up to 4,096 starts and 400 steps. It is not strictly monotone on every plotted curve. Its largest plotted restart count is below the 8,192-start main setting.

The aggregate ablation reference in Figure 3 is 97% OOD accuracy. Removing inductor Gumbel sampling gives 76%, the encoder loss 66%, skip 24%, interpreter Gumbel or the discrete layer 5%, recurrence 2%, and the discrete program 1%. The 97% reference is not Table 1's direct-induction row. These controlled removals support the joint usefulness of the imposed representation and execution choices on this suite, rather than universal necessity of those components.

Table 4 calls the 1e-5 coefficient the encoder loss coefficient. The main and appendix regularizer equations differ as described above. Appendix D separately studies annealing duration on **in-distribution** Shift-L accuracy. Durations of 1,000, 5,000 and at least 10,000 steps give 0.00, 0.41 and 1.00. Its text uses linear schedules, while Table 4 lists exponential schedules. This ablation does not directly establish OOD stability for every schedule.

Three training seeds and mean performance are reported. Table 1 and Figures 3, 4 and 6 supply no standard deviations, confidence intervals or visible error bars. The experiments were not independently replayed.

### 4.3 DeepCoder and additional supervision

DeepCoder tests five distinctions: training on 1–4-line programs and testing on five lines, mixing previously separated operation groups, reversing concept order, composing Scanl1 after seeing it only in isolation or excluding it, and using new Scanl1 lambda functions. The isolated Scanl1 cases make up 25% of training tasks in their split. These are explicit synthetic distribution shifts. [Appendix A.2]

Section 4.5 and Table 3 report 11.6 million regenerated training tasks and ten thousand test tasks. Appendix A.2 prose instead says two million training tasks. Both source statements are retained. The paper contrasts its regenerated data with 60 million tasks in the earlier work. It does not establish that all neuro-symbolic baselines were rerun with identical data, search budgets and supervision.

Figure 6 shows complementary strengths. NLI is stronger than LPN on length and some novel concept combinations, while LPN is stronger on order switching and added functionality. ExeDec remains stronger on several comparisons. The graph supports useful neural program induction without program labels, not dominance across all composition regimes.

The variants labeled **with programs** are different training-information conditions. Their so-called natural-language program encoder actually receives whitespace-tokenized DeepCoder DSL code. Appendix E also changes gradient routing: program reconstruction updates the executor, while I/O reconstruction is stopped from updating that executor and instead aligns the I/O inductor. The auxiliary loss weight is one. The program encoder is discarded at test. Thus the intervention changes both access to generating programs and how the execution model is trained. [Appendix E]

## 5. Scope of the useful result

NLI is a concrete recent example in which predictive I/O training acquires useful operation representations and test-time optimization recomposes them. The strongest evidence is bounded and empirical. Its exact mathematical structure is shared recurrent execution, with kernel composition available under hard-token and independent-noise conditions. The independent error recurrence identifies what extra intermediate-state coverage and stability would support semantic transfer to new words. The hardening bound states when the relaxed result could be replaced without changing a specified output. Neither guarantee is established by the paper's final-task loss alone.

The source itself lists test-time search cost, possible gradient problems at larger depths and an execution syntax without explicit parameterized primitives or branching as limitations. A neural transition may still implement a conditional function internally. The absence of a branch instruction should not be inflated into a general expressivity impossibility.

No FP mapping is proposed in this note. The source supplies task grouping, a fixed codebook, supervised I/O prediction and a designed recurrent interpreter. A transfer to prediction-induced state formation would require a separate justified object mapping and learning claim, which remain Astra's decision. No global discovery sweep, historical full-reading queue, new FP architecture or core edit was introduced.

The official edition is complete. The arXiv edition has separately documented whole-text alignment. Future work should build on the preserved exact interfaces and empirical budget rather than reread the paper. Continue recent constructive program and automata research after a fresh shared-history, owner and Astra-request check.
