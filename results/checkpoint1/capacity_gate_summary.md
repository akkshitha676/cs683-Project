# Reduced-Capacity Evaluation Summary

All metrics were recomputed from raw misprediction and instruction counts.

| Metric | 64K | LogG=9 | LogG=8 |
|---|---:|---:|---:|
| Arithmetic mean per-workload reduction | 12.60% | 20.60% | 29.62% |
| Geometric-mean ratio reduction | 12.92% | 21.37% | 32.34% |
| Median per-workload reduction | 11.92% | 20.63% | 27.20% |
| Pooled reduction (ratio of total error rates) | 13.41% | 19.98% | 27.82% |
| Workloads improved vs chosen reference | 14/14 | 14/14 | 14/14 |
| Minimum per-workload reduction | 2.00% | 7.10% | 10.79% |
| Maximum per-workload reduction | 28.47% | 42.03% | 73.00% |

## Reference definitions

- 64K: LLBP-X versus full-size standalone TAGE-SC-L.
- LogG=9 and LogG=8: tables show same-capacity comparisons.
- For reduced capacities, Metric A is same-capacity TAGE vs LLBP-X; Metric B is full-size 64K TAGE vs reduced-capacity LLBP-X.
- Pooled reductions are computed from total mispredictions divided by total measured instructions, not from rounded MPKI.
