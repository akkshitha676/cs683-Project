#!/usr/bin/env python3
import csv
import math
from pathlib import Path
from statistics import mean, median

REPO = Path(__file__).resolve().parents[1]
E = REPO / "results" / "checkpoint1"
CAP = E

def read(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def rate(r):
    n = int(r["roi_instructions"])
    m = int(r["roi_mispredictions"])
    recorded = float(r["roi_mpki"])
    calculated = 1000 * m / n
    if abs(calculated - recorded) > 0.00011:
        raise ValueError(f"MPKI mismatch: {r}")
    return m / n

def unique(rows, key, label):
    out = {}
    for r in rows:
        k = key(r)
        if k in out:
            raise ValueError(f"{label}: duplicate key {k}")
        out[k] = r
    return out

def pooled(ref, test):
    rn = sum(int(r["roi_instructions"]) for r in ref)
    rm = sum(int(r["roi_mispredictions"]) for r in ref)
    xn = sum(int(r["roi_instructions"]) for r in test)
    xm = sum(int(r["roi_mispredictions"]) for r in test)
    return 100 * (1 - (xm / xn) / (rm / rn))

def summary(ref_rows, test_rows):
    rr = [rate(r) for r in ref_rows]
    xr = [rate(r) for r in test_rows]
    per = [100 * (1 - x / r) for r, x in zip(rr, xr)]
    geometric = 100 * (
        1 - math.exp(mean(math.log(x / r) for r, x in zip(rr, xr)))
    )
    return {
        "median": median(per),
        "geometric": geometric,
        "pooled": pooled(ref_rows, test_rows),
        "wins": sum(x > 0 for x in per),
        "min": min(per),
        "max": max(per),
        "per": per,
    }

full_rows = read(E / "results_64k.csv")
if len(full_rows) != 28:
    raise ValueError(f"64K rows expected 28, got {len(full_rows)}")

full = unique(full_rows, lambda r: (r["trace"], r["model"]), "64K")
traces = sorted({r["trace"] for r in full_rows})
if len(traces) != 14:
    raise ValueError(f"Expected 14 workloads, got {len(traces)}")

full_t = [full[(t, "tage64kscl")] for t in traces]
full_x = [full[(t, "llbpx")] for t in traces]

capacity = {}
for name, models in {
    "LogG9": ("tage64kscl-reduced-tagged", "llbpx-reduced-tagged"),
    "LogG8": ("tage-logg8scl", "llbpx-logg8"),
}.items():
    rows = read(CAP / f"results_{name.lower()}.csv")
    if len(rows) != 28:
        raise ValueError(f"{name} rows expected 28, got {len(rows)}")
    ix = unique(rows, lambda r: (r["trace"], r["role"]), name)

    base, x = [], []
    for t in traces:
        b, p = ix[(t, "baseline")], ix[(t, "llbpx")]
        if b["model"] != models[0] or p["model"] != models[1]:
            raise ValueError(f"{name}: unexpected model for {t}")
        if b["roi_instructions"] != p["roi_instructions"]:
            raise ValueError(f"{name}: instruction count mismatch for {t}")
        if b["roi_instructions"] != full[(t, "tage64kscl")]["roi_instructions"]:
            raise ValueError(f"{name}: not matched to full-size window for {t}")
        base.append(b)
        x.append(p)

    capacity[name] = {"base": base, "x": x}

metrics = {
    "64K": summary(full_t, full_x),
    "LogG9_A": summary(capacity["LogG9"]["base"], capacity["LogG9"]["x"]),
    "LogG9_B": summary(full_t, capacity["LogG9"]["x"]),
    "LogG8_A": summary(capacity["LogG8"]["base"], capacity["LogG8"]["x"]),
    "LogG8_B": summary(full_t, capacity["LogG8"]["x"]),
}

for label, m in metrics.items():
    print(
        f"{label:8s} median={m['median']:.2f}% "
        f"geometric={m['geometric']:.2f}% pooled={m['pooled']:.2f}% "
        f"wins={m['wins']}/14"
    )

def mean_mpki(rows):
    return mean(
        1000 * int(row["roi_mispredictions"]) / int(row["roi_instructions"])
        for row in rows
    )

mean_mpkis = {
    "64K": (mean_mpki(full_t), mean_mpki(full_x)),
    "LogG9": (
        mean_mpki(capacity["LogG9"]["base"]),
        mean_mpki(capacity["LogG9"]["x"]),
    ),
    "LogG8": (
        mean_mpki(capacity["LogG8"]["base"]),
        mean_mpki(capacity["LogG8"]["x"]),
    ),
}

out = CAP / "capacity_gate_report_summary.md"
with out.open("w", encoding="utf-8") as f:
    f.write("# Checkpoint I: Capacity Evaluation Summary\n\n")
    f.write(
        "Normalized comparisons use geometric means of per-workload MPKI ratios. "
        "Pooled reductions use total mispredictions and total measured instructions.\n\n"
    )
    f.write("| Metric | 64K | LogG=9 | LogG=8 |\n|---|---:|---:|---:|\n")
    rows = [
        ("Geometric-mean MPKI-ratio reduction (Metric A)", "geometric"),
        ("Median per-workload reduction (Metric A, descriptive)", "median"),
        ("Pooled reduction (Metric A)", "pooled"),
        ("Geometric-mean MPKI-ratio reduction (Metric B)", "geometric"),
        ("Median per-workload reduction (Metric B, descriptive)", "median"),
        ("Pooled reduction (Metric B)", "pooled"),
    ]
    for index, (label, key) in enumerate(rows):
        if index < 3:
            vals = (metrics["64K"][key], metrics["LogG9_A"][key], metrics["LogG8_A"][key])
        else:
            vals = (metrics["64K"][key], metrics["LogG9_B"][key], metrics["LogG8_B"][key])
        f.write(f"| {label} | {vals[0]:.2f}% | {vals[1]:.2f}% | {vals[2]:.2f}% |\n")

    f.write("\n## Absolute MPKI means\n\n")
    f.write("Arithmetic mean workload MPKI, recomputed from raw instruction and misprediction counts.\n\n")
    f.write("| Capacity | Standalone TAGE-SC-L | LLBP-X |\n|---|---:|---:|\n")
    for name, label in (("64K", "Full size, LogG=10"), ("LogG9", "LogG=9"), ("LogG8", "LogG=8")):
        base, llbpx = mean_mpkis[name]
        f.write(f"| {label} | {base:.3f} | {llbpx:.3f} |\n")

    f.write("\n## Workload wins against the reference\n\n")
    f.write("| Reference | LogG=9 | LogG=8 |\n|---|---:|---:|\n")
    f.write(
        f"| Same-capacity TAGE (Metric A) | {metrics['LogG9_A']['wins']}/14 | "
        f"{metrics['LogG8_A']['wins']}/14 |\n"
    )
    f.write(
        f"| Full-size 64K TAGE (Metric B) | {metrics['LogG9_B']['wins']}/14 | "
        f"{metrics['LogG8_B']['wins']}/14 |\n"
    )

    f.write("\n## Definitions and limits\n\n")
    f.write("- Metric A compares LLBP-X with standalone TAGE at the same capacity.\n")
    f.write("- Metric B compares reduced-capacity LLBP-X with full-size 64K standalone TAGE.\n")
    f.write("- At 64K, Metrics A and B coincide.\n")
    f.write("- Results use the accuracy-only zero-latency configuration.\n")
    f.write("- These results do not establish timing, energy, IPC, or physical-area benefits.\n")

print(f"\nSaved report summary: {out}")
