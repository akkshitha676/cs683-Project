# Checkpoint I presentation materials

This directory versions the five-minute narration script and its presentation notes. The editable PowerPoint deck and PDF export are supplied separately as checkpoint submission files; they are not committed as binary assets in this repository revision.

The deck is aligned with the published result files in results/checkpoint1/: 14 workloads, 3 capacity points, and 84 accuracy-only simulator runs (100M warm-up and 200M measurement instructions per run, with BTB simulation enabled). The primary normalized statistic is the geometric-mean MPKI-ratio reduction; pooled reductions are reported separately.

The key results are 12.92% geometric-mean reduction at full size; 21.37% same-capacity and 7.22% full-size-reference reduction for LogG=9; and 32.34% same-capacity and 1.09% full-size-reference reduction for LogG=8. LogG=9 beats full-size TAGE on 13/14 workloads; LogG=8 does so on 6/14.

The experiment uses the accuracy-only configuration (simulateTiming=0, optW=0). Checkpoint II is framed as an exploratory timing-model study: accessDelay semantics must be checked before choosing values, and the model must not be treated as cycle-accurate CPU performance. The presentation makes no measured latency, IPC, energy, or physical-area claim.

The PHPWiki workload is listed in the result tables under the trace name mwnginxfpm-wiki. Keep the project README and result files synchronized with the script and any separate presentation export.

The spoken narration is about 580 words, or roughly 116 words per minute over five minutes, leaving room for pauses. Rehearse with a timer and shorten any sentence that feels rushed.
