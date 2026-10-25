# LLBP-X Capacity-Sensitivity Study: CS683 Project

This research project builds on the public [LLBP-X artifact](https://github.com/dhschall/LLBP-X). It asks how much prediction accuracy LLBP-X recovers when the base predictor becomes smaller.

The base TAGE-SC-L predictor combines TAGE (Tagged Geometric History Length), a Statistical Corrector (SC), and a Loop predictor (L). LLBP-X extends the Last-Level Branch Predictor (LLBP) with dynamic context-depth adaptation. Mispredictions per thousand instructions (MPKI) measure prediction errors. Branch target buffer (BTB) simulation is enabled in every run. This checkpoint does not measure instructions per cycle (IPC), energy, or physical area.

## Research question

**How much of the prediction accuracy lost by reducing base TAGE-SC-L capacity can LLBP-X recover?**

Two comparisons answer different questions. Metric A compares LLBP-X with standalone TAGE-SC-L at the same capacity. Metric B compares reduced-capacity LLBP-X with the original full-size TAGE-SC-L baseline.

## What this project adds

- Reduced-capacity predictor variants at LogG=9 and LogG=8.
- Evaluation over the artifact's 14 official server workloads.
- Matched runs using 100 million warm-up instructions and 200 million measured instructions.
- 84 total runs: 28 each at LogG=10, LogG=9, and LogG=8.
- CSV result files, per-run logs, trace-integrity records, provenance, and analysis scripts.

The capacity experiments use the accuracy-only configuration: timing simulation is disabled and optW=0. These experiments measure prediction accuracy. They do not measure cycle-accurate latency or full-system performance.

## Main results

The results use recorded instruction and misprediction counts. The geometric-mean ratio reduction is the primary normalized comparison. Pooled reduction is reported separately.

| Comparison | Geometric-mean MPKI-ratio reduction | Pooled reduction |
|---|---:|---:|
| Full-size 64K LLBP-X vs. full-size TAGE-SC-L | 12.92% | 13.41% |
| LogG=9 LLBP-X vs. same-capacity TAGE-SC-L (Metric A) | 21.37% | 19.98% |
| LogG=9 LLBP-X vs. full-size TAGE-SC-L (Metric B) | 7.22% | 8.22% |
| LogG=8 LLBP-X vs. same-capacity TAGE-SC-L (Metric A) | 32.34% | 27.82% |
| LogG=8 LLBP-X vs. full-size TAGE-SC-L (Metric B) | 1.09% | 2.85% |

LLBP-X improves over the same-capacity standalone baseline on all 14 workloads at both reduced capacities. Against full-size TAGE-SC-L, LogG=9 wins on 13 of 14 workloads. LogG=8 wins on 6 of 14.

**Main insight:** a large improvement over a smaller baseline does not prove that the design beats the full-size baseline. LogG=9 gives the more consistent result. LogG=8 is workload-dependent.

The 14 recorded full-size standalone TAGE-SC-L MPKIs were compared workload by workload with Table I and match to two decimal places. The primary paper is [“The Last-Level Branch Predictor Revisited” (HPCA 2026)](https://2026.hpca-conf.org/details/hpca-2026-main-conference/7/The-Last-Level-Branch-Predictor-Revisited). The upstream analysis notebook (`analysis/mpki.ipynb`) labels `llbpx-timing-ae` as `LLBP-X` and `llbpx-ae` as `LLBP-X-0Lat`. Its `Mean` bar reports the reduction calculated from mean MPKI values. This project reports the accuracy-only `llbpx` model with `simulateTiming=0`, using geometric-mean MPKI-ratio reduction and a separately computed pooled reduction. The 12.92% and 13.41% values therefore are not a direct reproduction of the paper's approximately 12.1% result. A matched timing-enabled comparison is a next-step experiment.

## Absolute MPKI

The table below reports the arithmetic mean of the 14 workload MPKIs, recomputed from raw misprediction and instruction counts. These absolute MPKI means are separate from the normalized geometric-mean ratios and the pooled reduction reported above.

| Capacity | Standalone TAGE-SC-L mean MPKI | LLBP-X mean MPKI |
|---|---:|---:|
| Full size, LogG=10 | 2.916 | 2.525 |
| LogG=9 | 3.345 | 2.677 |
| LogG=8 | 3.925 | 2.833 |

## Metric definitions

For each workload:

- T_s is standalone TAGE-SC-L MPKI at the selected capacity.
- X_s is LLBP-X MPKI at that same capacity.
- T_64 is full-size 64K standalone TAGE-SC-L MPKI.

**Metric A : same-capacity improvement**

Metric A = 100 × (T_s - X_s) / T_s

This measures LLBP-X's gain over standalone TAGE-SC-L at the same capacity.

**Metric B : full-size reference comparison**

Metric B = 100 × (T_64 - X_s) / T_64

This measures whether reduced-capacity LLBP-X beats the original full-size baseline. At 64K, the metrics coincide. At smaller capacities, they answer different questions.

The geometric mean summarizes normalized per-workload MPKI ratios. Pooled reduction is computed separately from total mispredictions and total measured instructions. The report does not use an arithmetic mean of per-workload percentage ratios.

## Experimental configurations

| Capacity point | Standalone baseline | LLBP-X variant | TAGE configuration |
|---|---|---|---|
| Full size | tage64kscl | llbpx | LogG=10, LogB=13 |
| LogG=9 | tage64kscl-reduced-tagged | llbpx-reduced-tagged | LogG=9, LogB=13 |
| LogG=8 | tage-logg8scl | llbpx-logg8 | LogG=8, LogB=13 |

The runs use the same workload windows and BTB setting. They do not establish latency, IPC, energy, or physical implementation benefits.

## Changes relative to upstream

The study-specific implementation, experiment runners, validation, and reporting changes are listed in [the changes guide](docs/changes_relative_to_upstream.md). The underlying LLBP-X artifact remains attributed to its original repository and paper.

## Repository layout

- `bpmodels/`: predictor implementations and model registrations.
- `scripts/`: build, trace-download, evaluation, and analysis scripts.
- `results/checkpoint1/`: result CSV files, per-workload metrics, integrity checks, and experiment logs.
- `docs/`: experiment protocol, claims ledger, provenance, threshold mapping, and preserved upstream documentation.
- `traces/`: precomputed context/pattern CSV files used by the separate `llbpx-optw` variant with `--tableload`. The reported `llbpx` runs use `optW=0` and do not consume these files.

## Presentation and recording materials

Presentation notes and limitations are documented in [the presentation notes](docs/presentation/README.md). The speaker script and presentation files are supplied separately as submission materials.

The editable PowerPoint and PDF export are supplied separately as checkpoint submission files. They are not stored as binary assets in this repository revision.

## Reproducing the analysis

Build and trace-download instructions for the upstream simulator are preserved in [upstream build and trace-download instructions](docs/UPSTREAM_README.md).

The original large server instruction traces are not redistributed here. They are available from the upstream artifact at [Zenodo record 13133242](https://doi.org/10.5281/zenodo.13133242). The precomputed pattern CSVs in traces/ are separate files used by LLBP-X and are included in this repository.

Expected MD5 checksums are listed in [trace checksum list](results/checkpoint1/required-traces.md5). Trace downloads must pass checksum and gzip-integrity checks before evaluation.

The published integrity log records successful gzip-integrity checks for all 14 traces. Runner console logs record the completed simulator runs. Analysis validation checks paired instruction counts and MPKI calculations. See [trace integrity log](results/checkpoint1/full_trace_gzip_validation.log), [analysis validation record](results/checkpoint1/analysis_validation.txt), and [capacity results summary](results/checkpoint1/capacity_gate_report_summary.md).

To regenerate the plots from the committed result CSV files, run `python3 scripts/plot_checkpoint1.py`. The script validates paired workload counts and produces the absolute MPKI chart, aggregate and normalized reduction charts, per-workload Metric B chart, storage-estimate chart, and `absolute_mpki_means.csv` under `results/checkpoint1/figures/`. The storage chart uses the source-based estimates documented in this repository.

The completed Checkpoint I results are provided for inspection. Runner scripts write fresh runs under results/checkpoint1/reruns/ and preserve published results. A rerun requires the original instruction traces, successful integrity validation, a build whose predictor binary matches the recorded checksum, and a clean tracked working tree. The capacity runner also checks that the validated source commit is an ancestor of the checked-out commit.

## Storage estimates

The primary source-based accounting estimates combined storage of approximately 574.5 KiB for LogG=10, 553.7 KiB for LogG=9, and 543.3 KiB for LogG=8. These correspond to estimated reductions of about 3.6% and 5.4% relative to LogG=10. An alternative source-based accounting method gives somewhat different totals. The claims ledger and experimental protocol document both methods.

These are estimates from source-level parameters, not physical silicon-area or energy measurements. The comparisons are not iso-storage comparisons against a 64 KiB baseline.

## Checkpoint II direction

Checkpoint II examines timing-aware behavior and refines the storage/latency analysis. It first checks what accessDelay models in the source, then uses a documented sensitivity sweep. Timing outputs remain approximate model results. They do not support claims about cycle-accurate latency, IPC, energy, or physical implementation benefits without separate evidence.

## Conclusion

The checkpoint validates a 14-workload, three-capacity accuracy study. LogG=9 gives the strongest observed balance: it halves tagged entries and beats full-size TAGE-SC-L on 13 of 14 workloads. LogG=8 shows that same-capacity gains can conceal losses against the full-size reference.

Repository: [CS683 project repository](https://github.com/akkshitha676/llbpx-capacity-sensitivity). The study builds on the original [LLBP-X artifact](https://github.com/dhschall/LLBP-X); see its documentation and license for original authorship, publication details, and reuse terms.
