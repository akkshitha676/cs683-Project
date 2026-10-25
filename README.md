# LLBP-X Capacity-Sensitivity Study — CS683 Project

This repository contains a CS683 research project based on the public
[LLBP-X artifact](https://github.com/dhschall/LLBP-X). It studies whether
LLBP-X can recover branch-prediction accuracy when the tagged tables in
the base TAGE-SC-L predictor are reduced.

The source artifact is associated with *The Last-Level Branch Predictor
Revisited* (HPCA 2026). This repository preserves the upstream implementation
and records the additional capacity variants, experiment outputs, and analysis
used for this project.

## Research question

**How much of the prediction accuracy lost by reducing the base TAGE-SC-L
capacity can LLBP-X recover?**

The key distinction is between improving over a smaller TAGE-SC-L baseline
and beating the original full-size baseline. These are different comparisons.

## What this project adds

- Reduced-capacity predictor variants at LogG=9 and LogG=8.
- Evaluation over the artifact's 14 official server workloads.
- Matched runs using 100 million warmup instructions and 200 million measured
  instructions, with BTB simulation enabled.
- Per-run logs, result CSVs, trace-integrity records, provenance, and analysis
  scripts for the Checkpoint I evaluation.

The capacity experiments use the accuracy-only LLBP-X configuration:
timing simulation is disabled and `optW=0`. They therefore measure prediction
accuracy, not cycle-accurate latency or full-system performance.

## Main results

The metrics below are calculated from the recorded instruction and
misprediction counts. The geometric-mean ratio reduction is the primary
normalized comparison; pooled reduction is reported separately.

| Comparison | Geometric-mean MPKI-ratio reduction | Pooled reduction |
|---|---:|---:|
| Full-size 64K LLBP-X vs. full-size TAGE-SC-L | 12.92% | 13.41% |
| LogG=9 LLBP-X vs. same-capacity TAGE-SC-L (Metric A) | 21.37% | 19.98% |
| LogG=9 LLBP-X vs. full-size TAGE-SC-L (Metric B) | 7.22% | 8.22% |
| LogG=8 LLBP-X vs. same-capacity TAGE-SC-L (Metric A) | 32.34% | 27.82% |
| LogG=8 LLBP-X vs. full-size TAGE-SC-L (Metric B) | 1.09% | 2.85% |

Against its same-capacity standalone baseline, LLBP-X improves on all 14
workloads at both reduced capacities. Against the original full-size
baseline, LogG=9 wins on 13 of 14 workloads, while LogG=8 wins on 6 of 14.

**Main insight:** a large improvement over a reduced-capacity baseline does
not necessarily mean the reduced-capacity design beats full-size TAGE-SC-L.
LogG=9 gives the more consistent result; LogG=8 is workload-dependent.

The full-size standalone TAGE-SC-L MPKI values match the paper's Table I to
two decimal places according to the project's independent result review.
The paper reports approximately 12.1% average improvement for standard
LLBP-X in §VII-A. The comparison is not an exact reproduction: the paper's
aggregation convention is not explicit in that discussion, and the current
runs use the accuracy-only, zero-latency model.

## Metric definitions

For each workload:

- \(T_s\): standalone TAGE-SC-L MPKI at the selected capacity.
- \(X_s\): LLBP-X MPKI at that same capacity.
- \(T_{64}\): full-size 64K standalone TAGE-SC-L MPKI.

**Metric A — same-capacity improvement**

\[
100\frac{T_s-X_s}{T_s}
\]

This measures LLBP-X's gain over the standalone baseline at the same capacity.

**Metric B — full-size reference comparison**

\[
100\frac{T_{64}-X_s}{T_{64}}
\]

This measures whether reduced-capacity LLBP-X beats the original full-size
TAGE-SC-L baseline. At 64K, the two metrics coincide; at smaller capacities,
they answer different questions.

Geometric-mean ratio reduction, arithmetic mean of per-workload percentages,
and pooled reduction are distinct summaries. Always label the aggregation
method when reporting a number.

## Experimental configurations

| Capacity point | Standalone baseline | LLBP-X variant | TAGE configuration |
|---|---|---|---|
| Full size | `tage64kscl` | `llbpx` | LogG=10, LogB=13 |
| LogG=9 | `tage64kscl-reduced-tagged` | `llbpx-reduced-tagged` | LogG=9, LogB=13 |
| LogG=8 | `tage-logg8scl` | `llbpx-logg8` | LogG=8, LogB=13 |

The runs use the same workload windows and BTB setting. They do not establish
latency, IPC, energy, or physical implementation benefits.

## Repository layout

- `bpmodels/`: predictor implementations and model registrations.
- `scripts/`: build, trace-download, evaluation, and analysis scripts.
- `results/checkpoint1/`: compact result CSVs, per-workload metrics, and raw
  experiment logs for Checkpoint I.
- `docs/`: experiment protocol, claims ledger, provenance, threshold mapping,
  and the preserved upstream README.

## Reproducing the analysis

Build and trace-download instructions for the upstream simulator are preserved
in [`docs/UPSTREAM_README.md`](docs/UPSTREAM_README.md).

The server traces are not redistributed in this repository because they occupy
tens of gigabytes. They are available from the upstream Zenodo artifact:
[10.5281/zenodo.13133242](https://zenodo.org/records/13133242).

Trace names and expected MD5 checksums are listed in
[`results/checkpoint1/required-traces.md5`](results/checkpoint1/required-traces.md5).
Trace downloads must pass checksum and gzip-integrity checks before evaluation.

The completed Checkpoint I result files are provided for inspection. The
runner scripts resolve paths relative to the repository and write fresh runs
under `results/checkpoint1/reruns/`, preserving the published results. A rerun
requires the original traces, successful trace-integrity validation, a build
whose predictor binary matches the recorded checksum, and a clean tracked
working tree. The capacity runner also verifies that the validated source
commit is an ancestor of the checked-out commit.

## Storage estimates

The primary source-based accounting estimates combined storage of approximately
574.5 KiB for LogG=10, 553.7 KiB for LogG=9, and 543.3 KiB for LogG=8. These
correspond to estimated reductions of about 3.6% and 5.4% for LogG=9 and LogG=8
relative to LogG=10. An alternative source-based accounting method gives
somewhat different totals; see the claims ledger.

These are estimates from source-level parameters, not physical silicon-area
or energy measurements. These experiments are not iso-storage comparisons
against a 64 KiB baseline.

## Checkpoint II direction

The next stage will investigate timing-aware behavior and refine the
storage/latency analysis. Any latency, energy, IPC, or physical-design claims
require separate evidence and are not established by Checkpoint I.

## Attribution and license

This project builds on the original
[LLBP-X repository](https://github.com/dhschall/LLBP-X) and its associated
paper. Please consult the upstream project and preserved license for original
authors, publication details, and reuse terms. The source tree includes the
upstream `LICENSE`; contributions and results specific to this CS683 study
are documented in the checkpoint evidence.
