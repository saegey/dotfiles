#!/usr/bin/env bash

# Sync only deliberately shared Supacode global preferences. Repository roots,
# repository settings, and worktree state always remain in the local file.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
shared_settings="$repo_root/supacode/settings.shared.json"
local_settings="${SUPACODE_SETTINGS_PATH:-$HOME/.supacode/settings.json}"

usage() {
  printf 'Usage: %s apply|export\n' "${0##*/}" >&2
}

require_jq() {
  command -v jq >/dev/null || {
    printf 'jq is required to sync Supacode settings.\n' >&2
    exit 1
  }
}

refuse_symlink() {
  if [[ -L "$local_settings" ]]; then
    printf 'Refusing to modify symlinked settings: %s\n' "$local_settings" >&2
    exit 1
  fi
}

apply_settings() {
  refuse_symlink
  mkdir -p "$(dirname "$local_settings")"

  local temporary
  temporary=$(mktemp "${local_settings}.tmp.XXXXXX")
  trap 'rm -f "$temporary"' EXIT

  if [[ -e "$local_settings" ]]; then
    jq --slurpfile shared "$shared_settings" \
      '.global = $shared[0].global' "$local_settings" >"$temporary"
  else
    jq . "$shared_settings" >"$temporary"
  fi

  mv "$temporary" "$local_settings"
  trap - EXIT
}

export_settings() {
  [[ -f "$local_settings" ]] || {
    printf 'Supacode settings not found: %s\n' "$local_settings" >&2
    exit 1
  }

  local temporary
  temporary=$(mktemp "${shared_settings}.tmp.XXXXXX")
  trap 'rm -f "$temporary"' EXIT

  # The template's existing keys are the allowlist. New fields are never
  # exported automatically, so a future local setting cannot leak by default.
  jq --slurpfile shared "$shared_settings" '
    ($shared[0].global | keys) as $allowed
    | {global: (.global | with_entries(select(.key as $key | $allowed | index($key))))}
  ' "$local_settings" >"$temporary"

  mv "$temporary" "$shared_settings"
  trap - EXIT
}

require_jq
[[ -f "$shared_settings" ]] || {
  printf 'Shared settings template not found: %s\n' "$shared_settings" >&2
  exit 1
}

case "${1:-}" in
  apply) apply_settings ;;
  export) export_settings ;;
  *) usage; exit 2 ;;
esac
