#!/bin/bash

SCRIPTDIR=$(cd $(dirname $0) && pwd)

echo
echo "bootstrapping via brew"

[[ ! -x $(which brew) ]] && /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew analytics off
brew update
brew upgrade
brew bundle --file="${SCRIPTDIR}/Brewfile"
