# Literature work and research handoff

## Division of work agreed on 2026-11-23, Shanghai

The user assigned ChatGPT in the cloud session responsibility for literature discovery, source collection, complete reading and the literature index. The locally running Astra 6.2 remains responsible for FP theory, representation design, learning rules and experiments. Astra can reread any needed source, challenge a reading note and amend a finding with an explanation. It need not duplicate the bulk search and reading queue.

Use this file and ordinary commit messages to exchange requests, corrections and mathematical findings. Keep one shared `frontier` branch alongside `main` and `archive`. Fetch before publishing, inspect incoming changes and incorporate them without overwriting the other worker. Never force-push shared research history. A Git commit makes a message available when the other worker fetches. It does not prove that worker has already seen it.

## Reading and publication rule

Read each manuscript's complete text, formulas, proof steps, footnotes, figures, appendices and bibliography. Read the source when PDF extraction loses mathematical information. Record unread or inaccessible material explicitly. A download, abstract, extracted text file or summary is not a completed reading. Understanding an imported theorem's role does not count as reading its cited paper.

Publish one completed-paper commit at a time, with a note under `literature/notes/`, that edition's index update and a brief progress entry. Use the commit subject `literature: read <paper ID> — <finding>`. State precisely what was read and what remains unverified. Complete reading, independent proof verification and a local Lean replay are separate statuses. A failed or questionable argument still receives a complete reading note after every part has been examined.

Maintain the original OpenAI corpus queue and its separately indexed revisions. OpenAI and Anthropic have discovery priority, followed by reliable reviewed work, independently supported AI proofs and frontier preprints. Publication priority does not establish correctness. Add direct PISF foundations and current work without restricting discovery to mathematics headlines or title keywords.

## Current work

- ChatGPT is broadening the scanner and continuing the original queue at OAI-1006-002. The user requires this work to be done by the main assistant alone, without subagents. Papers 003 and 004 have downloaded source files but remain unread. Interrupted preliminary work does not count as a completed reading.
- Local Astra should continue the registered learning problem in `research/frontier/NEXT.md`, consulting new reading notes when useful.
- The corpus remains in progress. A completed paper or infrastructure change does not close FP Goal V2.

## Requests and replies

2026-11-23 — ChatGPT to local Astra: I have taken over literature discovery and full reading at the user's request. Please continue the theory and learning work. Put requests for specific papers, missing hypotheses or corrections here, or describe them in an ordinary research commit. I will check incoming history before each paper is published. The first scanner update will broaden PISF coverage and remove the first-50-record date-window shortcut.
