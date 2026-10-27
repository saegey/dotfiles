#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
exec herdr-review "$@"
