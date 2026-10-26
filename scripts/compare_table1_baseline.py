#!/usr/bin/env python3
"""Compare recorded full-size TAGE MPKIs with the published Table I values."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "checkpoint1" / "results_64k.csv"
OUTPUT = ROOT / "results" / "checkpoint1" / "table1_baseline_comparison.csv"

# Transcribed from Table I, "Workloads with branch MPKI for 64K TSL",
# in Schall, Durackova, and Grot, The Last-Level Branch Predictor Revisited.
TABLE_I = {
    "mwnginxfpm-wiki": ("PHPWiki", 3.08),
    "dacapo-kafka": ("Kafka", 0.26),
    "dacapo-tomcat": ("Tomcat", 3.40),
    "dacapo-spring": ("Spring", 3.58),
    "renaissance-finagle-chirper": ("Finagle-chirper", 0.48),
    "renaissance-finagle-http": ("Finagle-HTTP", 2.81),
    "benchbase-tpcc": ("TPCC", 3.74),
    "benchbase-twitter": ("Twitter", 3.03),
    "benchbase-wikipedia": ("Wikipedia", 2.52),
    "nodeapp-nodeapp": ("NodeApp", 4.43),
    "charlie.1006518": ("Charlie", 2.89),
    "delta.507252": ("Delta", 1.09),
    "merced.467915": ("Merced", 4.13),
    "whiskey.426708": ("Whiskey", 5.38),
}


def main() -> None:
    with SOURCE.open(newline="") as handle:
        records = list(csv.DictReader(handle))

    baselines = {
        row["trace"]: row
        for row in records
        if row["model"] == "tage64kscl"
    }
    if set(baselines) != set(TABLE_I):
        missing = sorted(set(TABLE_I) - set(baselines))
        extra = sorted(set(baselines) - set(TABLE_I))
        raise SystemExit(f"Trace set mismatch. Missing={missing}; extra={extra}")

    output = []
    for trace, (label, paper_mpki) in TABLE_I.items():
        row = baselines[trace]
        instructions = int(row["roi_instructions"])
        mispredictions = int(row["roi_mispredictions"])
        calculated = 1000.0 * mispredictions / instructions
        rounded = f"{calculated:.2f}"
        paper_rounded = f"{paper_mpki:.2f}"
        output.append({
            "trace": trace,
            "workload": label,
            "table_i_mpki": paper_rounded,
            "roi_instructions": instructions,
            "roi_mispredictions": mispredictions,
            "recomputed_mpki": f"{calculated:.4f}",
            "recomputed_mpki_2dp": rounded,
            "match_to_2dp": "YES" if rounded == paper_rounded else "NO",
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    mismatches = [row for row in output if row["match_to_2dp"] != "YES"]
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(output)} workloads.")
    print(f"Table I matches to two decimal places: {len(output) - len(mismatches)}/{len(output)}.")
    if mismatches:
        for row in mismatches:
            print(
                f"MISMATCH {row['workload']}: Table I={row['table_i_mpki']}, "
                f"recomputed={row['recomputed_mpki_2dp']}"
            )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
