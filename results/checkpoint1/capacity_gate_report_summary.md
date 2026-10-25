# Checkpoint I: Capacity Evaluation Summary

Normalized comparisons use geometric means of per-workload MPKI ratios. Pooled reductions use total mispredictions and total measured instructions.

| Metric | 64K | LogG=9 | LogG=8 |
|---|---:|---:|---:|
| Geometric-mean MPKI-ratio reduction (Metric A) | 12.92% | 21.37% | 32.34% |
| Median per-workload reduction (Metric A, descriptive) | 11.92% | 20.63% | 27.20% |
| Pooled reduction (Metric A) | 13.41% | 19.98% | 27.82% |
| Geometric-mean MPKI-ratio reduction (Metric B) | 12.92% | 7.22% | 1.09% |
| Median per-workload reduction (Metric B, descriptive) | 11.92% | 4.54% | -0.53% |
| Pooled reduction (Metric B) | 13.41% | 8.22% | 2.85% |

## Absolute MPKI means

Arithmetic mean workload MPKI, computed from raw instruction and misprediction counts.

| Capacity | Standalone TAGE-SC-L | LLBP-X |
|---|---:|---:|
| Full size, LogG=10 | 2.916 | 2.525 |
| LogG=9 | 3.345 | 2.677 |
| LogG=8 | 3.925 | 2.833 |

## Workload wins against the reference

| Reference | LogG=9 | LogG=8 |
|---|---:|---:|
| Same-capacity TAGE (Metric A) | 14/14 | 14/14 |
| Full-size 64K TAGE (Metric B) | 13/14 | 6/14 |

## Definitions and limits

- Metric A compares LLBP-X with standalone TAGE at the same capacity.
- Metric B compares reduced-capacity LLBP-X with full-size 64K standalone TAGE.
- At 64K, Metrics A and B coincide.
- Results use the accuracy-only zero-latency configuration.
- These results do not establish timing, energy, IPC, or physical-area benefits.
