# Eliminate a proposal that has exactly one acceptable answer

Status: **proved conditional implementation law; implemented for the fixed
indexed reference and global/projected AMP schedules; CPU and all fifteen actual
CUDA A1 jobs pass**. No Foundation or ERC-1 change.

## 1. The removable object is the producer, not its input

Let x be the complete owner-held input, including the actual causal query,
native predecessor and declared resource/numerical contract. Suppose a
trusted checker constructs P(x) and accepts a proposed plan p exactly when
p=P(x). The numerical implementation K(x,p) is already trusted; a separate
producer H contributes only p. Keep the complete x and the same K, construct
P(x) privately and run K(x,P(x)). The producer H is unnecessary.

**Elimination law.** For a fixed x and fixed numerical contract, this change
preserves every valid accepted numerical execution of the proposal path.
It cannot introduce another accepted plan or arithmetic schedule. If the
producer, transfer and redundant checks cost nonnegative resources, removing
them admits a no-greater abstract work charge; it may remove refusals caused
only by those operations or by an incorrect/raising producer.

**Proof.** An accepted, correctly framed proposal has p=P(x). Substitution
in K gives exactly K(x,P(x)); neither x nor K has changed. Construction of
P(x) was already required by the checker. Remove H and its exchange work,
retaining that construction and the numerical execution. Their sum is no
greater than the original nonnegative sum. A failed proposal has no missing
legal plan to contribute, because the accepted set is a singleton. QED.

The qualification "valid" matters. This is not a promise to reproduce the
wrong outputs of the previous alias counterexamples: those changed x or
accepted history behind the checker. Frame preservation and numerical
refinement remain separate obligations. Nor is the law equality of complete
resource histories. New runs use their new contract and actual debits; no
past work is refunded and no old evidence is rewritten. Removing operations
does not prove a bound or monotonicity for whole-process memory, allocator
behavior, wall time, or every possible resource schedule.

P need not be injective. For n3, query(1,2), native counts(0,0,+1) and
(0,0,-1) have the same complete global AMP plan. Their exact RNE predictions
are13757317/16777216 and12079595/67108864. Retaining the plan alone loses
current information, before considering future queries. All counts, native
state, sources, histories and lineage remain; no state quotient is licensed.

## 2. Apply the law to the actual fixed classes

The existing reference validator reconstructed the full query-block plan.
The global and projected AMP validators each reconstructed their entire
declared tape, including factor addresses, operations, order, scopes, arena
extents and output count. Each accepted exactly its own private builder's
answer. There was no accepted order choice for a producer to discover.

Runtime now calls the existing builders and fixed numerical kernels inside
their owner. The passive `prepare_prediction`, `execute_prediction` and
`execute_observation` convenience functions are not Runtime proposal ports.
No external plan or numerical endpoint is admitted. The reference value
adapter introduced atda532dc remains a passive frame-law witness; its
Runtime wiring and redundant exchange are superseded by elimination.

The private AMP builders were already the independent plan checkers' trusted
implementations. The fixed prediction/observation schedules were already
the exact RNE interpreters. Their numerical bodies, arithmetic interpreter
and native/word checkers are unchanged from7fe0471. Calling them directly
does not add a new trusted planner or new arithmetic schedule. Complete
post-execution plan checking, exact operation/end-point checks, native bridge,
arena ownership, paid retention, lineage and fresh/install gates remain.

The owned native initializer, observation, commit and attachment implement
the fixed G/Gamma/U registration. They are trusted implementation code, not
ports accepting caller-produced native endpoints. This result is not a
Python sandbox: replacing a private kernel, mutating a public snapshot with
`object.__setattr__`, or arbitrary globals/stack/process-memory access lies
outside its component fault model. The old counterexamples concerned
replaceable producers receiving live inputs or retaining their own outputs.
Those particular capabilities no longer exist in the fixed Runtime path.

The byte-only compressor still has a real proposal boundary and its existing
value-exchange/independent-reader proof remains necessary. A future paid
order solver would also contribute a real choice in a non-singleton class;
then the continuation-stable value interface is useful. Neither case is
permission to hand a producer live native state or numerical workspace.

## 3. Declared resources and identities

The reference model is `packed-indexed-reference-payload-v2`; its arithmetic
identity is unchanged. With D=n(n-1)/2, its prepaid metadata work returns to
64(n+1)^2(D+n+1)+128(D+n+1). It retains the earlier conservative two-pass
planning envelope, despite having one owned construction. The now-absent
value-transfer fee2048(D+n+16) is removed. Numerical work is separately
debited from the owner's plan before entering the fixed exact kernel.

The AMP work identity is
`prepaid-indexed-owned-plan-and-scalar-arena-v2`, with the existing byte-only
compression suffix. Its former conservative planning/scalar tariff and
actual paid arena extents are retained. Global/projected numerical backend,
forward IDs, rounding and complete evidence formats are unchanged. These
are declared logical work bounds, not exact CPU instruction or total heap
theorems. Each fresh physical job keeps the whole-process memory limit.

## 4. CPU evidence

`scripts/audit_indexed_owned_schedule.py --cpu` writes
`FP_INDEXED_OWNED_SCHEDULE_CPU.json`. The finite abstraction exhausts1300
input/proposal/helper-cost/cap combinations, preserves130 old successes and
admits720 additional legal successes. This is an exact finite model of the
stated elimination law, not exhaustive Python model checking.

With all six retired reference/global/projected plan/numerical ports replaced
by raising functions, real reference Runtime completes388 small histories
and776 native phase comparisons, profiles and finite ordinary closure.
Every port receives zero calls. The same audit checks the noninjective-plan
witness above and compares the unchanged AMP interpreter/checker AST bodies
against7fe0471. No torch import or owned device claim occurs in this audit.

The complete indexed Runtime, projection, global AMP and projected AMP
regressions have separate source-bound reports named
`FP_INDEXED_OWNED_SCHEDULE_{RUNTIME,PROJECTION,AMP,PROJECTED_AMP}.json`.
Prepaid-refusal spies target the actual private builder/kernel. Old proposal
substitution tests remain evidence at their historical source; the current
projection regression instead verifies that the retired ports receive no
calls during three complete native events.

## 5. Actual CUDA gate, registered before execution

Fifteen fresh4-GiB/900-second jobs are registered by the new audit script:

- Global and projected continuations with all six retired producer ports
  raising. Both must predict and learn the complete literal native state,
  with zero calls and all earlier snapshots/sealed records preserved.
- One bit changed in one fresh actual prediction word, observation gradient
  word, or primitive add output; plus the projected prediction-word case.
  Independent checks must refuse before publication/learner advance, keep
  native and physical predecessors and all older metadata unchanged, and
  retain the actual target precisely when it has been observed. These
  mutate no old tensor or native metadata and replace no schedule/checker.
- Global/projected profiles, n256 with literal world builders forbidden,
  global/projected fresh installation and subsequent learning, projected
  ordinary closure, unfunded execution, and second-lineage commit refusal.

All execution inputs must be committed before launch; source remains fixed
while live. Every outcome is retained in a fresh
`FP_INDEXED_OWNED_SCHEDULE_CUDA_A*.json`. Failed attempts are not overwritten
or silently retried. Full phase readers and existing independent numerical,
native lineage and fresh/install assertions remain mandatory.

No `CERTIFIED_COMPLETE` class, indexed full release, model-science advantage
or completed model stream is claimed by this component gate. The next
substantive solver frontier is still paid query-order choice; it is not a
reason to change FP semantics or discard the complete retained native state.

## 6. Actual CUDA A1 result

All fifteen fresh jobs pass atcdea7db05577ecd8771e6903a921f7a7018cdb18 in
`FP_INDEXED_OWNED_SCHEDULE_CUDA_A1.json`. Each is attached to its4-GiB job
before execution and exits zero without timeout or limit termination.
Maximum job commitment is2,394,525,696 bytes. Source and all execution
inputs stayed committed and fixed throughout the matrix.

Both removed-port cases receive zero calls, preserve earlier snapshots and
sealed metadata, and complete the literal native/AMP update. All four
one-bit physical faults are refused with no publication/learner advance;
predecessors and old records remain intact. Only the gradient case has an
observed target, which is retained as0. These six cases check35 complete
phase records, including their failed final frames.

Seven numerical integrations check354 phases and48663 floating words,
including16080 half words. Both profile paths pass58 phases. The global
n256 path checks42594 words and the projected path514, with literal world
builders disabled in both. Both fresh-evidence paths cross at20, install
with alpha1/2 retained, and learn to21. Projected ordinary closure seals
without a class decision. The two other integrations separately confirm
preflight refusal before any numerical executor entry and second-lineage
commit refusal retaining the observed target and both observed states.

This closes the stated fixed-schedule producer and fresh-output fault gate.
It is not a complete indexed release or an optimization-class certificate.
No model worker ran, and no time/memory superiority is inferred. Continue
with paid order search and its explicit structural/numerical decision class;
do not rerun these terminal jobs without a substantive new change.
