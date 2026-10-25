#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/results/checkpoint1"
RUN_DIR="$EVIDENCE/reruns/64k_gate"
CSV="$RUN_DIR/results.csv"

cd "$ROOT"
mkdir -p "$RUN_DIR/logs"

echo "Checking predictor binary..."
printf '%s  ./build/predictor\n' \
  'd7aff66067b66480127dd1921361a2147f29d4ee1fe429cefc14c236d7926621' \
  | sha256sum -c -

echo "Checking completed trace validation..."
grep -qx 'ALL 14 GZIP INTEGRITY CHECKS PASSED' \
  "$EVIDENCE/full_trace_gzip_validation.log"

PASS_COUNT=$(grep -c '^PASS:' \
  "$EVIDENCE/full_trace_gzip_validation.log")
if [[ "$PASS_COUNT" -ne 14 ]]; then
    echo "ERROR: Expected 14 gzip passes, got $PASS_COUNT"
    exit 1
fi

if [[ -e "$CSV" ]]; then
    echo "ERROR: $CSV already exists. Refusing to overwrite results."
    exit 1
fi

printf 'trace,model,roi_instructions,roi_mispredictions,roi_mpki\n' \
  > "$CSV"

completed=0
total=28

while read -r expected relpath; do
    [[ -n "${relpath:-}" ]] || continue
    name=$(basename "$relpath" .champsim.trace.gz)
    trace="$ROOT/$relpath"

    for model in tage64kscl llbpx; do
        log="$RUN_DIR/logs/${name}_${model}.log"

        echo "START [$((completed + 1))/$total] trace=$name model=$model"

        if "$ROOT/build/predictor" \
            --bpmodel "$model" \
            --input-file "$trace" \
            --simulate-btb \
            --inst-warm 100000000 \
            --inst-sim 200000000 \
            > "$log" 2>&1; then
            :
        else
            rc=$?
            echo "FAILED: trace=$name model=$model exit=$rc"
            echo "Inspect log: $log"
            exit "$rc"
        fi

        roi_inst=$(awk -F: \
          '/ROI INSTRUCTIONS/ {gsub(/[[:space:]]/,"",$2); v=$2} END{print v}' \
          "$log")
        roi_misp=$(awk -F: \
          '/ROI MISPREDICTIONS/ {gsub(/[[:space:]]/,"",$2); v=$2} END{print v}' \
          "$log")
        roi_mpki=$(awk -F: \
          '/ROI MPKI/ {gsub(/[[:space:]]/,"",$2); v=$2} END{print v}' \
          "$log")

        if [[ -z "$roi_inst" || -z "$roi_misp" || -z "$roi_mpki" ]]; then
            echo "ERROR: Could not extract final metrics from $log"
            exit 1
        fi

        printf '%s,%s,%s,%s,%s\n' \
          "$name" "$model" "$roi_inst" "$roi_misp" "$roi_mpki" \
          >> "$CSV"

        completed=$((completed + 1))
        echo "DONE [$completed/$total] trace=$name model=$model instructions=$roi_inst mispredictions=$roi_misp MPKI=$roi_mpki"
    done
done < "$EVIDENCE/required-traces.md5"

echo "64K GATE COMPLETE: $completed runs"
echo "Results CSV: $CSV"
