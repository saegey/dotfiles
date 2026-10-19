#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

power=$(pmset -g batt)
if [[ ! "$power" =~ ([0-9]+)% ]]; then
  sketchybar --set battery drawing=off
  exit 0
fi
percentage="${BASH_REMATCH[1]}"
color="$GREEN"
label="$percentage%"
if [[ "$power" == *"AC Power"* ]]; then
  label="$label+"
elif (( percentage <= 20 )); then
  color="$RED"
fi
sketchybar --set battery drawing=on icon.color="$color" label="$label"
