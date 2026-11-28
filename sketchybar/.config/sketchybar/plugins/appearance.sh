#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

if [[ "${SENDER:-}" == mouse.clicked && "${BUTTON:-left}" == left ]]; then
  osascript -e 'tell application "System Events" to tell appearance preferences to set dark mode to not (dark mode)'
fi

mode=$(defaults read -g AppleInterfaceStyle 2>/dev/null || true)
if [[ "$mode" == Dark ]]; then
  icon=''
  label=Dark
else
  icon=''
  label=Light
fi

sketchybar --set appearance icon="$icon" icon.color="$TEXT" label="$label"
