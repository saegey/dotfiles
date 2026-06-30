#!/bin/bash

set -eo pipefail

SCRIPTDIR=$(cd $(dirname $0) && pwd)
EXTENSIONS_FILE="${SCRIPTDIR}/gh/extensions.txt"

echo
echo "bootstrapping gh extensions"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is not installed; skipping gh extensions"
  exit 0
fi

if [[ ! -f "${EXTENSIONS_FILE}" ]]; then
  echo "no gh extensions manifest found; skipping"
  exit 0
fi

while IFS= read -r extension; do
  [[ -z "${extension}" ]] && continue
  [[ "${extension}" =~ ^# ]] && continue

  if gh extension list | awk '{print $2}' | grep -qx "${extension}"; then
    gh extension upgrade "${extension}"
  else
    gh extension install "${extension}"
  fi
done < "${EXTENSIONS_FILE}"
