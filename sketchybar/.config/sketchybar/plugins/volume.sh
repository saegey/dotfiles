#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

if [[ "${SENDER:-}" == mouse.clicked ]]; then
  osascript -e 'set volume output muted (not (output muted of (get volume settings)))'
fi

settings=$(osascript -e 'set s to get volume settings' \
  -e 'return ((output volume of s) as text) & "|" & ((output muted of s) as text)')
IFS='|' read -r level muted <<< "$settings"
color="$GREEN"
label="$level%"
if [[ "$muted" == true ]]; then
  color="$MUTED"
  label=Muted
fi
sketchybar --set volume icon.color="$color" label="$label"
