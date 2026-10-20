#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

# Read only the running app's Dock badge, without Slack API credentials.
# Slack reports a number for notifications or a dot for other unread activity.
status=$(lsappinfo info -only StatusLabel Slack 2>/dev/null || true)
badge=$(printf '%s\n' "$status" | sed -n 's/.*"label"[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p')

case "$badge" in
  ''|0) sketchybar --set slack drawing=off label='' ;;
  # Draw unread dots as a circle so font glyph bounds cannot clip them.
  '•'|'·'|'●')
    sketchybar --set slack drawing=on label='' label.width=8 \
      label.background.drawing=on label.background.color="$MAUVE" \
      label.background.height=8 label.background.corner_radius=4
    ;;
  *)
    sketchybar --set slack drawing=on label="$badge" label.width=dynamic \
      label.background.drawing=off
    ;;
esac
