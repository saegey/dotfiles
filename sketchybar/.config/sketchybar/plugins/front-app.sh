#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

if [[ "${SENDER:-}" == front_app_switched ]]; then
  app="${INFO:-}"
else
  app=$(dinky list-windows --focused --format '%{app-name}' 2>/dev/null || true)
fi
# Focus can briefly be empty during a Space change. Keep the last valid app.
[[ -n "$app" ]] || exit 0
sketchybar --set front_app label="$app"
