#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE="$ROOT/results/checkpoint1"
RUN_DIR="$EVIDENCE/reruns/capacity_gate_logg9_logg8_2026-10-25"
CSV9="$RUN_DIR/results_logg9.csv"
CSV8="$RUN_DIR/results_logg8.csv"
PROV="$RUN_DIR/provenance.txt"
SCRIPT="$ROOT/scripts/run_capacity_gate_logg9_logg8_2026-10-25.sh"

mkdir -p "$RUN_DIR/logs"
exec 9>"$RUN_DIR/.lock"
if ! flock -n 9; then
    echo "ERROR: another capacity runner already holds the lock."
    exit 2
fi

cd "$ROOT"

EXPECTED_HEAD="5da415efc2ffd76d6944fcf2cb306742b882d961"
EXPECTED_BIN="d7aff66067b66480127dd1921361a2147f29d4ee1fe429cefc14c236d7926621"

if ! git merge-base --is-ancestor "$EXPECTED_HEAD" HEAD; then
    echo "ERROR: validated source commit is not an ancestor of HEAD."
    exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ERROR: tracked source changes detected; review before running."
    exit 1
fi

ACTUAL_BIN=$(sha256sum "$ROOT/build/predictor" | awk '{print $1}')
if [[ "$ACTUAL_BIN" != "$EXPECTED_BIN" ]]; then
    if [[ "${ALLOW_UNVERIFIED_BUILD:-0}" == "1" ]]; then
        echo "WARNING: binary differs from the archived checkpoint build."
        echo "This is a fresh-build rerun, not a byte-identical reproduction."
    else
        echo "ERROR: predictor binary checksum mismatch."
        echo "Set ALLOW_UNVERIFIED_BUILD=1 only for an explicitly labelled fresh-build rerun."
        exit 1
    fi
else
    echo "PASS: archived predictor binary checksum matches."
fi

grep -qx 'ALL 14 GZIP INTEGRITY CHECKS PASSED' \
    "$EVIDENCE/full_trace_gzip_validation.log"
PASS_COUNT=$(grep -c '^PASS:' \
    "$EVIDENCE/full_trace_gzip_validation.log")
[[ "$PASS_COUNT" -eq 14 ]]

for csv in "$CSV9" "$CSV8"; do
    if [[ ! -f "$csv" ]]; then
        echo 'trace,capacity,role,model,roi_instructions,roi_mispredictions,roi_mpki' > "$csv"
    elif [[ "$(head -n 1 "$csv")" != \
        'trace,capacity,role,model,roi_instructions,roi_mispredictions,roi_mpki' ]]; then
        echo "ERROR: unexpected CSV header in $csv"
        exit 1
    fi
done

{
    echo
    echo "========== RUN INVOCATION: $(date -Is) =========="
    echo "Source commit: $(git rev-parse HEAD)"
    echo "Tracked source changes: none"
    echo "Working-tree status (untracked files preserved):"
    git status --short
    echo
    sha256sum "$ROOT/build/predictor" "$SCRIPT" \
      "$EVIDENCE/required-traces.md5" \
      "$EVIDENCE/analysis_protocol_2026-10-24.md" \
      "$EVIDENCE/64k_gate/results.csv"
} >> "$PROV"

run_capacity() {
    local cap="$1"
    local baseline="$2"
    local llbpx="$3"
    local csv="$4"

    while read -r checksum relpath; do
        [[ -n "${relpath:-}" ]] || continue

        local name trace role model log roi_inst roi_misp roi_mpki
        name=$(basename "$relpath" .champsim.trace.gz)
        trace="$ROOT/$relpath"
        [[ -f "$trace" ]] || {
            echo "ERROR: missing trace $trace"
            exit 1
        }

        for role in baseline llbpx; do
            if [[ "$role" == "baseline" ]]; then
                model="$baseline"
            else
                model="$llbpx"
            fi

            # Skip a run only if its completed metrics row is already recorded.
            if awk -F, -v t="$name" -v r="$role" -v m="$model" \
                'NR>1 && $1==t && $3==r && $4==m {found=1}
                 END {exit !found}' "$csv"; then
                echo "SKIP capacity=$cap trace=$name role=$role model=$model"
                continue
            fi

            local done9 done8 next
            done9=$(awk 'END {print NR-1}' "$CSV9")
            done8=$(awk 'END {print NR-1}' "$CSV8")
            next=$((done9 + done8 + 1))

            log="$RUN_DIR/logs/${cap}_${name}_${role}_${model}.log"
            echo "START [$next/56] capacity=$cap trace=$name role=$role model=$model"

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
                echo "FAILED capacity=$cap trace=$name model=$model exit=$rc log=$log"
                exit "$rc"
            fi

            roi_inst=$(awk -F: \
              '/ROI INSTRUCTIONS/ {gsub(/[[:space:]]/,"",$2); v=$2}
               END {print v}' "$log")
            roi_misp=$(awk -F: \
              '/ROI MISPREDICTIONS/ {gsub(/[[:space:]]/,"",$2); v=$2}
               END {print v}' "$log")
            roi_mpki=$(awk -F: \
              '/ROI MPKI/ {gsub(/[[:space:]]/,"",$2); v=$2}
               END {print v}' "$log")

            if [[ ! "$roi_inst" =~ ^[0-9]+$ ||
                  ! "$roi_misp" =~ ^[0-9]+$ ||
                  ! "$roi_mpki" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
                echo "ERROR: could not extract final metrics from $log"
                exit 1
            fi

            if (( roi_inst < 199000000 )); then
                echo "ERROR: ROI instruction count unexpectedly low: $roi_inst"
                exit 1
            fi

            printf '%s,%s,%s,%s,%s,%s,%s\n' \
              "$name" "$cap" "$role" "$model" \
              "$roi_inst" "$roi_misp" "$roi_mpki" >> "$csv"

            echo "DONE [$next/56] capacity=$cap trace=$name role=$role instructions=$roi_inst mispredictions=$roi_misp MPKI=$roi_mpki"
        done
    done < "$EVIDENCE/required-traces.md5"
}

run_capacity logg9 \
    tage64kscl-reduced-tagged llbpx-reduced-tagged "$CSV9"

run_capacity logg8 \
    tage-logg8scl llbpx-logg8 "$CSV8"

echo "CAPACITY CAMPAIGN COMPLETE"
echo "LogG9 rows: $(($(awk 'END {print NR}' "$CSV9") - 1)) / 28"
echo "LogG8 rows: $(($(awk 'END {print NR}' "$CSV8") - 1)) / 28"
echo "Results directory: $RUN_DIR"
