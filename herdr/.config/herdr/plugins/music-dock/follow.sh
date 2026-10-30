#!/bin/bash
set -euo pipefail
export PATH="$HOME/.local/share/mise/shims:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin${PATH:+:$PATH}"
exec "$HOME/.local/bin/herdr-music-dock" --follow
