# Checkpoint I : Capacity Evaluation Summary

Normalized comparisons use geometric means of per-workload MPKI ratios. Pooled reductions are computed separately from total error rates. Median values are descriptive summaries of workload variation.

| Metric | 64K | LogG=9 | LogG=8 |
|---|---:|---:|---:|
| Geometric-mean ratio reduction (Metric A) | 12.92% | 21.37% | 32.34% |
| Median per-workload reduction (Metric A, descriptive) | 11.92% | 20.63% | 27.20% |
| Pooled reduction (Metric A) | 13.41% | 19.98% | 27.82% |
| Geometric-mean ratio reduction (Metric B) | 12.92% | 7.22% | 1.09% |
| Median per-workload reduction (Metric B, descriptive) | 11.92% | 4.54% | -0.53% |
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

## Absolute MPKI means

Arithmetic mean workload MPKI, computed from the raw misprediction and instruction counts:

| Capacity | Standalone TAGE-SC-L | LLBP-X |
|---|---:|---:|
| Full size, LogG=10 | 2.916 | 2.525 |
| LogG=9 | 3.345 | 2.677 |
| LogG=8 | 3.925 | 2.833 |
