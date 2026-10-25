#!/usr/bin/env python3
import csv
import math
import hashlib
from pathlib import Path
from statistics import mean, median

REPO = Path(__file__).resolve().parents[1]
E = REPO / "results" / "checkpoint1"
G64 = E / "results_64k.csv"
CAP = E

FILES = {
    "64K": G64,
    "LogG9": CAP / "results_logg9.csv",
    "LogG8": CAP / "results_logg8.csv",
}

EXPECTED = {
    "LogG9": ("tage64kscl-reduced-tagged", "llbpx-reduced-tagged"),
    "LogG8": ("tage-logg8scl", "llbpx-logg8"),
}

def load_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def idx_unique(rows, key_fn, label):
    out = {}
    for r in rows:
        k = key_fn(r)
        if k in out:
            raise ValueError(f"{label}: duplicate key {k}")
        out[k] = r
    return out

def counts(r):
    n = int(r["roi_instructions"])
    m = int(r["roi_mispredictions"])
    if n <= 0 or m < 0:
        raise ValueError(f"Invalid counts in row: {r}")
    mpki = 1000.0 * m / n
    if abs(mpki - float(r["roi_mpki"])) > 0.00011:
        raise ValueError(f"MPKI mismatch in row: {r}")
    return n, m, m / n, mpki

def pct_reduction(ref_rate, test_rate):
    return 100.0 * (1.0 - test_rate / ref_rate)

def pooled_reduction(ref_rows, test_rows):
    ref_n = sum(int(r["roi_instructions"]) for r in ref_rows)
    ref_m = sum(int(r["roi_mispredictions"]) for r in ref_rows)
    test_n = sum(int(r["roi_instructions"]) for r in test_rows)
    test_m = sum(int(r["roi_mispredictions"]) for r in test_rows)
    return pct_reduction(ref_m / ref_n, test_m / test_n)

def geometric_reduction(ref_rates, test_rates):
    ratios = [x / r for r, x in zip(ref_rates, test_rates)]
    return 100.0 * (1.0 - math.exp(mean(math.log(x) for x in ratios)))

def check_rows(label, rows, expected):
    if len(rows) != expected:
        raise ValueError(f"{label}: expected {expected} rows; got {len(rows)}")

raw = {name: load_csv(path) for name, path in FILES.items()}
check_rows("64K", raw["64K"], 28)
check_rows("LogG9", raw["LogG9"], 28)
check_rows("LogG8", raw["LogG8"], 28)

full = idx_unique(
    raw["64K"], lambda r: (r["trace"], r["model"]), "64K"
)
for trace in {r["trace"] for r in raw["64K"]}:
    for model in ("tage64kscl", "llbpx"):
        if (trace, model) not in full:
            raise ValueError(f"64K missing {trace}/{model}")

traces = sorted({r["trace"] for r in raw["64K"]})
if len(traces) != 14:
    raise ValueError(f"Expected 14 workloads, got {len(traces)}")

cap = {}
for name in ("LogG9", "LogG8"):
    rows = raw[name]
    pair = idx_unique(rows, lambda r: (r["trace"], r["role"]), name)
    base_model, llbpx_model = EXPECTED[name]
    for trace in traces:
        for role, model in (("baseline", base_model), ("llbpx", llbpx_model)):
            r = pair.get((trace, role))
            if r is None:
                raise ValueError(f"{name}: missing {trace}/{role}")
            if r["model"] != model:
                raise ValueError(
                    f"{name}: {trace}/{role} expected {model}, got {r['model']}"
                )
    cap[name] = pair

# Per-workload metrics are computed from raw misprediction/instruction counts.
detail = []
for trace in traces:
    r64_t = full[(trace, "tage64kscl")]
    r64_x = full[(trace, "llbpx")]
    n64, m64t, rate64t, mpki64t = counts(r64_t)
    _, m64x, rate64x, mpki64x = counts(r64_x)

    entry = {
        "trace": trace,
        "64K_TAGE_instructions": n64,
        "64K_TAGE_mispredictions": m64t,
        "64K_TAGE_MPKI": f"{mpki64t:.4f}",
        "64K_LLBPX_mispredictions": m64x,
        "64K_LLBPX_MPKI": f"{mpki64x:.4f}",
    }

    for name, prefix in (("LogG9", "logg9"), ("LogG8", "logg8")):
        base = cap[name][(trace, "baseline")]
        x = cap[name][(trace, "llbpx")]
        nb, mb, rb, mpkib = counts(base)
        nx, mx, rx, mpkix = counts(x)

        if nb != nx:
            raise ValueError(f"{name}/{trace}: paired instruction counts differ")
        if nb != n64:
            raise ValueError(f"{name}/{trace}: instruction window differs from 64K")

        A = pct_reduction(rb, rx)
        B = pct_reduction(rate64t, rx)

        entry.update({
            f"{prefix}_TAGE_mispredictions": mb,
            f"{prefix}_TAGE_MPKI": f"{mpkib:.4f}",
            f"{prefix}_LLBPX_mispredictions": mx,
            f"{prefix}_LLBPX_MPKI": f"{mpkix:.4f}",
            f"{prefix}_MetricA_pct": f"{A:.4f}",
            f"{prefix}_MetricB_pct": f"{B:.4f}",
        })
    detail.append(entry)

# Sanity invariants: reducing the base should not improve either model's
# error rate in any of these matched traces; LLBP-X should beat its own
# same-capacity standalone TAGE baseline.
for d in detail:
    trace = d["trace"]
    t64 = counts(full[(trace, "tage64kscl")])[2]
    x64 = counts(full[(trace, "llbpx")])[2]
    t9 = counts(cap["LogG9"][(trace, "baseline")])[2]
    x9 = counts(cap["LogG9"][(trace, "llbpx")])[2]
    t8 = counts(cap["LogG8"][(trace, "baseline")])[2]
    x8 = counts(cap["LogG8"][(trace, "llbpx")])[2]

    if not (t64 <= t9 <= t8):
        raise ValueError(f"Standalone TAGE capacity invariant failed: {trace}")
    if not (x64 <= x9 <= x8):
        raise ValueError(f"LLBP-X capacity invariant failed: {trace}")
    if not (x9 < t9 and x8 < t8):
        raise ValueError(f"Same-capacity LLBP-X improvement failed: {trace}")

DETAIL = CAP / "capacity_metrics_per_trace.csv"
with DETAIL.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(detail[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(detail)

def metrics(name, ref_model, x_model):
    if name == "64K":
        ref = [full[(t, ref_model)] for t in traces]
        test = [full[(t, x_model)] for t in traces]
    else:
        ref = [cap[name][(t, "baseline")] for t in traces]
        test = [cap[name][(t, "llbpx")] for t in traces]

    r_rates = [counts(r)[2] for r in ref]
    x_rates = [counts(r)[2] for r in test]
    per = [pct_reduction(r, x) for r, x in zip(r_rates, x_rates)]

    return {
        "arithmetic": mean(per),
        "geometric": geometric_reduction(r_rates, x_rates),
        "median": median(per),
        "pooled": pooled_reduction(ref, test),
        "wins": sum(p > 0 for p in per),
        "min": min(per),
        "max": max(per),
    }

summaries = {
    "64K": metrics("64K", "tage64kscl", "llbpx"),
    "LogG9": metrics("LogG9", "", ""),
    "LogG8": metrics("LogG8", "", ""),
}

summary_path = CAP / "capacity_gate_summary.md"
with summary_path.open("w") as f:
    f.write("# Reduced-Capacity Evaluation Summary\n\n")
    f.write("All metrics were recomputed from raw misprediction and instruction counts.\n\n")
    f.write("| Metric | 64K | LogG=9 | LogG=8 |\n")
    f.write("|---|---:|---:|---:|\n")
    for label, key, fmt in (
        ("Arithmetic mean per-workload reduction", "arithmetic", "{:.2f}%"),
        ("Geometric-mean ratio reduction", "geometric", "{:.2f}%"),
        ("Median per-workload reduction", "median", "{:.2f}%"),
        ("Pooled reduction (ratio of total error rates)", "pooled", "{:.2f}%"),
        ("Workloads improved vs chosen reference", "wins", "{}/14"),
        ("Minimum per-workload reduction", "min", "{:.2f}%"),
        ("Maximum per-workload reduction", "max", "{:.2f}%"),
    ):
        cells = []
        for name in ("64K", "LogG9", "LogG8"):
            value = summaries[name][key]
            cells.append(fmt.format(value))
        f.write(f"| {label} | " + " | ".join(cells) + " |\n")

    f.write("\n## Reference definitions\n\n")
    f.write("- 64K: LLBP-X versus full-size standalone TAGE-SC-L.\n")
    f.write("- LogG=9 and LogG=8: tables show same-capacity comparisons.\n")
    f.write("- For reduced capacities, Metric A is same-capacity TAGE vs LLBP-X; ")
    f.write("Metric B is full-size 64K TAGE vs reduced-capacity LLBP-X.\n")
    f.write("- Pooled reductions are computed from total mispredictions divided ")
    f.write("by total measured instructions, not from rounded MPKI.\n")

validation_path = CAP / "analysis_validation.txt"
with validation_path.open("w") as f:
    f.write("PASS: 28 rows at 64K, LogG=9, and LogG=8.\n")
    f.write("PASS: expected model names and one paired run per workload.\n")
    f.write("PASS: recorded MPKI matches 1000 * mispredictions / instructions.\n")
    f.write("PASS: paired instruction counts match across capacities.\n")
    f.write("PASS: standalone TAGE error rate is monotonic as capacity shrinks.\n")
    f.write("PASS: LLBP-X error rate is monotonic as capacity shrinks.\n")
    f.write("PASS: LLBP-X beats its same-capacity standalone baseline on all workloads.\n")

hash_path = CAP / "analysis_input_hashes.sha256"
with hash_path.open("w") as f:
    for p in [G64, FILES["LogG9"], FILES["LogG8"], Path(__file__)]:
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        f.write(f"{digest}  {p.resolve().relative_to(REPO)}\n")

print(validation_path.read_text(), end="")
print("\nSummary:")
for name, s in summaries.items():
    print(
        f"{name:5s}: mean={s['arithmetic']:.2f}%, "
        f"geometric={s['geometric']:.2f}%, pooled={s['pooled']:.2f}%, "
        f"median={s['median']:.2f}%, range={s['min']:.2f}% to {s['max']:.2f}%"
    )
print(f"\nPer-workload CSV: {DETAIL}")
print(f"Markdown summary: {summary_path}")
print(f"Input hashes: {hash_path}")
