# Checkpoint I — Capacity Evaluation Summary

All percentages are recomputed from raw instruction and misprediction counts.

| Metric | 64K | LogG=9 | LogG=8 |
|---|---:|---:|---:|
| Arithmetic mean reduction (Metric A) | 12.60% | 20.60% | 29.62% |
| Median per-workload reduction (Metric A) | 11.92% | 20.63% | 27.20% |
| Geometric-mean ratio reduction (Metric A) | 12.92% | 21.37% | 32.34% |
| Pooled reduction (Metric A) | 13.41% | 19.98% | 27.82% |
| Arithmetic mean reduction (Metric B) | 12.60% | 6.99% | 0.81% |
| Median per-workload reduction (Metric B) | 11.92% | 4.54% | -0.53% |
| Geometric-mean ratio reduction (Metric B) | 12.92% | 7.22% | 1.09% |
| Pooled reduction (Metric B) | 13.41% | 8.22% | 2.85% |

## Workload wins against the reference

| Reference | LogG=9 | LogG=8 |
|---|---:|---:|
| Same-capacity TAGE (Metric A) | 14/14 | 14/14 |
| Full-size 64K TAGE (Metric B) | 13/14 | 6/14 |

## Definitions

- Metric A compares LLBP-X with standalone TAGE at the same capacity.
- Metric B compares reduced-capacity LLBP-X with full-size 64K standalone TAGE.
- Pooled reduction is computed from the ratio of total error rates.
- At 64K, Metrics A and B coincide.
- These are accuracy-only, zero-latency results; they do not establish timing, energy, or IPC benefit.
