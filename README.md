# Factor Programs

FP studies how ordinary prediction error can teach a learner which computations to perform under physical resource limits. Work on the second foundational investigation takes place on this branch.

## Research branches

| Branch | What it contains |
|---|---|
| `main` | The canonical Foundation R4 theory, tested implementations, release boundaries and original experiment journals. [Canonical theory](https://github.com/alan-ai1196/FP/blob/a35ef18b0576048ea93f0b87ea6f6a78760bb447/FP_THEORY.md) |
| `frontier` | Active mathematics, falsifiers and reproducible evidence. The branch descends directly from the completed reconstruction. |
| `archive` | Historical source trees, including divergent research, PR #1, superseded release work and the original run evidence. Each retired branch can be recovered by ancestry. [Archive index](https://github.com/alan-ai1196/FP/blob/40cf379c85f6a8a2ae86cb72f5b85696b1712c1d/research/archive/INDEX.md) |

## Reproduce the first reconstruction

The reconstruction shows when a learner can acquire a cheaper read. On the original 12,288-token development suffix, every fixed mixture of the 512 lag-copy distributions and the training-prefix add-one unigram has optimum loss within [7.236294824, 7.236529809] nats per token. The historical Transformer scored 6.260544623 and order-5 modified Kneser–Ney scored 6.587281632. Context-dependent mixing and learned transformations have different hypothesis classes. [Report](https://github.com/alan-ai1196/FP/blob/a674dda8985be1dd316b102da4fa00a42c837819/research/reconstruction/REPORT.md) · [Certificate](https://github.com/alan-ai1196/FP/blob/a674dda8985be1dd316b102da4fa00a42c837819/research/reconstruction/text_capacity_result.json)

The historical checkout keeps the exact evaluator, corpus reader, baseline journals and numerical fixtures together. From a full clone with Python and NumPy, the following commands run the portable checks. The additional `--text` option on the last command uses the two original token files at the registered data location and verifies both prefix identities. The four portable checks and the full text certificate were reproduced during consolidation.

```sh
git worktree add --detach ../fp-reconstruction-check a674dda8985be1dd316b102da4fa00a42c837819
python -B ../fp-reconstruction-check/research/reconstruction/audit_routing.py
python -B ../fp-reconstruction-check/research/reconstruction/audit_address_process.py
python -B ../fp-reconstruction-check/research/reconstruction/audit_foundation_comparison.py
python -B ../fp-reconstruction-check/research/reconstruction/text_capacity.py
git worktree remove ../fp-reconstruction-check
```

The canonical checkout also holds the original [claims register](https://github.com/alan-ai1196/FP/blob/a35ef18b0576048ea93f0b87ea6f6a78760bb447/CLAIMS_AND_STATUS.md), [research history](https://github.com/alan-ai1196/FP/blob/a35ef18b0576048ea93f0b87ea6f6a78760bb447/RESEARCH_HISTORY.md), [resource contract](https://github.com/alan-ai1196/FP/blob/a35ef18b0576048ea93f0b87ea6f6a78760bb447/EXPERIMENT_RESOURCE_CONTRACT.md) and [implementation status](https://github.com/alan-ai1196/FP/blob/a35ef18b0576048ea93f0b87ea6f6a78760bb447/IMPLEMENTATION_STATUS.md). Historical experiment packages and repeated Compiler status registers have a single working home there.
