#!/bin/bash

set -euo pipefail

SCRIPTDIR=$(cd "$(dirname "$0")" && pwd)

usage() {
  echo 'Usage: ./bootstrap.sh [--apply] [--packages name ...]'
  echo 'Defaults to a preview. --packages limits Stow to the named packages.'
  echo 'Package setup is separate; this command never runs a package manager.'
}

apply=false
selected=false
packages=()
while (( $# )); do
  case "$1" in
    --apply) apply=true ;;
    --packages)
      if [[ $selected == true ]]; then
        echo '--packages may only be specified once' >&2
        exit 2
      fi
      selected=true
      ;;
    --help|-h) usage; exit 0 ;;
    --*) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)
      if [[ $selected != true ]]; then
        echo "Unexpected package: $1 (use --packages first)" >&2
        usage >&2
        exit 2
      fi
      packages+=("$1")
      ;;
  esac
  shift
done

if ! command -v stow >/dev/null 2>&1; then
  echo 'GNU Stow is required (on Omarchy: omarchy pkg add stow).' >&2
  exit 1
fi

if [[ $selected == true ]]; then
  if (( ${#packages[@]} == 0 )); then
    echo '--packages needs at least one package name' >&2
    exit 2
  fi
else
  # Opt in to Bash, SSH, Git, tools, and Ghostty only after reviewing
  # each machine's existing config. In particular, keep Omarchy's defaults.
  packages=(zsh npm hunk gh-dash)
fi

for package in "${packages[@]}"; do
  case "$package" in
    zsh|bash|git|npm|starship|ghostty|hunk|gh-dash|zed|tools|ssh|claude) ;;
    *) echo "Unknown package: $package" >&2; exit 2 ;;
  esac
done

cd "${SCRIPTDIR}"
echo "Packages: ${packages[*]}"
# Always check all requested packages before linking any of them.
# No --adopt/--override: pre-existing files must be handled explicitly.
stow --no-folding --simulate --verbose --target="${HOME}" "${packages[@]}"
if [[ $apply == true ]]; then
  stow --no-folding --target="${HOME}" "${packages[@]}"
  echo 'Links installed. Package installation, shell changes and Git/SSH credentials are manual.'
else
  echo 'Preview only; rerun with --apply to install the listed links.'
fi
