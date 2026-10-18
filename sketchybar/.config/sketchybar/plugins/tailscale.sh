#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

tailscale_bin=$(command -v tailscale || true)
if [[ -z "$tailscale_bin" && -x /Applications/Tailscale.app/Contents/MacOS/Tailscale ]]; then
  tailscale_bin=/Applications/Tailscale.app/Contents/MacOS/Tailscale
fi

label=Unavailable
color="$MUTED"
if [[ -n "$tailscale_bin" ]] && metadata=$("$tailscale_bin" status --json --peers=false 2>/dev/null); then
  state=$(printf '%s' "$metadata" | jq -r '.BackendState // "Unknown"')
  case "$state" in
    Running)
      if [[ $(printf '%s' "$metadata" | jq -r '.Self.Online == true') == true ]]; then
        label=On
        color="$GREEN"
        if [[ $(printf '%s' "$metadata" | jq -r '.ExitNodeStatus.Online == true') == true ]]; then
          label=Exit
        fi
      else
        label=Connecting
      fi
      ;;
    Stopped) label=Off ;;
    NeedsLogin) label=Login; color="$RED" ;;
    NeedsMachineAuth) label=Approve; color="$RED" ;;
    Starting) label=Starting ;;
    *) label=Offline ;;
  esac
fi

sketchybar --set tailscale icon.color="$color" label="$label"
