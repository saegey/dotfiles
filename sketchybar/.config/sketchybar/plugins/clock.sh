#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"
sketchybar --set clock label="$(date '+%a %d %b  %H:%M')"
