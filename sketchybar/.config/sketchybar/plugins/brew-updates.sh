#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

if [[ "${SENDER:-}" == mouse.exited.global ]]; then
  sketchybar --set brew_updates popup.drawing=off
  exit 0
fi
if [[ "${SENDER:-}" == mouse.clicked ]] &&
   [[ $(sketchybar --query brew_updates | jq -r '.popup.drawing') == on ]]; then
  sketchybar --set brew_updates popup.drawing=off
  exit 0
fi

# Use Homebrew's existing package index. Never run upgrades from a bar refresh.
# A fresh session avoids Ruby child-status failures in SketchyBar's process
# context on recent macOS (FelixKratz/SketchyBar#807).
if ! outdated=$(HOMEBREW_NO_AUTO_UPDATE=1 /usr/bin/perl -e '
  use POSIX ();
  $SIG{CHLD} = "DEFAULT";
  POSIX::setsid();
  exec @ARGV or die "Cannot start Homebrew: $!";
' -- brew outdated --json=v2 2>/dev/null); then
  sketchybar --set brew_updates label='?' icon.color="$RED" popup.drawing=off
  exit 0
fi
count=$(printf '%s' "$outdated" | jq '[.formulae[]?, .casks[]?] | length')
color="$GREEN"
if (( count > 0 )); then
  color="$MAUVE"
fi
sketchybar --set brew_updates label="$count" icon.color="$color"

if [[ "${SENDER:-}" != mouse.clicked ]]; then
  exit 0
fi

sketchybar --remove '/brew_updates\.package\..*/' >/dev/null
if (( count == 0 )); then
  sketchybar --add item brew_updates.package.0 popup.brew_updates \
    --set brew_updates.package.0 icon.drawing=off label='All packages up to date' \
    padding_left=8 padding_right=8
else
  index=0
  while IFS= read -r package; do
    sketchybar --add item "brew_updates.package.$index" popup.brew_updates \
      --set "brew_updates.package.$index" icon.drawing=off label="$package" \
      label.max_chars=60 padding_left=8 padding_right=8
    index=$((index + 1))
  done < <(printf '%s' "$outdated" | jq -r '
    [.formulae[]?, .casks[]?] | sort_by(.name)[] | "\(.name) → \(.current_version)"
  ')
fi
sketchybar --set audio popup.drawing=off --set brew_updates popup.drawing=on
