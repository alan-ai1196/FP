# Literature archive

The [primary index](index.csv) has one row per indexed edition. Paths start at the FP repository root. The first 722 records, OAI-1006-001 through OAI-1006-722, follow the original catalog order. The version and review fields distinguish later editions and withdrawals. Reading status is independent of both. [Section-level progress](READING_PROGRESS.md) · [Mathematical instruments](mathematical_instruments.md) · [Cross-paper results](research_connections.md) · [Daily discoveries](DAILY_DISCOVERIES.md) · [Work division and requests](COORDINATION.md)

## Reading principles

Each paper is an independent knowledge asset. Study its own problem, argument, evidence and limitations in full. FP relevance is optional. A transfer proposal requires the source theorem, concrete target objects, a justified mapping with extra assumptions, a new deduction or falsifiable prediction, and failure conditions. Keep author claims, independent deductions, conjectures, analogies and verified results distinct. Existing cross-paper connections are retained and reassessed in [CONNECTION_REVIEW.md](CONNECTION_REVIEW.md). Routine readings do not directly modify core FP theory.

## OpenAI collection

| Publisher date | Manuscripts | Families | What the version preserves |
|---|---:|---:|---|
| October 6 | 722 | 372 | Complete detached source checkout with manuscript PDFs, TeX, appendices, research traces, cited references and the accompanying Lean tree. |
| October 7 | 719 | 372 | Three withdrawals, fourteen revisions described as fixes and thirteen dependent editions with reference changes. |
| October 26 | 721 | 373 | Two additional manuscripts, local smoothing and the exponential time hypothesis. Includes changed verification materials for the dimension-six bases paper and updates to the Lean tree. |
| October 29 | 721 | 373 | Comparator namespace repair for the rational Hodge conjecture for CM abelian varieties. The commit was published October 30 UTC. |

The [snapshot register](snapshots/openai_math.csv) gives immutable revisions and local catalog paths. The original checkout lives under [the local library](corpus/openai_math_2026/initial/). Updated catalogs and changed manuscript directories, including unchanged supporting files within those directories, live under [releases](corpus/openai_math_2026/releases/). The initial checkout's Git object database also contains the *entire* Lean and manuscript tree of every subsequent release. For example, running the following from the FP root lists the October 26 Lean files without changing the original checkout. The October 12 repository-policy change did not alter a manuscript catalog. [Original release](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a) · [October 26 release](https://github.com/openai/math/tree/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a) · [Publisher change history](https://github.com/openai/math/blob/4eaee87548250b2682affda7d05d947c05554bae/history.md)

~~~powershell
git -C literature/corpus/openai_math_2026/initial ls-tree -r --name-only 7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a lean
python -B literature/library.py
~~~

The builder verifies catalog counts, PDF signatures and accompanying LaTeX for every newly cataloged edition. It preserves reading progress on a repeat run. The formal-status marker records a direct source-path match in the publisher's version-specific manifest. Other Lean connections may be present. A statement review or kernel run requires its own record.

## Discovery and rereading

Run the following at the beginning of each local working day. Python needs requests, beautifulsoup4 and filelock. The initial import also needs Git. Bulk documents stay under the ignored corpus directory. The sweep writes the ordinary index, a dated source report and a line in the daily report. A researcher adds full-read status and mathematical findings after examining the work. A Windows Task Scheduler daily trigger can call this same command using absolute paths. On this machine the command and trigger definition were checked locally. Timer installation is a separate choice.

~~~powershell
python -B literature/sweep.py
~~~

The declared discovery scope covers mathematical tools and the direct PISF literature. Discovery priority is OpenAI and Anthropic, then reliably reviewed work, independently supported AI proof work, and frontier preprints. Correctness is evaluated separately. Reading is performed by the main ChatGPT assistant without subagents, as requested by the user.

- **OpenAI and formal projects.** Compare the openai/math tip with the retained release. Record mathlib's head and Lean's current official release. A new repository tip is fetched into the local source repository and flagged for edition comparison.
- **Institutional publications.** Inspect every item in the OpenAI and DeepMind feeds within the last seven inclusive calendar dates and every visible Anthropic research link. Inspect and retain primary landing pages without a mathematics-title gate. Save linked papers and appendices when available. Web articles and uncertain leads enter the queue even when a PDF is absent. The visible landing page is not the whole institutional archive. Directed archive and reference searches extend it.
- **Preprints.** Query arXiv's primary API across the declared AI, language, vision, information, learning, control and mathematics categories. Search both titles and abstracts for predictive and causal states, identification, automata, sequence and world models, representation learning, learning dynamics, memory, information bottlenecks, compression, token/byte/patch and continuous interfaces, interaction, and mathematical tools. Page by revision time until the entire declared date window is covered. A request failure or repeated page leaves coverage explicitly incomplete. Save versioned PDFs and available source archives. The dated report records the exact query. No finite keyword query certifies all relevant literature, so citation following and the complete OpenAI corpus remain separate tracks.
- **Journals and conferences.** Retain all in-window records from the declared specialist mathematics and ML venues. Broad journals use titles and deposited abstracts and retain missing-abstract cases for primary-page inspection. Conference programs and OpenReview records are separate discovery channels. Record each source's examined count and failures. Directed reading of a proof's references extends the dated window. [Venue collection code](venue_sweep.py)
- **P1/P2 foundational seed.** The initial directed collection took one constructive intelligence functional and its published counterexample, Bayesian sequence prediction, belief-state control, sequential importance weighting, a finite-sample offline learning obstruction, and a cross-field AI-discovered finite tensor certificate. The parity investigation added two systematic data-structure papers and three primary sources on parity dimension, entropy moments and collision probability. This seed defines a reproducible starting set for its stated questions.

Use `python -B literature/sweep.py --metadata-only` to save the discovery queue before a large document transfer. Its entries remain unread and unavailable full texts remain pending. The ordinary command also downloads available documents. Neither command changes a paper into a full read. A repeated metadata pass preserves earlier local paths and reading notes. Source dates are interpreted as documented by each channel. The default working date uses Asia/Shanghai.

For each completed manuscript publish one commit containing its note in `notes/`, its edition-specific index update and the reading-progress entry. Inspect the entire body, proofs, formulas, footnotes, figures, appendices and bibliography. Record external dependencies separately. The original corpus is read in catalog order, with cross-referenced or research-requested papers added explicitly rather than silently replacing the queue.

For a local catalog rebuild, curated metadata can be reimported with the following command. Each intake preserves companion links, inspected sections and remaining work. To reproduce an indexed result after cloning FP elsewhere, fetch the original P0 release with the builder and use the index's source URLs for external items.

~~~powershell
python -B literature/library.py --intake literature/corpus/anthropic_math/intake.json literature/corpus/peer_reviewed/intake.json literature/corpus/peer_reviewed/parity-intake.json
~~~
