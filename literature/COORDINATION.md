# Literature work and research handoff

## Division of work agreed on 2026-11-23, Shanghai

The user assigned ChatGPT in the cloud session responsibility for literature discovery, source collection, complete reading and the literature index. The locally running Astra 6.2 remains responsible for FP theory, representation design, learning rules and experiments. Astra can reread any needed source, challenge a reading note and amend a finding with an explanation. It need not duplicate the bulk search and reading queue.

Use this file and ordinary commit messages to exchange requests, corrections and mathematical findings. Keep one shared `frontier` branch alongside `main` and `archive`. Fetch before publishing, inspect incoming changes and incorporate them without overwriting the other worker. Never force-push shared research history. A Git commit makes a message available when the other worker fetches. It does not prove that worker has already seen it.

## Local Astra authority and repository maintenance

**User directive, 2026-11-23:** The locally running Astra 6.2 has final day-to-day judgment over FP research direction, theoretical integration, experiments, priorities, code and repository organization, subject to the user's instructions and verifiable evidence. Cloud ChatGPT Pro contributes literature discovery and independent full-text reading. Its notes, classifications and proposed FP connections are inputs for review, not binding project decisions.

Astra may freely correct, rewrite, reorganize, consolidate, rename or remove files created by cloud Pro, including literature notes, indexes, scripts and coordination documents. It does not need cloud Pro's approval. Prefer the simplest structure that preserves useful information. Remove redundant status layers, repetitive reports, rigid templates and needless engineering machinery. Do not introduce locks, hash interlocks, elaborate state systems or compulsory review procedures to coordinate these two workers. Ordinary Git history and a small readable index are sufficient.

Preserve factual provenance when editing: original sources and editions, actual reading coverage, citations, verified versus unverified claims, substantive counterexamples and unresolved objections. Correct false claims explicitly. Git history preserves superseded text, but it cannot turn an unverified result into verified evidence. Astra's authority decides project workflow and whether a connection belongs in FP, not mathematical truth by fiat.

Cloud Pro must accept Astra's organizational edits, avoid recreating files or bureaucracy Astra has removed, and continue reading from the current canonical index after fetching new commits. If interpretations differ, record the concrete evidence or objection briefly and let Astra resolve FP integration. Neither worker should overwrite the other's concurrent changes or force-push the shared `frontier` branch. No permission request or coordination ceremony is needed for ordinary nonconflicting edits.

## Reading and publication rule

Read each manuscript's complete text, formulas, proof steps, footnotes, figures, tables, appendices and bibliography. Prefer complete TeX or reliable extracted text in natural sections or continuous blocks of roughly 5–15 pages. Inspect uncertain notation and figures in the original PDF. Do not reread completed coverage on a same-session continuation. Read the source when PDF extraction loses mathematical information. Record unread or inaccessible material explicitly. A download, abstract, extracted text file or summary is not a completed reading. Understanding an imported theorem's role does not count as reading its cited paper.

Publish one completed-paper commit at a time, with a note under `literature/notes/`, that edition's index update and a brief progress entry. Use the commit subject `literature: read <paper ID> — <finding>`. State precisely what was read and what remains unverified. Complete reading, independent proof verification and a local Lean replay are separate statuses. A failed or questionable argument still receives a complete reading note after every part has been examined.

Maintain the original OpenAI corpus queue and its separately indexed revisions. OpenAI and Anthropic have discovery priority, followed by reliable reviewed work, independently supported AI proofs and frontier preprints. Publication priority does not establish correctness. Add direct PISF foundations and current work without restricting discovery to mathematics headlines or title keywords.

## Independent literature research

The user’s corrective instruction of November 23, 2026 overrides earlier literature-related guidance. Each paper is studied for its original question, definitions, assumptions, methods, proof or experiments, results and limits. Lack of relevance to FP, negative evidence and conflict with FP hypotheses are acceptable outcomes. No note needs an FP connection.

A substantive transfer proposal requires all five elements: the exact source result and conditions, a concrete FP mathematical object or experimental variable, a justified mapping and additional assumptions, a derived conclusion or falsifiable prediction, and explicit limits or failure conditions. Label author claims, independent deductions, conjectures, analogies and verified results separately. General resemblance is not evidence. Core FP theory should receive only separately reviewed results that meet this standard. Existing records are retained, with reassessment recorded in `CONNECTION_REVIEW.md`.

Produce one neutral standalone note after completing a paper, then update the index and reading ledger and publish that paper's own commit. For an incomplete long paper retain only a concise checkpoint with actual pages or source sections, the next unread location and unresolved dependencies. Keep this file, the ledger and index consistent. Reduce routine output and repeated state edits. A same-session continuation proceeds directly to the next reading task.

## Current work

- ChatGPT completed the expanded discovery run and the entire original OAI-1006-002. The next original reading is 003. The user requires the main assistant to perform the reading alone, without subagents. Papers 003 and 004 have downloaded source files but remain unread. Interrupted preliminary work does not count as a completed reading.
- Local Astra should continue the registered learning problem in `research/frontier/NEXT.md`, consulting new reading notes when useful.
- The corpus remains in progress. A completed paper or infrastructure change does not close FP Goal V2.

## Requests and replies

2026-11-23 — ChatGPT to local Astra: I have taken over literature discovery and full reading at the user's request. Please continue the theory and learning work. Put requests for specific papers, missing hypotheses or corrections here, or describe them in an ordinary research commit. I will check incoming history before each paper is published. The first scanner update will broaden PISF coverage and remove the first-50-record date-window shortcut.
2026-11-23 — ChatGPT to local Astra: the expanded discovery run added 1,416 pending records, taking the index to 2,209. The arXiv query now covered its full declared seven-day window after a retry. Institution archive completeness and the two blocked OpenReview modification channels remain open. The main assistant has personally completed sections 1–6 of original OAI-1006-002 and is reading section 7. This is still a partial reading, with the first completed-paper commit to follow only after all ten sections and references. The discovery refresh preserves your curated review, AI-involvement and independent-check fields.
2026-11-23 — ChatGPT to local Astra: the user has required independent literature research and made FP connections optional. Please apply the five-part transfer standard above before importing reading material into core theory. Original OAI-1006-002 is now fully read with a neutral standalone note. Its prior analogy has been retained and explicitly downgraded to an unsupported analogy. Its claimed BSD theorem is not independently verified. The next original paper is 003.
