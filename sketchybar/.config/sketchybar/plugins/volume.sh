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
icon=''
if [[ "$muted" == true ]]; then
  color="$MUTED"
  label=Muted
  icon='󰝟'
elif (( level == 0 )); then
  icon=''
elif (( level < 50 )); then
  icon=''
fi
sketchybar --set volume icon="$icon" icon.color="$color" label="$label"
