#!/bin/bash

set -eo pipefail

CURRDIR=$(pwd)
SCRIPTDIR=$(cd $(dirname $0) && pwd)

. ./config.sh

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

# install lsd
# LSD_VERSION=$(get_latest_release lsd-rs/lsd)
# EXISTING_LSD_VERSION=none
# if [[ -x $(which lsd) ]]; then
#   EXISTING_LSD_VERSION=$(lsd --version | awk '{print $2}')
# fi
# if [[ ${LSD_VERSION} != ${EXISTING_LSD_VERSION} ]]; then
#   echo
#   echo "installing lsd ${LSD_VERSION}"
#   if [[ -x $(which lsd) ]]; then
#     sudo dpkg -P lsd
#   fi
#   LSD_DEB=lsd_${LSD_VERSION}_amd64.deb
#   sudo wget https://github.com/lsd-rs/lsd/releases/download/${LSD_VERSION}/${LSD_DEB} -O /tmp/${LSD_DEB}
#   sudo dpkg -i /tmp/${LSD_DEB}
#   sudo rm -f /tmp/${LSD_DEB}
# fi
