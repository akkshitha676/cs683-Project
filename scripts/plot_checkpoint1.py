#!/usr/bin/env python3
"""Regenerate Checkpoint I result plots from committed CSV files."""

import argparse
import csv
import math
from pathlib import Path
from statistics import fmean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "checkpoint1"
FILES = {
    "LogG10": RESULTS / "results_64k.csv",
    "LogG9": RESULTS / "results_logg9.csv",
    "LogG8": RESULTS / "results_logg8.csv",
}
MODEL_PAIRS = {
    "LogG10": ("tage64kscl", "llbpx"),
    "LogG9": ("tage64kscl-reduced-tagged", "llbpx-reduced-tagged"),
    "LogG8": ("tage-logg8scl", "llbpx-logg8"),
}
LABELS = {
    "mwnginxfpm-wiki": "PHPWiki",
    "dacapo-kafka": "Kafka",
    "dacapo-tomcat": "Tomcat",
    "dacapo-spring": "Spring",
    "renaissance-finagle-chirper": "Chirper",
    "renaissance-finagle-http": "HTTP",
    "benchbase-tpcc": "TPC-C",
    "benchbase-twitter": "Twitter",
    "benchbase-wikipedia": "Wikipedia",
    "nodeapp-nodeapp": "NodeApp",
    "charlie.1006518": "Charlie",
    "delta.507252": "Delta",
    "merced.467915": "Merced",
    "whiskey.426708": "Whiskey",
}


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 28:
        raise ValueError(f"{path}: expected 28 rows, got {len(rows)}")
    return rows


def metric(row):
    instructions = int(row["roi_instructions"])
    mispredictions = int(row["roi_mispredictions"])
    if instructions <= 0 or mispredictions < 0:
        raise ValueError(f"Invalid counts in row: {row}")
    mpki = 1000.0 * mispredictions / instructions
    if abs(mpki - float(row["roi_mpki"])) > 0.00011:
        raise ValueError(f"Recorded MPKI does not match counts: {row}")
    return {
        "instructions": instructions,
        "mispredictions": mispredictions,
        "rate": mispredictions / instructions,
        "mpki": mpki,
    }


def ordered_traces(rows):
    found = {row["trace"] for row in rows}
    traces = [trace for trace in LABELS if trace in found]
    if len(traces) != 14 or len(found) != 14:
        raise ValueError(f"Expected 14 workloads, got {len(found)}")
    return traces


def load_results():
    loaded = {}
    reference_traces = None
    for capacity, path in FILES.items():
        rows = read_rows(path)
        traces = ordered_traces(rows)
        if capacity == "LogG10":
            data = {}
            for row in rows:
                key = (row["trace"], row["model"])
                if key in data:
                    raise ValueError(f"Duplicate row in {path}: {key}")
                data[key] = metric(row)
            baseline, llbpx = MODEL_PAIRS[capacity]
            if any((trace, model) not in data for trace in traces for model in (baseline, llbpx)):
                raise ValueError("The full-size CSV is missing a model or workload.")
        else:
            data = {}
            baseline, llbpx = MODEL_PAIRS[capacity]
            for row in rows:
                key = (row["trace"], row["role"])
                if key in data:
                    raise ValueError(f"Duplicate row in {path}: {key}")
                expected = baseline if row["role"] == "baseline" else llbpx
                if row["model"] != expected:
                    raise ValueError(f"Unexpected model in {path}: {row}")
                data[key] = metric(row)
            for trace in traces:
                if (trace, "baseline") not in data or (trace, "llbpx") not in data:
                    raise ValueError(f"Missing paired workload in {path}: {trace}")
                if data[(trace, "baseline")]["instructions"] != data[(trace, "llbpx")]["instructions"]:
                    raise ValueError(f"Instruction counts differ in {capacity}: {trace}")
        if reference_traces is not None and traces != reference_traces:
            raise ValueError(f"Workload set differs in {capacity}")
        reference_traces = traces
        loaded[capacity] = {"data": data, "traces": traces}
    for trace in reference_traces:
        n64 = loaded["LogG10"]["data"][(trace, "tage64kscl")]["instructions"]
        for capacity in ("LogG9", "LogG8"):
            for role in ("baseline", "llbpx"):
                if loaded[capacity]["data"][(trace, role)]["instructions"] != n64:
                    raise ValueError(f"Instruction count mismatch for {capacity}, {trace}")
    return loaded


def get_pair(loaded, capacity, trace):
    data = loaded[capacity]["data"]
    if capacity == "LogG10":
        baseline, llbpx = MODEL_PAIRS[capacity]
        return data[(trace, baseline)], data[(trace, llbpx)]
    return data[(trace, "baseline")], data[(trace, "llbpx")]


def geometric_reduction(reference_rates, test_rates):
    ratios = [test / ref for ref, test in zip(reference_rates, test_rates)]
    if any(value <= 0 for value in ratios):
        raise ValueError("Geometric reduction requires positive rates.")
    return 100.0 * (1.0 - math.exp(fmean(math.log(value) for value in ratios)))


def pooled_reduction(reference_rows, test_rows):
    reference_rate = sum(row["mispredictions"] for row in reference_rows) / sum(row["instructions"] for row in reference_rows)
    test_rate = sum(row["mispredictions"] for row in test_rows) / sum(row["instructions"] for row in test_rows)
    return 100.0 * (1.0 - test_rate / reference_rate)


def summarize(loaded):
    summary = {}
    for capacity, block in loaded.items():
        pairs = [get_pair(loaded, capacity, trace) for trace in block["traces"]]
        base = [pair[0] for pair in pairs]
        test = [pair[1] for pair in pairs]
        summary[capacity] = {
            "base_mpki": [row["mpki"] for row in base],
            "llbpx_mpki": [row["mpki"] for row in test],
            "mean_base_mpki": fmean(row["mpki"] for row in base),
            "mean_llbpx_mpki": fmean(row["mpki"] for row in test),
            "metric_a_geomean": geometric_reduction(
                [row["rate"] for row in base], [row["rate"] for row in test]
            ),
            "metric_a_pooled": pooled_reduction(base, test),
        }
    for capacity in ("LogG9", "LogG8"):
        traces = loaded[capacity]["traces"]
        reference = [loaded["LogG10"]["data"][(trace, "tage64kscl")] for trace in traces]
        test = [get_pair(loaded, capacity, trace)[1] for trace in traces]
        summary[capacity]["metric_b_geomean"] = geometric_reduction(
            [row["rate"] for row in reference], [row["rate"] for row in test]
        )
        summary[capacity]["metric_b_pooled"] = pooled_reduction(reference, test)
    summary["LogG10"]["metric_b_geomean"] = summary["LogG10"]["metric_a_geomean"]
    summary["LogG10"]["metric_b_pooled"] = summary["LogG10"]["metric_a_pooled"]
    return summary


def save_absolute_plot(loaded, output_dir):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
    titles = {
        "LogG10": "Full size (LogG=10)",
        "LogG9": "Reduced base (LogG=9)",
        "LogG8": "Reduced base (LogG=8)",
    }
    for ax, capacity in zip(axes, ("LogG10", "LogG9", "LogG8")):
        traces = loaded[capacity]["traces"]
        pairs = [get_pair(loaded, capacity, trace) for trace in traces]
        baseline = [pair[0]["mpki"] for pair in pairs]
        llbpx = [pair[1]["mpki"] for pair in pairs]
        positions = list(range(len(traces)))
        width = 0.38
        ax.bar([x - width / 2 for x in positions], baseline, width, label="Standalone TAGE-SC-L")
        ax.bar([x + width / 2 for x in positions], llbpx, width, label="LLBP-X")
        ax.set_title(titles[capacity])
        ax.set_xticks(positions)
        ax.set_xticklabels([LABELS[trace] for trace in traces], rotation=50, ha="right", fontsize=8)
        ax.set_ylabel("MPKI")
        ax.grid(axis="y", alpha=0.3)
        ax.set_axisbelow(True)
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle("Absolute branch prediction error by workload")
    fig.tight_layout()
    path = output_dir / "absolute_mpki_by_workload.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def save_reduction_plot(summary, output_dir):
    capacities = ("LogG10", "LogG9", "LogG8")
    labels = ("Full size", "LogG=9", "LogG=8")
    metrics = (
        ("Metric A, geometric mean", "metric_a_geomean"),
        ("Metric B, geometric mean", "metric_b_geomean"),
        ("Metric A, pooled", "metric_a_pooled"),
        ("Metric B, pooled", "metric_b_pooled"),
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    width = 0.19
    centers = list(range(len(capacities)))
    for i, (label, key) in enumerate(metrics):
        positions = [x + (i - 1.5) * width for x in centers]
        values = [summary[capacity][key] for capacity in capacities]
        bars = ax.bar(positions, values, width, label=label)
        ax.bar_label(bars, fmt="%.1f%%", padding=2, fontsize=8)
    ax.axhline(0, linewidth=0.8)
    ax.set_xticks(centers)
    ax.set_xticklabels(labels)
    ax.set_ylabel("MPKI reduction (%)")
    ax.set_title("LLBP-X accuracy reduction against two baselines")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    ax.set_axisbelow(True)
    fig.tight_layout()
    path = output_dir / "normalized_reductions.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def save_mean_csv(summary, output_dir):
    path = output_dir / "absolute_mpki_means.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("capacity", "standalone_tage_mean_mpki", "llbpx_mean_mpki"))
        for capacity in ("LogG10", "LogG9", "LogG8"):
            row = summary[capacity]
            writer.writerow((capacity, f"{row['mean_base_mpki']:.6f}", f"{row['mean_llbpx_mpki']:.6f}"))
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=RESULTS / "figures")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    loaded = load_results()
    summary = summarize(loaded)
    outputs = (
        save_absolute_plot(loaded, args.output_dir),
        save_reduction_plot(summary, args.output_dir),
        save_mean_csv(summary, args.output_dir),
    )
    for capacity in ("LogG10", "LogG9", "LogG8"):
        row = summary[capacity]
        print(
            f"{capacity}: mean MPKI TAGE={row['mean_base_mpki']:.3f}, "
            f"LLBP-X={row['mean_llbpx_mpki']:.3f}; "
            f"Metric A geomean={row['metric_a_geomean']:.2f}%, "
            f"Metric A pooled={row['metric_a_pooled']:.2f}%, "
            f"Metric B geomean={row['metric_b_geomean']:.2f}%, "
            f"Metric B pooled={row['metric_b_pooled']:.2f}%"
        )
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
