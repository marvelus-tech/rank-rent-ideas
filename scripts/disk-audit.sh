#!/bin/bash
# Disk Audit — OpenClaw storage hygiene (read-only)
# Spec: scripts/disk-audit.spec.md
# Run: bash scripts/disk-audit.sh [--json-only] [--quiet]

set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
WORKSPACE="${WORKSPACE:-$OPENCLAW_HOME/workspace}"
SESSIONS_DIR="${SESSIONS_DIR:-$OPENCLAW_HOME/agents/main/sessions}"
TMP_DIR="${TMP_DIR:-$OPENCLAW_HOME/tmp}"
REPORT_JSON="${REPORT_JSON:-$WORKSPACE/disk-audit-report.json}"

JSON_ONLY=false
QUIET=false
for arg in "$@"; do
  case "$arg" in
    --json-only) JSON_ONLY=true ;;
    --quiet) QUIET=true ;;
  esac
done

NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

PASS=0
FAIL=0
WARN=0
CRITICAL_FAIL=0
DETAILS=""
DETAIL_JSON=""

# --- helpers ---
dir_size_bytes() {
  local path="$1"
  if [ ! -e "$path" ]; then
    echo 0
    return
  fi
  local kb
  kb=$(du -sk "$path" 2>/dev/null | awk '{print $1}')
  echo $((kb * 1024))
}

human_bytes() {
  local bytes="$1"
  if [ "$bytes" -ge 1073741824 ]; then
    awk -v b="$bytes" 'BEGIN { printf "%.1fG", b/1073741824 }'
  elif [ "$bytes" -ge 1048576 ]; then
    awk -v b="$bytes" 'BEGIN { printf "%.0fM", b/1048576 }'
  elif [ "$bytes" -ge 1024 ]; then
    awk -v b="$bytes" 'BEGIN { printf "%.0fK", b/1024 }'
  else
    echo "${bytes}B"
  fi
}

count_workspace_root_entries() {
  local count=0
  local entry
  shopt -s nullglob
  for entry in "$WORKSPACE"/*; do
    [ -e "$entry" ] || continue
    count=$((count + 1))
  done
  shopt -u nullglob
  echo "$count"
}

count_venvs() {
  find "$OPENCLAW_HOME" \( \
    -type d -name venv -o \
    -type d -name .venv -o \
    -type d -name '.venv-*' \
  \) 2>/dev/null | wc -l | tr -d ' '
}

count_node_modules() {
  find "$OPENCLAW_HOME" -type d -name node_modules 2>/dev/null | wc -l | tr -d ' '
}

count_nested_git() {
  find "$WORKSPACE" -type d -name .git 2>/dev/null | wc -l | tr -d ' '
}

count_large_files_outside_archive() {
  find "$OPENCLAW_HOME" -type f -size +50M 2>/dev/null \
    ! -path '*/archive/*' \
    ! -path '*/.snapshots/*' \
    ! -path '*/node_modules/*' \
    ! -path '*/venv/*' \
    ! -path '*/.venv/*' \
    ! -path '*/.venv-*/*' \
    | wc -l | tr -d ' '
}

list_large_files_json() {
  local lines=()
  local line
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    lines+=("$line")
  done < <(
    find "$OPENCLAW_HOME" -type f -size +50M 2>/dev/null \
      ! -path '*/archive/*' \
      ! -path '*/.snapshots/*' \
      ! -path '*/node_modules/*' \
      ! -path '*/venv/*' \
      ! -path '*/.venv/*' \
      ! -path '*/.venv-*/*' \
      -exec stat -f '%z %N' {} \; 2>/dev/null \
      | sort -rn \
      | head -5 \
      | awk '{
          path = substr($0, index($0,$2))
          gsub(/"/, "\\\"", path)
          printf "    {\"path\": \"%s\", \"bytes\": %s}", path, $1
        }'
  )

  local i
  for i in "${!lines[@]}"; do
    printf '%s' "${lines[$i]}"
    if [ "$i" -lt $((${#lines[@]} - 1)) ]; then
      printf ',\n'
    else
      printf '\n'
    fi
  done
}

check() {
  local name="$1" status="$2" detail="$3" critical="${4:-false}"
  local escaped_detail
  escaped_detail=$(printf '%s' "$detail" | sed 's/"/\\"/g')

  if [ "$status" = "PASS" ]; then
    PASS=$((PASS + 1))
    DETAILS="${DETAILS}\n  ✅ ${name}: ${detail}"
  elif [ "$status" = "WARN" ]; then
    WARN=$((WARN + 1))
    DETAILS="${DETAILS}\n  ⚠️  ${name}: ${detail}"
  else
    FAIL=$((FAIL + 1))
    DETAILS="${DETAILS}\n  ❌ ${name}: ${detail}"
    if [ "$critical" = "true" ]; then
      CRITICAL_FAIL=$((CRITICAL_FAIL + 1))
    fi
  fi

  DETAIL_JSON="${DETAIL_JSON}    {\"name\": \"${name}\", \"status\": \"${status}\", \"detail\": \"${escaped_detail}\"},"
}

threshold_check_bytes() {
  local name="$1" bytes="$2" pass_max="$3" warn_max="$4" critical="${5:-false}"
  local detail
  detail="$(human_bytes "$bytes")"

  if [ "$bytes" -le "$pass_max" ]; then
    check "$name" "PASS" "$detail"
  elif [ "$bytes" -le "$warn_max" ]; then
    check "$name" "WARN" "$detail"
  else
    check "$name" "FAIL" "$detail" "$critical"
  fi
}

threshold_check_count() {
  local name="$1" count="$2" pass_max="$3" warn_max="$4" critical="${5:-false}"
  if [ "$count" -le "$pass_max" ]; then
    check "$name" "PASS" "$count"
  elif [ "$count" -le "$warn_max" ]; then
    check "$name" "WARN" "$count"
  else
    check "$name" "FAIL" "$count" "$critical"
  fi
}

# --- checks ---
TOTAL_BYTES=$(dir_size_bytes "$OPENCLAW_HOME")
threshold_check_bytes "Total OpenClaw size" "$TOTAL_BYTES" $((2 * 1024 * 1024 * 1024)) $((4 * 1024 * 1024 * 1024)) true

ROOT_ENTRIES=$(count_workspace_root_entries)
threshold_check_count "Workspace root entries" "$ROOT_ENTRIES" 25 40

NODE_MODULES_COUNT=$(count_node_modules)
threshold_check_count "node_modules directories" "$NODE_MODULES_COUNT" 3 8

VENV_COUNT=$(count_venvs)
threshold_check_count "Python virtualenvs" "$VENV_COUNT" 2 4

if [ -d "$SESSIONS_DIR" ]; then
  SESSIONS_BYTES=$(dir_size_bytes "$SESSIONS_DIR")
  SESSION_FILE_COUNT=$(find "$SESSIONS_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
  TRAJECTORY_COUNT=$(find "$SESSIONS_DIR" -name '*.trajectory.jsonl' 2>/dev/null | wc -l | tr -d ' ')
  SESSION_DETAIL="$(human_bytes "$SESSIONS_BYTES"), ${SESSION_FILE_COUNT} files, ${TRAJECTORY_COUNT} trajectories"

  if [ "$SESSIONS_BYTES" -le $((200 * 1024 * 1024)) ]; then
    check "Agent sessions size" "PASS" "$SESSION_DETAIL"
  elif [ "$SESSIONS_BYTES" -le $((400 * 1024 * 1024)) ]; then
    check "Agent sessions size" "WARN" "$SESSION_DETAIL"
  else
    check "Agent sessions size" "FAIL" "$SESSION_DETAIL" true
  fi
else
  SESSIONS_BYTES=0
  check "Agent sessions size" "PASS" "sessions dir missing (skipped)"
fi

if [ -d "$TMP_DIR" ]; then
  TMP_BYTES=$(dir_size_bytes "$TMP_DIR")
  TMP_FILE_COUNT=$(find "$TMP_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
  TMP_DETAIL="$(human_bytes "$TMP_BYTES"), ${TMP_FILE_COUNT} files"

  if [ "$TMP_BYTES" -le $((100 * 1024 * 1024)) ]; then
    check "Temp directory size" "PASS" "$TMP_DETAIL"
  elif [ "$TMP_BYTES" -le $((300 * 1024 * 1024)) ]; then
    check "Temp directory size" "WARN" "$TMP_DETAIL"
  else
    check "Temp directory size" "FAIL" "$TMP_DETAIL"
  fi
else
  TMP_BYTES=0
  check "Temp directory size" "PASS" "tmp dir missing (skipped)"
fi

NESTED_GIT=$(count_nested_git)
threshold_check_count "Nested git repos in workspace" "$NESTED_GIT" 1 3

LARGE_FILE_COUNT=$(count_large_files_outside_archive)
if [ "$LARGE_FILE_COUNT" -eq 0 ]; then
  check "Large files (>50M) outside archive" "PASS" "0"
elif [ "$LARGE_FILE_COUNT" -le 3 ]; then
  check "Large files (>50M) outside archive" "WARN" "$LARGE_FILE_COUNT files"
else
  check "Large files (>50M) outside archive" "FAIL" "$LARGE_FILE_COUNT files"
fi

# --- scoring ---
TOTAL_CHECKS=$((PASS + FAIL + WARN))
if [ "$TOTAL_CHECKS" -eq 0 ]; then
  RAW_SCORE=0
else
  RAW_SCORE=$((PASS * 100 / TOTAL_CHECKS))
fi

if [ "$CRITICAL_FAIL" -gt 0 ]; then
  INTEGRITY="FAILING"
  MULTIPLIER="0.33"
  FINAL_SCORE=$(echo "$RAW_SCORE * 0.33" | bc -l | cut -d. -f1)
elif [ "$WARN" -gt 2 ]; then
  INTEGRITY="WARNING"
  MULTIPLIER="0.67"
  FINAL_SCORE=$(echo "$RAW_SCORE * 0.67" | bc -l | cut -d. -f1)
else
  INTEGRITY="HEALTHY"
  MULTIPLIER="1.0"
  FINAL_SCORE=$RAW_SCORE
fi

if [ "$FINAL_SCORE" -ge 90 ]; then GRADE="A"
elif [ "$FINAL_SCORE" -ge 80 ]; then GRADE="B"
elif [ "$FINAL_SCORE" -ge 70 ]; then GRADE="C"
elif [ "$FINAL_SCORE" -ge 60 ]; then GRADE="D"
else GRADE="F"
fi

LARGE_FILES_JSON=$(list_large_files_json)
DETAIL_JSON="${DETAIL_JSON%,}"

mkdir -p "$(dirname "$REPORT_JSON")"

cat > "$REPORT_JSON" <<EOF
{
  "timestamp": "$NOW",
  "grade": "$GRADE",
  "score": $FINAL_SCORE,
  "rawScore": $RAW_SCORE,
  "integrity": "$INTEGRITY",
  "multiplier": $MULTIPLIER,
  "openclawHomeBytes": $TOTAL_BYTES,
  "checks": {
    "pass": $PASS,
    "warn": $WARN,
    "fail": $FAIL,
    "criticalFail": $CRITICAL_FAIL
  },
  "metrics": {
    "totalBytes": $TOTAL_BYTES,
    "workspaceRootEntries": $ROOT_ENTRIES,
    "nodeModulesCount": $NODE_MODULES_COUNT,
    "venvCount": $VENV_COUNT,
    "sessionsBytes": ${SESSIONS_BYTES:-0},
    "tmpBytes": ${TMP_BYTES:-0},
    "nestedGitCount": $NESTED_GIT,
    "largeFilesOutsideArchive": $LARGE_FILE_COUNT
  },
  "largeFiles": [
$(printf '%s\n' "$LARGE_FILES_JSON")
  ],
  "details": [
${DETAIL_JSON}
  ]
}
EOF

if [ "$JSON_ONLY" = true ]; then
  cat "$REPORT_JSON"
elif [ "$QUIET" = false ]; then
  echo "💾 *Disk Audit Report*

📊 *Grade:* \`$GRADE\` ($FINAL_SCORE/100)
• Raw Score: $RAW_SCORE
• Integrity: $INTEGRITY

📈 *Checks*
• ✅ Pass: $PASS
• ⚠️ Warn: $WARN
• ❌ Fail: $FAIL
• 🚨 Critical: $CRITICAL_FAIL

📁 *Details*
$(echo -e "$DETAILS" | sed 's/^/• /')"
fi

if [ "$FAIL" -gt 0 ]; then
  exit 2
elif [ "$WARN" -gt 0 ]; then
  exit 1
fi
exit 0
