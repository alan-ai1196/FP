# Frozen token reporting: scope, loss bounds and owned execution

Status: conditional proof, exact/CPU controls and both fixed actual RTX3090
workers **PASS** at8adf9af. Both workers are terminal. No corpus, language
score, fresh persistence result, installation or Compiler completeness claim.
Foundation and ERC-1 remain frozen; the rational/relation branch stays closed.

**Correction:** section7 falsifies the old public-snapshot immutability
assertion and repairs it in CPU Runtime logic. The two device results above
remain observations of their declared traces, not coverage of this attack.
The corrected implementation has no new device qualification yet.

The first text comparison may test one preregistered native G/Gamma/U without
adaptive graph replacement. Its evaluation must still belong to the same
paid complete Runtime. A passive predictor applied to an exported snapshot
does not establish that ownership. This implementation supplies a terminal
reporting epilogue for that narrower empirical claim. It adds no architecture
action and grants no authority to select or install another graph.

## 1. The two clocks and the frozen state

`TokenReportingContract(stream_id, log_terms, accumulator_bits)` is optional
constructor data. It wraps the actual run manifest only when present; old
default manifests do not change. The declared stream must already have a
validation/test role, unique observation identities and the complete indexed
past-token source interface with no caller-supplied inputs. The declared
training horizon must contain whole optimizer units.

`begin_report()` is eligible only after that entire horizon has completed,
with a committed range-safe incumbent. It retains the actual native learner,
program identity and current physical phase. Once reporting starts, all
ordinary learning, construction, query, persistence and installation ports
are permanently closed, including after reporting completes or fails.
Snapshots remain passive. Old installation classes keep both new reporting
coordinates `None`, and retain them unchanged through the existing root copy.
Token installations remain unimplemented, as before.

The learner clock stays at its final training cursor. The reporting source
clock starts at zero and advances on the declared reporting stream. At its
position t, lag l reads reporting target t-l when available and PAD otherwise.
There is no EOT-triggered reset. Every original context, identity, target and
forecast is retained. This is a fixed file/stream-boundary convention; arbitrary
subsampling does not authorize replacing a corpus's original context. A text
preregistration must bind its actual stream construction to this convention.

**Frozen-state induction.** Initially the saved incumbent is the actual
committed native learner and physical phase. Reporting prediction evaluates
that learner on its owned reporting context. Target scoring invokes no native
observation, gradient, optimizer or attachment transition. The physical
`report:readout` executes the existing target-mass recipe from the actual
forecast, compares every new primitive/output word with its guarded CPU
decision, and rechecks the full predecessor and forecast. Its acceptance
publishes neither a staged nor a current physical learner. The next reporting
event therefore has the same native learner and physical state. The common
public-port gate prevents an intervening Compiler action from invalidating
the induction. This is a statement about the closed supported ports, not
arbitrary external mutation of Python/CUDA memory.

Previous reporting labels may affect later reporting *contexts*, as required
for next-token prediction. They cannot affect training, G, Gamma, U, a search
or persistence evidence within this Runtime. External human/model tuning
across runs remains an experiment-protocol issue; a read-only Runtime cannot
turn exposed development data into fresh evidence.

## 2. Normalize the physical distribution before scoring

For a given owned pre-target context, let m_y > 0 be the binary32 mass defined
by the registered readout recipe on the actual retained physical operands.
The mathematical decoder is

    S = sum_y m_y,      p_y = m_y / S.

The existing all-label envelope proves S in [L,U] without executing all
unqueried label/context pairs. This is a conditional recipe bound, not a
claim that those masses were materialized on the GPU. The actual revealed
target mass m is then separately executed and checked against that same
recipe/forecast. The rounded division by the stored normalizer Z is retained
but is not the proper probability. For example, three binary32 masses
11184811/33554432 have sum 33554433/33554432, whereas stored Z can be exactly
one. Their properly normalized probabilities are all exactly 1/3.

**Loss enclosure.** Given the complete-operand/recipe premises, actual target
mass m and 0 < L <= S <= U, monotonicity of log gives

    max(0, log(L/m)) <= -log(p_target) <= log(U/m).

The lower clipping uses the independently known S >= m. A claimed U < m is
inconsistent and rejected. The native forecast is scored separately with
its exact target probability q: set m=q and L=U=1. This does not identify the
native and physical learners or claim an exact physical likelihood gradient.

The implementation uses the existing guarded exact rational log enclosures,
with a fixed preregistered number of terms and reference integer allowance.
It prepays the logarithm operations before computing them. Missing work,
storage, precision or numerical relation yields `UNRESOLVED`; no clamping of
probabilities, retroactive tolerance change or fake completed score is used.

Before numerical logarithm error, the physical interval's width is at most
log(U/L), independently of the target mass. Thus a useful all-label relative
normalizer enclosure suffices for a useful proper log score. Absolute native
probability error alone is not silently treated as a relative loss bound.

## 3. Directed mean accumulation with bounded denominators

Suppose event i has a valid exact loss interval [a_i,b_i]. For a fixed
q=2^-p, retain integer accumulators

    A_N = sum_i floor(a_i / q),
    B_N = sum_i ceil(b_i / q).

Then [q A_N/N, q B_N/N] encloses the finite-stream mean. Each endpoint's added
rounding error is less than q, **independently of N**. The interval width is
at most the mean event-interval width plus 2q. Combined with the preceding
lemma, this is at most mean log(U_i/L_i), mean logarithm approximation width,
and 2q. This avoids multiplying all event rational denominators merely to
report one mean. Integer size still grows with accumulated magnitude; the
registered integer guard remains binding. A huge p is rejected before any
unbounded shift. Every event's full retained numerical record is preserved.

This law concerns numerical reporting accuracy, not generalization error.
No independence, stationarity, population confidence or fresh stochastic
filtration is inferred from a finite deterministic text tape.

## 4. Owned ports and failure prefixes

`predict_report(id)` accepts only the next preregistered identity. It pays
source reconstruction and evaluation, reserves the fixed target slot, retains
the original context, obtains the exact forecast and, when registered, the
actual checked AMP forecast. It cannot accept a caller context or probability.

`observe_report(target)` requires that actual pre-target event. It records the
revealed target and reporting data use, fills its prepaid slot, and then pays
the score calculation. The native forecast is independently recomputed on
the same frozen learner/context. The physical readout must retain the same
owned predecessor/observation/forecast identity, every original physical word
and the full new checked phase. Native and physical accumulators stay distinct.
The full event and accumulators are retained before publishing a scored event.

After target publication, numerical/work/retention refusals keep the target,
context, forecast and earlier paid buffers; neither learner advances and no
failed event enters the mean. Host-allocation failure uses the existing
terminal boundary. This is not crash recovery or a promise that an allocation
failure before an ingress is published produces a completed ingress record.

`report_result()` decodes a mean only after all fixed reporting events succeed.
Incomplete/failed prefixes provide a diagnostic status, not a completed
finite-stream score. `COMPLETE_REPORT` means exactly that declared finite
stream of the fixed incumbent under this registration. It is not
`CERTIFIED_COMPLETE`, a search optimum, a population claim or a whole-Compiler
release. The ordinary cursor, records, learners and existing obligations are
preserved. Full CUDA frames keep the existing paid whole-byte retention;
no device allocation, old phase or carry cache is reclaimed.

## 5. Exact/CPU evidence and original device registration

`scripts/audit_token_reporting.py --write` currently passes:

- 162 normalized-mass cases with exact fractions and an independent
  Decimal90 loss calculation; 64 directed-mean prefixes and huge-scale refusal.
- Every binary two-token training/three-token reporting word: 32 histories,
  96 report events, exact agreement with the literal native graph, 416 complete
  reporting records decoded, unchanged learners and original training records.
- All 28 ordinary/control public ports closed after freezing; identity/order,
  split-role, repeated-target, partial-training and precision refusals.
- Five injected post-target work/storage/forecast/host failures plus an actual
  logarithm integer-limit refusal, preserving the target and old learners.
- 75 checked CPU array phases and 48 normalized physical label losses; eight
  full owner-phase CPU controls and three origin/identity/forecast refusals.

Minimal evidence is `evidence/minimal/FP_TOKEN_REPORTING_CPU.json`. Ordinary
event, CPU installation and token phase regressions pass. The host-failure
current-port/current-prefix sections pass. Its historical adapter is stale:
it passes `indexed_order_search` to the dfa1583 constructor, so the full old
adapter run is **not** reported as passing. No unrelated adapter rewrite or
old device replay is needed for this result.

The registration required the original shared-retention A1 to terminate and
all sources to be committed before `scripts/run_token_reporting_audit.py --run`.
It refuses an existing journal and an active canonical shared-retention A1.
The two fresh workers were fixed before outcomes:

- `frozen-report`: the existing mixed native token graph, four training labels
  (two units) followed by four report labels; verify frozen actual learners,
  original report clocks, paid complete phases and both mean enclosures.
- `forecast-forgery`: the same four-label training registration; alter the
  actual first reporting forecast's source after prediction, then reveal its
  target. The owner must retain that target and reject the readout without
  publishing a loss or learner.

Each uses a 4-GiB host job, 180-second wall cap, one 32-MiB CUDA arena with the
same allocator cap, 384-MiB reference payload, 10^15 work per role, 4096 output
cells per phase and 1-MiB complete frames. The existing state/probability
tolerances are 1/4 and 1/10000. Shared literal/program/expanded/reference caps
are each 2^20, comparison cap 2^22. Log terms=12 and accumulator p=40.
No corpus is read. Save the original outcome in FP_TOKEN_REPORTING_A1.json;
do not replay it or infer full-vocabulary feasibility from this small control.
After this boundary, return to affordable owned text training and competitive
baselines rather than adding further reporting variants.

## 6. Terminal actual reporting result

Both workers pass at8adf9af on the pinned RTX3090. The original four-hour
shared-retention A1 had already terminated and its journal was committed
before this independent reporting attempt began. No corpus was opened.

| Worker | Checked phases / device words | Peak job commitment | Launcher wall |
|---|---:|---:|---:|
| frozen-report | 19 / 6,340 | 1,983,094,784 bytes | 4.8764097 s |
| forecast-forgery | 12 / 4,987 | 1,848,635,392 bytes | 4.1573055 s |

The first worker completes four training events/two units followed by four
owned reports, retaining separate exact native and proper physical mean
enclosures. Both actual learners remain frozen. Paid reference peak is
4,045,956 bytes; arena consumption is34,376 bytes in1,827 regions.

The second completes its same two training units, changes the actual first
reporting forecast after prediction and then reveals the real target. That
target remains owned; the readout refuses, with zero scored report events
and no loss or learner published. Paid reference peak is3,860,654 bytes;
arena consumption is27,280 bytes in1,394 regions. Both workers preserve the
original single32-MiB backing allocation and lifetime allocator peaks.

Minimal evidence is `evidence/minimal/FP_TOKEN_REPORTING_A1.json`; the journal
and jobs are terminal and must not be replayed. This establishes the two
declared finite device controls, not full-vocabulary reporting feasibility,
language quality, fresh persistence, installation, a search certificate or a
complete Compiler release. Stop reporting variants. The remaining immediate
boundary is affordable owned full-vocabulary training under the original
model/numerical/resource limits, followed by a concrete strong text comparison.

## 7. Public snapshot counterexample and value-boundary repair

At a7d2232, `IndexedCudaPhase` is a frozen outer dataclass, but the token
producer inserts ordinary relation and execution-plan dictionaries into it.
Both the public snapshot and the live owner retain that same phase object.
Sealing a separate immutable encoding does not freeze the original object.

After two ordinary training labels (0,1), freeze the toy incumbent and obtain
its first reporting forecast through the public Runtime. Its actual target-0
recipe mass is8422541/16777216 and the sum of both masses is10503637/8388608.
The proper probability is therefore8422541/21007274, strictly below one.
Change only the public phase relation's `stored_sum_lower` and
`stored_sum_upper` entries to that target mass, then reveal target0 normally.
The old reporter reads these altered bounds from the old forecast and emits
`COMPLETE_REPORT` with physical mean [0,0]. The native mean remains unchanged.
The sealed forecast bytes are intact but no longer match the public record.
Both plain and shared retention admit this counterexample. It needs no
private Runtime field, tensor write, object-level frozen-dataclass bypass,
changed model, resource limit or numerical tolerance.

The corrected phase boundary recursively copies relation mappings into
immutable proxies and converts mutable sequences to tuples. It wraps the
fresh plan dictionary too; its fields are immutable scalars or the frozen
`TokenWindow`. No producer-owned mutable mapping remains aliased. Canonical
encoding is unchanged. Physical scoring now takes the target recipe mass
and full-alphabet normalization bounds from the **same freshly checked
readout phase**. That phase already checks the original pre-target forecast,
source, observation and predecessor. Neither exported diagnostics nor a
retained producer dictionary can rewrite the future score.

This follows a value-boundary invariant, not a new semantic action: once
the owner publishes a phase, its live record and sealed bytes describe the
same fixed value under all supported public continuations. Immutable copies
establish the value boundary; byte equality checks establish the encoding.
The two obligations cannot substitute for each other. The proper-loss and
mean-rounding proofs are unchanged; their witness must be this owned value.

`scripts/audit_token_snapshot_bounds.py --write` runs the actual Runtime,
token phase, reporting and retention code with only device binding, arena
checks and the array backend replaced by CPU implementations. It loads the
two historical function bodies from a7d2232 to reproduce the two old failures,
then checks six current cases: unchanged, public snapshot write and mutation
of a retained producer dictionary, each with plain/shared storage. The public
write raises `TypeError`; producer mutation leaves the record intact. All
six yield the same physical mean enclosure

    [1004906220241/1099511627776, 502453437801/549755813888],

which encloses the independent Decimal90 value of
`-ln(8422541/21007274)`. The audit checks every one of their48 retained phase
frames, zero padding and unchanged canonical encoding (1,843,572 body bytes
in total), plus immutable relations/plans. It imports no Torch or CUDA.
Minimal evidence is `evidence/minimal/FP_TOKEN_SNAPSHOT_BOUNDS_CPU.json`.
Existing exact/CPU reporting and544-phase shared-word regressions still pass.

This is an implementation counterexample and CPU repair, not a Foundation
refutation or an actual-device mutation result. The old device reporting
jobs remain terminal; do not replay them. The running A2 does no reporting
and retains its original source and registration. Integrate the correction
after A2 terminates, and qualify it with the next justified text execution.
The subsequent [token reuse implementation](../../theory/proofs/TOKEN_CONTINUATION_STORAGE.md#implemented-owned-lowering-and-its-exact-scope)
uses this corrected immutable-history boundary and passes CPU controls;
its actual device qualification is pending. Do not extend this into reporting
variants.

## 8. Corrected boundary on the actual device

After shared-retention A2 terminated and the prepared correction/reuse commits
were integrated, the two fixed [owned token reuse workers](OWNED_TOKEN_REUSE.md#actual-device-result-and-closure)
pass on the RTX3090 at6941373. The successful worker completes eight training
units and two frozen reports in an8-KiB arena, retaining45 checked phases.
Both attempted public normalization writes raise TypeError and leave the
phase bytes unchanged. Native/physical learners remain frozen during scoring;
the physical mean enclosure has a positive lower endpoint and matches the
previous CPU branch control. The second worker preserves the original learner
and actual revealed target through an unsealed retention failure.

These are finite actual-device checks of the corrected boundary, not a new
language score or general mutation certificate. The historical counterexample
above is still a CPU reproduction of the old implementation. All original
reporting and reuse workers are terminal; no further reporting variant is due.
Minimal device evidence is `FP_TOKEN_REUSE_CUDA_A1.json`, with the full fixed
scope, word counts and resource observations in OWNED_TOKEN_REUSE.md.
