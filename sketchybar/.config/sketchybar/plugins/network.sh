#!/bin/bash
set -euo pipefail
source "${CONFIG_DIR:-$HOME/.config/sketchybar}/plugins/env.sh"

# Report the default route rather than a saved Wi-Fi name. This also works on
# Ethernet and IPv6-only networks without requiring location permission.
interface=$(route -n get default 2>/dev/null | awk '/interface:/ {print $2; exit}' || true)
if [[ -z "$interface" ]]; then
  interface=$(route -n get -inet6 default 2>/dev/null | awk '/interface:/ {print $2; exit}' || true)
fi

label=Offline
color="$RED"
if [[ -n "$interface" ]]; then
  port=$(networksetup -listallhardwareports 2>/dev/null | awk -v device="$interface" '
    /^Hardware Port:/ {sub(/^Hardware Port: /, ""); port=$0}
    $1 == "Device:" && $2 == device {print port; exit}
  ' || true)
  color="$GREEN"
  case "$port" in
    Wi-Fi|AirPort) label=Wi-Fi ;;
    *Ethernet*) label=LAN ;;
    *)
      case "$interface" in
        utun*|ppp*|ipsec*) label=VPN ;;
        *) label="$interface" ;;
      esac
      ;;
  esac
fi

sketchybar --set network icon.color="$color" label="$label"
