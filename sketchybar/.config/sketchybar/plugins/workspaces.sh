#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

if ! state=$(dinky list-workspaces --all \
  --format '%{workspace}|%{workspace-is-visible}|%{monitor-id}' 2>/dev/null); then
  sketchybar --set '/space\..*/' drawing=off
  exit 0
fi

occupied=$(dinky list-workspaces --all --empty no 2>/dev/null || true)
args=()
while IFS='|' read -r workspace visible monitor; do
  [[ "$workspace" =~ ^[1-9]$ && "$monitor" =~ ^[0-9]+$ ]] || continue
  color="$MUTED"
  background=0x00000000
  case $'\n'"$occupied"$'\n' in
    *$'\n'"$workspace"$'\n'*) color="$TEXT" ;;
  esac
  if [[ "$visible" == true ]]; then
    color="$BASE"
    background="$MAUVE"
  fi
  args+=(--set "space.$workspace" drawing=on display="$monitor"
    label.color="$color" background.color="$background")
done <<< "$state"

if (( ${#args[@]} )); then sketchybar "${args[@]}"; fi
