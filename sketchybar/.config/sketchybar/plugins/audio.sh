#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

if [[ "${SENDER:-}" == mouse.exited.global ]]; then
  sketchybar --set audio popup.drawing=off
  exit 0
fi

if ! command -v SwitchAudioSource >/dev/null 2>&1; then
  sketchybar --set audio label=Unavailable icon.color="$MUTED" popup.drawing=off
  exit 0
fi

if [[ "${1:-}" == --select && -n "${2:-}" ]]; then
  SwitchAudioSource -t output -u "$2" >/dev/null
  sketchybar --set audio popup.drawing=off
fi

if ! current=$(SwitchAudioSource -c -t output -f json 2>/dev/null); then
  sketchybar --set audio label=Unavailable icon.color="$MUTED" popup.drawing=off
  exit 0
fi
label=$(printf '%s' "$current" | jq -r '.name')
current_uid=$(printf '%s' "$current" | jq -r '.uid')
sketchybar --set audio label="$label" icon.color="$GREEN"

if [[ "${1:-}" == --select || "${SENDER:-}" != mouse.clicked ]]; then
  exit 0
fi
if [[ $(sketchybar --query audio | jq -r '.popup.drawing') == on ]]; then
  sketchybar --set audio popup.drawing=off
  exit 0
fi

devices=$(SwitchAudioSource -a -t output -f json)
sketchybar --remove '/audio\.device\..*/' >/dev/null
index=0
while IFS= read -r device; do
  uid=$(printf '%s' "$device" | jq -r '.uid')
  name=$(printf '%s' "$device" | jq -r '.name')
  color="$TEXT"
  if [[ "$uid" == "$current_uid" ]]; then
    name="✓ $name"
    color="$GREEN"
  fi
  # Quote the UID as a shell argument; device names never become executable code.
  printf -v action '%q --select %q' "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/audio.sh" "$uid"
  sketchybar --add item "audio.device.$index" popup.audio \
    --set "audio.device.$index" icon.drawing=off label="$name" \
    label.color="$color" label.max_chars=50 padding_left=8 padding_right=8 \
    click_script="$action"
  index=$((index + 1))
done <<< "$devices"
sketchybar --set brew_updates popup.drawing=off --set audio popup.drawing=on
