#!/bin/bash

set -eo pipefail

CURRDIR=$(pwd)
SCRIPTDIR=$(cd $(dirname $0) && pwd)

. ${SCRIPTDIR}/config.sh

# apt packages
echo
echo "installing/upgrading packages via apt"
[[ -z "$(which curl)" ]] && sudo apt install -y curl
sudo apt update
sudo apt upgrade -y
sudo apt install -y $(cat $SCRIPTDIR/bootstrap.packages/debian.txt)
sudo apt autoremove -y

if ! command -v starship &>/dev/null; then
  echo "Installing Starship..."
  curl -fsSL https://starship.rs/install.sh | sh
fi
