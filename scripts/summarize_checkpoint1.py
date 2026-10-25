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
        "mean": mean(per),
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
        f"{label:8s} mean={m['mean']:.2f}% "
        f"median={m['median']:.2f}% geometric={m['geometric']:.2f}% "
        f"pooled={m['pooled']:.2f}% wins={m['wins']}/14"
    )

out = CAP / "capacity_gate_report_summary.md"
with out.open("w") as f:
    f.write("# Checkpoint I — Capacity Evaluation Summary\n\n")
    f.write("All percentages are recomputed from raw instruction and misprediction counts.\n\n")
    f.write("| Metric | 64K | LogG=9 | LogG=8 |\n")
    f.write("|---|---:|---:|---:|\n")
    for label, key, fmt in [
        ("Arithmetic mean reduction (Metric A)", "mean", "{:.2f}%"),
        ("Median per-workload reduction (Metric A)", "median", "{:.2f}%"),
        ("Geometric-mean ratio reduction (Metric A)", "geometric", "{:.2f}%"),
        ("Pooled reduction (Metric A)", "pooled", "{:.2f}%"),
        ("Arithmetic mean reduction (Metric B)", "mean", "{:.2f}%"),
        ("Median per-workload reduction (Metric B)", "median", "{:.2f}%"),
        ("Geometric-mean ratio reduction (Metric B)", "geometric", "{:.2f}%"),
        ("Pooled reduction (Metric B)", "pooled", "{:.2f}%"),
    ]:
        # At 64K, A and B coincide.
        a = metrics["64K"][key]
        b = metrics["LogG9_A"][key] if "Metric A" in label else metrics["LogG9_B"][key]
        c = metrics["LogG8_A"][key] if "Metric A" in label else metrics["LogG8_B"][key]
        f.write(f"| {label} | {fmt.format(a)} | {fmt.format(b)} | {fmt.format(c)} |\n")

    f.write("\n## Workload wins against the reference\n\n")
    f.write("| Reference | LogG=9 | LogG=8 |\n|---|---:|---:|\n")
    f.write(f"| Same-capacity TAGE (Metric A) | {metrics['LogG9_A']['wins']}/14 | {metrics['LogG8_A']['wins']}/14 |\n")
    f.write(f"| Full-size 64K TAGE (Metric B) | {metrics['LogG9_B']['wins']}/14 | {metrics['LogG8_B']['wins']}/14 |\n")

    f.write("\n## Definitions\n\n")
    f.write("- Metric A compares LLBP-X with standalone TAGE at the same capacity.\n")
    f.write("- Metric B compares reduced-capacity LLBP-X with full-size 64K standalone TAGE.\n")
    f.write("- Pooled reduction is computed from the ratio of total error rates.\n")
    f.write("- At 64K, Metrics A and B coincide.\n")
    f.write("- These are accuracy-only, zero-latency results; they do not establish timing, energy, or IPC benefit.\n")

print(f"\nSaved report summary: {out}")
