#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

if [[ "${SENDER:-}" == mouse.exited.global ]]; then
  sketchybar --set stacks popup.drawing=off
  exit 0
fi

if [[ ! -x "$HOME/.local/bin/dev-stack-status" ]]; then
  sketchybar --set stacks label='?' icon.color="$MUTED"
  exit 0
fi
state=$("$HOME/.local/bin/dev-stack-status" --json)
count=$(printf '%s' "$state" | jq -r '.running_stacks // "?"')
color="$GREEN"
if [[ "$count" == '?' || "$count" == 0 ]]; then
  color="$MUTED"
elif printf '%s' "$state" | jq -e 'any(.projects[]; .unhealthy > 0)' >/dev/null; then
  color="$RED"
fi
sketchybar --set stacks label="$count" icon.color="$color"

if [[ "${SENDER:-}" == mouse.clicked ]]; then
  if [[ $(sketchybar --query stacks | jq -r '.popup.drawing') == on ]]; then
    sketchybar --set stacks popup.drawing=off
    exit 0
  fi
  sketchybar --remove '/stacks\.project\..*/'
  index=0
  while IFS='|' read -r name running total unhealthy; do
    [[ -n "$name" ]] || continue
    label="$name  $running/$total"
    [[ "$unhealthy" != 0 ]] && label="$label !"
    sketchybar --add item "stacks.project.$index" popup.stacks \
      --set "stacks.project.$index" label="$label" label.color="$TEXT" icon.drawing=off
    index=$((index + 1))
  done < <(printf '%s' "$state" | jq -r '.projects[] | [.name, .running, .total, .unhealthy] | join("|")')
  if (( index == 0 )); then
    label=$(printf '%s' "$state" | jq -r '.error // "No dev stacks"')
    sketchybar --add item stacks.project.empty popup.stacks \
      --set stacks.project.empty label="$label" label.color="$MUTED" icon.drawing=off
  fi
  sketchybar --set stacks popup.drawing=on
fi
