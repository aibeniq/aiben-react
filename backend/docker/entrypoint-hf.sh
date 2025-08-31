#!/usr/bin/env bash
set -euo pipefail

PRIMARY_DIR="${HF_HOME:-/app/.cache/huggingface}"
TRANSFORMERS_DIR="${TRANSFORMERS_CACHE:-/app/.cache/transformers}"
SENTENCE_DIR="${SENTENCE_TRANSFORMERS_HOME:-$PRIMARY_DIR}"
FALLBACK_DIR="${HF_FALLBACK:-/tmp/huggingface-cache}"

reassign_var() {
  local var_name=$1
  local new_value=$2
  # shellcheck disable=SC2140
  eval "export ${var_name}='${new_value}'"
  echo "[HF-CACHE] Using ${var_name}=${new_value}" >&2
}

ensure_writable() {
  local path=$1
  if [ ! -d "$path" ]; then
    mkdir -p "$path" 2>/dev/null || return 1
  fi
  touch "$path/.perm_check" 2>/dev/null || return 1
  rm -f "$path/.perm_check" 2>/dev/null || true
  return 0
}

# Try primary locations; if any fail, switch all to fallback for consistency
if ensure_writable "$PRIMARY_DIR" && ensure_writable "$TRANSFORMERS_DIR" && ensure_writable "$SENTENCE_DIR"; then
  echo "[HF-CACHE] Primary cache directories are writable." >&2
else
  echo "[HF-CACHE] Primary cache not writable. Falling back to $FALLBACK_DIR" >&2
  mkdir -p "$FALLBACK_DIR/huggingface" "$FALLBACK_DIR/transformers" || true
  chmod -R 0777 "$FALLBACK_DIR" || true
  reassign_var HF_HOME "$FALLBACK_DIR/huggingface"
  reassign_var TRANSFORMERS_CACHE "$FALLBACK_DIR/transformers"
  reassign_var SENTENCE_TRANSFORMERS_HOME "$FALLBACK_DIR/huggingface"
fi

# Final diagnostic output
for v in HF_HOME TRANSFORMERS_CACHE SENTENCE_TRANSFORMERS_HOME; do
  eval val=\"\${$v}\"
  echo "[HF-CACHE] $v=$val" >&2
  df -h "$val" 2>/dev/null | sed 's/^/[HF-CACHE] /' || true
  ls -ld "$val" 2>/dev/null | sed 's/^/[HF-CACHE] /' || true
 done

echo "[HF-CACHE] Launching application: $*" >&2
exec "$@"
