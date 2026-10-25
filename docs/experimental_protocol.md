# CS683 Checkpoint I — Preregistered Analysis Protocol
Date: 2026-10-24

## Experiment scope
Compare standalone TAGE-SC-L and accuracy-only LLBP-X at
LogG=10, LogG=9, and LogG=8 over the 14 workloads listed in
scripts/eval_all.sh.

Use 100,000,000 warmup instructions, 200,000,000 measured
instructions, and --simulate-btb. Do not enable the approximate
timing model for this capacity-reproduction experiment.

## Required validation gates
1. Verify every trace is complete and its checksum matches the
   authoritative dataset metadata.
2. Run gzip integrity tests on all downloaded trace archives.
3. Repeat the existing PHPWiki LogG=10 standalone baseline.
   Expected prior count: 616,930 ROI mispredictions.
   Investigate any mismatch before proceeding.
4. Evaluate LogG=10 standalone TAGE-SC-L and LLBP-X across all
   14 workloads before spending compute on reduced capacities.
5. Compare the LogG=10 arithmetic-mean MPKI reduction to the
   paper's reported approximately 12.1% result and examine the
   per-workload range. Treat this as a sanity gate, not a target
   to tune toward. If materially different, stop and investigate.

## Metrics for every workload t and size s
Record exact ROI instructions, ROI mispredictions, and MPKI for
both standalone TAGE-SC-L (T) and LLBP-X (X).

Metric A: reduction versus the same-size TAGE-SC-L baseline:
100 * (T(s,t) - X(s,t)) / T(s,t)

Metric B: reduction versus full-size TAGE-SC-L:
100 * (T(10,t) - X(s,t)) / T(10,t)

Report absolute MPKI and both metrics per workload. For each size,
report the arithmetic mean of per-workload reductions and a
geometric-mean sensitivity check based on X/T ratios.

At LogG=10, Metrics A and B coincide. The expected mean reduction
is approximately 12.1% according to the published result; verify
the exact definition and range from the paper.

At the nominal 16K point, calculate both Metric A and Metric B
and compare their means with the paper's reported 2.6% result.
Verify the mapping from LogG/table entries to the paper's capacity
labels before assigning the 16K label. Do not declare the figure
caption incorrect based on a single aggregate alone.

## Storage reporting
Present the LLBP-X structures bottom-up using the documented
field widths and configuration constants. Report the TAGE-SC-L
estimate under both source formulas until their accounting
difference is resolved.

Current derived estimates:
First TAGE formula plus SC and loop:
  LogG=10: 63.89 KiB
  LogG=9:  36.39 KiB
  LogG=8:  22.64 KiB

Second TAGE enabled-table subtotal plus SC and loop:
  LogG=10: approximately 50.13 KiB
  LogG=9:  approximately 29.32 KiB
  LogG=8:  approximately 18.91 KiB

LLBP-X additional structures are estimated at approximately
524.36 KiB, excluding wiring and implementation overheads.
These are estimates, not physical measurements. Report total
storage reductions as a range until the two TAGE formulas are
fully reconciled.

## Interpretation limits
The accuracy-only capacity sweep is a reproduction/validation
study of the paper's zero-cycle pattern-store model, not by
itself a new finding. The local event/tick delay sweep is an
approximation and does not establish cycle-accurate latency,
energy, IPC, or full-pipeline performance.

Do not modify the analysis rules after results arrive without
documenting the reason and preserving the original protocol.
