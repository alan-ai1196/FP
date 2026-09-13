# ERC-1 / RTX 3090 experiment 1: known-table resource and precision frontier

Protocol registered before target execution. Foundation R4, XVII.31,
ERC-1 and the scoped Runtime release remain frozen. This experiment uses
the two existing LIMIT_ONLY tables from
[`node_edge_precision_accuracy_audit.py`](../../theory/numerical_checks/node_edge_precision_accuracy_audit.py):

| Name | Q at x=0 | Q at x=1 | Critical cap R0 |
|---|---|---|---|
| scalar | (5/8, 3/8) | (5/8, 3/8) | 8/3 |
| mixed | (1/4, 3/8, 3/8) | (1/4, 1/3, 5/12) | 4 |

Q is public **before construction**. The question is how actual native
resource consumption and accuracy change with construction depth on the
frozen half/single executor. It is not recovery of an unknown table,
optimization over the entire grammar, a learning/population claim, or
a new static theorem. An unrestricted Q oracle has probability error zero;
it is a diagnostic floor, not a local-alphabet resource-feasible competitor.

## Registered comparisons

All graphs use binary unary sources, base one, local SUM weights
(1/2, 1, 2), shared binary PRODUCTs, and one final normalization. All three
parameter slots remain owned, including unused slots. Each graph enters as
the registered initial Program of its own complete Runtime. There is no
external candidate selection, state replacement or installation claim.

At R0 compare, for **each** table:

* Fixed-P singleton/Horner approximation, flooring ideal excesses to
  denominator 2^L, L in (4, 8, 16, 24, 32).
* A stronger fractional-Horner realization of exactly the same excesses
  at the same five levels. It processes fraction bits from least to most
  significant using `(current + bit * source)/2`, avoiding a tiny initial
  seed followed by repeated amplification.
* The existing shared reciprocal construction at n in (1, 2, 3, 4, 5).

At each positive slack h = (D-1) R0 (1/4)^(2^n), compare the following
three methods. Here D is the common denominator of ideal excesses:
D=3 and n in (1, 2, 3, 4) for scalar; D=6 and n in (2, 3, 4, 5) for mixed.
All registered h are at most one.

* The existing shared reciprocal with its counted positive tail repair.
* Exact singleton masses from the smallest-denominator dyadic row scale
  in [1/min(a), (R0+h)/sum(a)], with ordinary Horner.
* The same exact singleton masses with fractional Horner.

There are **54 configurations**. Singleton controls group equal column
coefficients before scaling; all grouping SUMs, scaling, empty heads and
edges are counted. This strengthens the existing generic singleton upper.
The alternate Programs have distinct parameter-response lineages; equal
initial functions are not claimed to make their gradients interchangeable.
No uncounted arbitrary coefficient or free multiplication is introduced.
We do not claim these finitely many Programs are the all-graph optimum.

## Data, execution and resources

Each row's minimal integer label frequencies are delivered in context order
(x=0, then x=1), and within a context in increasing label order: 16 ordinary
events for scalar, 20 for mixed. Thus the closed stream's empirical table
equals the registered known Q. The data law is explicitly
`declared-exogenous-no-probability-guarantee`; no fresh evidence rule or
stochastic assumption is registered. Empty owned `CudaCompilerPolicy(())`
closes the stream. Learning rate is zero, update unit two, commit grid 16;
both reference and device still execute and retain gradients and commits.

The immutable Runtime manifest owns the actual Program, source domain,
online contract, numerical tolerances, policy and resource limits. This
protocol additionally registers known Q and the external comparison plan;
post-run evaluation does not issue a Runtime certificate about external Q.
Q is also recoverable from the actually retained labels of every sealed run.

| Coordinate | Fixed registration |
|---|---|
| Native caps | nodes/SUMs/PRODUCTs 1,000 each; edges 10,000; slots 100 |
| Range | T <= R0 or R0+h; native activation <= max(1, cap-k); full two-context domain |
| Exact reference | 32,768 integer bits; packed payload 1 GiB; 100,000 objects; work 10^13 per role |
| CPU branch | Continuous binary64; absolute state/probability tolerance 2^-24 |
| CUDA branch | Frozen eager half forward/storage; ordered single accumulation/readout/division/backward/master; absolute state/probability tolerance 1/100 |
| CUDA evidence | 4,096 output cells and 131,072 bytes per phase |
| Native CUDA storage | 16 MiB arena, 32 MiB reservation bound, both roles |
| Physical board | Frozen actual RTX 3090 binding; separate 24 GiB whole-board residency envelope |
| Host | Fresh Windows worker fenced before first instruction; 4 GiB process/job commitment; one process; 10 minute observation timeout |

No caps/tolerances/depths are adapted to observed successes. First failed
ordinary endpoint stops that configuration. Failure reason, checked prefix,
any fully retained failed output and absence of closure remain in the
record. Unresolved prefixes never supply complete-domain metrics. A worker
crash or timeout is an experiment execution failure, not a numerical result.

## Evaluation and minimal evidence

Before target execution, exact arithmetic checks every graph on both
contexts and independently differentiates every label loss. Fractional
Horner's coefficient identity is exhaustively checked on the denominator
256 grid. These are constructor checks, not a new release prerequisite.

Actual retained CUDA phases are replayed by the existing independent exact
rounded interpreter. CPU phases use the independent Python float
interpreter. Failure outputs, when fully materialized, are compared too;
their raw equality does not make their reference bridge successful.
Reference event gradients are checked against forward differentials.
Complete owned policy/report, buffers and current learners remain checked.

Report native P/S/E separately; direct exact materialization volume and
significand width; minimum nonzero reference/device activations and
underflows; mathematical normalization of retained single masses **and**
raw rounded single predictions against Q; complete-state error; packed
peak; native consumed arena extent; actual fenced host peak/exit records.
All raw result metrics identify whether both contexts were executed.

The fixed arena and board capacity are not smaller-FP-VRAM observations.
Whole-worker CPU ticks include construction, Runtime and independent audit;
they are not inference latency, GPU time or a speedup benchmark. No timing
claim or statistical significance test is planned from these single runs.
No weights, datasets, full phase logs or expanded graphs are retained.

Run `python -B experiments/erc1_rtx3090/resource_frontier.py --preflight`,
commit the protocol and code, then run the same script with `--write`.
The result records the committed source. Analysis and any follow-up are
reported separately from this preregistration.
Completed workers are retained incrementally as `PARTIAL_EXECUTION` until
all 54 finish. `--write --resume` can continue such a record. It preserves
each worker's execution revision and checks unchanged constructors,
parameters, Runtime, audit dependencies and this protocol; a reporting or
independent-replay correction is not permission to tune the experiment.
