#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

if ! command -v media-control >/dev/null 2>&1; then
  sketchybar --set media drawing=off
  exit 0
fi

if [[ "${SENDER:-}" == mouse.clicked ]]; then
  media-control toggle-play-pause >/dev/null 2>&1 || true
fi

# System Now Playing follows the current media app, including supported browsers.
if ! metadata=$(media-control get --no-artwork 2>/dev/null); then
  sketchybar --set media drawing=off
  exit 0
fi

if ! label=$(printf '%s' "$metadata" | jq -er '
  select(type == "object" and (.title? | type == "string"))
  | select(.title | length > 0)
  | [.title, (.artist // "")]
  | map(select(type == "string" and length > 0))
  | join(" — ")
  | gsub("[\r\n\t]"; " ")
'); then
  sketchybar --set media drawing=off
  exit 0
fi

icon="Ⅱ"
color="$MUTED"
if [[ $(printf '%s' "$metadata" | jq -r '.playing == true') == true ]]; then
  icon="▶"
  color="$GREEN"
fi

sketchybar --set media drawing=on icon="$icon" icon.color="$color" label="$label"
