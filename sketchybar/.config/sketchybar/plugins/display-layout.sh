#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

# Dinky monitor numbers match SketchyBar's display arrangement IDs.
monitors=$(dinky list-monitors --format '%{monitor-id}|%{monitor-name}' 2>/dev/null) || exit 0
internal=()
external=()
while IFS='|' read -r id name; do
  [[ "$id" =~ ^[0-9]+$ ]] || continue
  case "$name" in
    *Built-in*|*built-in*|*Color\ LCD*) internal+=("$id") ;;
    *) external+=("$id") ;;
  esac
done <<< "$monitors"

# A zero display mask means all displays, so hide and stop updates when there
# are no eligible screens. Polling plugins must not re-show excluded items.
args=()
if (( ${#external[@]} )); then
  external_ids=$(IFS=,; printf '%s' "${external[*]}")
  for item in brand clock volume audio; do
    args+=(--set "$item" display="$external_ids" drawing=on updates=on)
  done
  args+=(--set media display="$external_ids" updates=on)
else
  for item in brand clock volume audio media; do
    args+=(--set "$item" drawing=off updates=off)
  done
fi

if (( ${#internal[@]} )); then
  internal_ids=$(IFS=,; printf '%s' "${internal[*]}")
  args+=(--set media.compact display="$internal_ids" updates=on)
else
  args+=(--set media.compact drawing=off updates=off)
fi

sketchybar "${args[@]}"
