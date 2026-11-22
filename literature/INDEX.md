# FP mathematics library

The [primary index](index.csv) has one row per indexed edition. Paths start at the FP repository root. The first 722 records, OAI-1006-001 through OAI-1006-722, follow the original catalog order. The version and review fields distinguish later editions and withdrawals. Reading status is independent of both. [Section-level progress](READING_PROGRESS.md) · [Mathematical instruments](mathematical_instruments.md) · [Cross-paper results](research_connections.md) · [Daily discoveries](DAILY_DISCOVERIES.md)

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

The scheduled collection scope is reproducible and bounded.

- **OpenAI and formal projects.** Compare the openai/math tip with the retained release. Record mathlib's head and Lean's current official release. A new repository tip is fetched into the local source repository and flagged for edition comparison.
- **Institutional publications.** Inspect all items in the OpenAI and DeepMind feeds falling within the last seven inclusive calendar dates. Check titles for mathematics, theorems, formal proof, formalization, Riemann, scientific discovery and AlphaProof. Inspect matching links on the Anthropic research landing page, whose visible list is independent of date. Save publisher-labeled primary PDFs and appendices and record links requiring editorial identification. An announcement is a discovery lead. The primary-corpus intake additionally covers Alpöge's original release, both independent verification sites, the formal-math project list, two mathematical-physics projects and two historical representation studies.
- **Preprints.** Query arXiv's primary API for math.CO, math.PR, math.MG, cs.CC, cs.LG and stat.ML and the eight title phrases in the dated report. Examine the first 50 results sorted by revision time. Record whether the last item establishes coverage of the window. Save versioned PDFs and available source archives separately. This title search has a narrower recall than reading all six categories.
- **Journals and conferences.** The venue module declares its publication-date windows, ISSNs, primary official program sources, title predicates and discovery channels. Every in-scope match enters the queue, including records awaiting full text. Each channel's examined count and access failures are retained separately. Directed lookup of references used in a proof adds to this window and is labeled in the reading record. [Venue collection code](venue_sweep.py)
- **P1/P2 foundational seed.** The initial directed collection took one constructive intelligence functional and its published counterexample, Bayesian sequence prediction, belief-state control, sequential importance weighting, a finite-sample offline learning obstruction, and a cross-field AI-discovered finite tensor certificate. The parity investigation added two systematic data-structure papers and three primary sources on parity dimension, entropy moments and collision probability. This seed defines a reproducible starting set for its stated questions.

For a local catalog rebuild, curated metadata can be reimported with the following command. Each intake preserves companion links, inspected sections and remaining work. To reproduce an indexed result after cloning FP elsewhere, fetch the original P0 release with the builder and use the index's source URLs for external items.

~~~powershell
python -B literature/library.py --intake literature/corpus/anthropic_math/intake.json literature/corpus/peer_reviewed/intake.json literature/corpus/peer_reviewed/parity-intake.json
~~~
