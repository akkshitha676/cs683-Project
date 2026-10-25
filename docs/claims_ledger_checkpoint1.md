# LLBP-X Checkpoint I — Claims Ledger

## Experimental provenance

- Source commit: `5da415efc2ffd76d6944fcf2cb306742b882d961`
- Predictor SHA-256: `d7aff66067b66480127dd1921361a2147f29d4ee1fe429cefc14c236d7926621`
- Workloads: 14 official evaluation traces
- Trace checksums: all 14 passed
- Gzip integrity: all 14 passed
- Evaluation windows: 100M warm-up, 200M measurement
- BTB simulation: enabled
- Model for reported LLBP-X accuracy results: llbpx (simulateTiming=0, optW=0)

## Claim 1 — Full-size baseline reproducibility

Status: VERIFIED

All 14 standalone TAGE-SC-L baseline MPKIs match the paper's Table I to two decimal places, according to the independent review.

PHPWiki exact check:
- ROI instructions: 199,999,983
- ROI mispredictions: 616,930
- ROI MPKI: 3.0847

Evidence in this repository:
- [64K result CSV](../results/checkpoint1/results_64k.csv)
- [64K runner console log](../results/checkpoint1/logs/runner_console_64k.log)
- [64K provenance record](provenance_64k.txt)
- PHPWiki per-run evidence: [mwnginxfpm-wiki_llbpx.log](../results/checkpoint1/logs/64k_gate/mwnginxfpm-wiki_llbpx.log)

## Claim 2 — Full-size LLBP-X accuracy improvement

Status: VERIFIED, WITH COMPARABILITY CAVEATS

- 28/28 runs completed across 14 workloads.
- Arithmetic mean of per-workload percentage reductions: 12.60%.
- Geometric-mean ratio reduction: 12.92%.
- Pooled misprediction reduction: 13.41%.
- Median per-workload reduction: 11.92%.
- Per-workload range: 2.00% to 28.47%.

The paper reports an average of approximately 12.1%, with a range of 1.4% to 27% in §VII-A. Its averaging convention is not explicit in that discussion. The results are close, but are not an exact reproduction. The run uses the accuracy-only, zero-latency LLBP-X model.

Evidence:
- [64K result CSV](../results/checkpoint1/results_64k.csv)
- [64K runner console log](../results/checkpoint1/logs/runner_console_64k.log)
- Per-workload logs are in results/checkpoint1/logs/64k_gate/ in the repository.

## Claim 3 — LogG=9 reduced-capacity result

Status: VERIFIED, INTERPRETATION SUPPORTED

- 28/28 runs completed.
- Metric A: same-capacity LLBP-X improvement over standalone TAGE.
  - Arithmetic mean: 20.60%.
  - Pooled reduction: 19.98%.
  - LLBP-X improves on the same-capacity baseline on 14/14 workloads.
- Metric B: reduced-capacity LLBP-X compared with the fixed full-size 64K TAGE baseline.
  - Arithmetic mean: 6.99%.
  - Pooled reduction: 8.22%.
  - LLBP-X beats full-size TAGE on 13/14 workloads.

Evidence:
- [LogG=9 result CSV](../results/checkpoint1/results_logg9.csv)
- [Per-workload capacity metrics](../results/checkpoint1/capacity_metrics_per_trace.csv)
- [Capacity runner console log](../results/checkpoint1/logs/runner_console_capacity.log)
- Per-run logs are in results/checkpoint1/logs/capacity_gate/ in the repository.

## Claim 4 — LogG=8 reduced-capacity result

Status: VERIFIED, WORKLOAD-DEPENDENT

- 28/28 runs completed.
- Metric A:
  - Arithmetic mean: 29.62%.
  - Pooled reduction: 27.82%.
  - LLBP-X improves on the same-capacity baseline on 14/14 workloads.
- Metric B:
  - Arithmetic mean: 0.81%.
  - Pooled reduction: 2.85%.
  - LLBP-X beats full-size TAGE on 6/14 workloads.
  - Median Metric B: -0.53%.

Interpretation: the same-capacity improvement is large, but much of it is spent recovering the accuracy lost by shrinking the base TAGE predictor. The result is workload-dependent. Do not headline the 0.81% arithmetic mean without the per-workload distribution.

Evidence:
- [LogG=8 result CSV](../results/checkpoint1/results_logg8.csv)
- [Per-workload capacity metrics](../results/checkpoint1/capacity_metrics_per_trace.csv)
- [Capacity runner console log](../results/checkpoint1/logs/runner_console_capacity.log)
- Per-run logs are in results/checkpoint1/logs/capacity_gate/ in the repository.

## Claim 5 — History threshold and Opt-W configuration

Status: RUNTIME CONFIGURATION VERIFIED

The PHPWiki LLBP-X log reports:
- histLenThreshold=22
- Runtime mapping: 22=>15:3:63:232
- optW=0
- simulateTiming=0
- NumContexts=14336
- NumPatterns=16
- CitSize=6144
- CitAssoc=6
- adaptThreshold=7

The printed TAGE configuration is nhist=36, minhist=6, maxhist=3000, LogG=10, LogB=13.

The runtime mapping associates table index 22 with history length 232. This supports the implemented threshold convention. It does not replace a complete source-level parameter-parity audit.

Evidence:
- [Threshold mapping verification](threshold_mapping_verification.txt)
- [PHPWiki LLBP-X run log](../results/checkpoint1/logs/64k_gate/mwnginxfpm-wiki_llbpx.log)

## Claim 6 — Storage trade-off

Status: ESTIMATE, NOT A PHYSICAL MEASUREMENT

Using the second source-based TAGE storage formula as the primary estimate, and approximately 524.36 KiB for LLBP-X-specific structures:

- LogG=10 combined estimate: approximately 574.5 KiB.
- LogG=9 combined estimate: approximately 553.7 KiB, about 3.6% below LogG=10.
- LogG=8 combined estimate: approximately 543.3 KiB, about 5.4% below LogG=10.

An alternate TAGE accounting formula yields combined estimates of approximately 588.3, 560.8, and 547.0 KiB respectively. These correspond to reductions of about 4.7% and 7.0%. The accounting difference must be explained when reporting this range.

These are source-based estimates, not measured silicon area, energy, IPC, or cycle-accurate latency. The comparisons are not iso-storage comparisons against a 64 KiB baseline.

## Limitations and claims not established

- The capacity experiments use the accuracy-only zero-latency model.
- One 200M-instruction measurement window is used per trace and configuration.
- Timing, energy, IPC, and physical implementation benefits are not established.
- Paper/artifact aggregation and finite-latency parity require cautious wording.
- The paper's Figure 16b caption/text ambiguity remains unresolved.
- The older three-trace pilot CSV is exploratory and is not a headline result.
- The study does not claim exact reproduction of the paper or iso-storage superiority.

## Key definitions

Metric A = 100 × (T_s − X_s) / T_s, where T_s is standalone TAGE MPKI at the same capacity and X_s is LLBP-X MPKI at that capacity.

Metric B = 100 × (T_64 − X_s) / T_64, where T_64 is full-size 64K standalone TAGE MPKI.

At 64K, Metric A and Metric B coincide. At smaller capacities, they answer different questions and must both be labelled.
