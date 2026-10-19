#!/bin/bash

set -euo pipefail

if [[ $(uname -s) != Darwin ]]; then
  echo 'This script only supports macOS.' >&2
  exit 1
fi

# Hide desktop icons independently of Desktop & Dock's Show Items setting.
# Files remain accessible in ~/Desktop through Finder.
defaults write com.apple.finder CreateDesktop -bool false
killall Finder 2>/dev/null || true
echo 'Desktop icons hidden. Finder will restart if it was running.'
