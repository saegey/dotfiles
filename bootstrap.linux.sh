#!/bin/bash

set -eo pipefail

CURRDIR=$(pwd)
SCRIPTDIR=$(cd $(dirname $0) && pwd)

# create links
mkdir -p ~/.config
cd ~/.config
# [[ ! -L foot ]] && ln -s ${SCRIPTDIR}/config/foot foot
# echo
# echo "installing fonts"
# mkdir -p ~/.local/share/fonts
# cd ~/.local/share/fonts
# for f in $(ls ${SCRIPTDIR}/fonts); do
#   [[ ! -L $f ]] && ln -s ${SCRIPTDIR}/fonts/$f
# done

# distro-specific bootstrap
echo
# LINUX_DISTRO=$(echo "${LINUX_DISTRO}" | sed -n '1p')

if [[ -f ${SCRIPTDIR}/bootstrap.${LINUX_DISTRO}.sh ]]; then
  echo "bootstrapping ${LINUX_DISTRO}"
  "${SCRIPTDIR}/bootstrap.${LINUX_DISTRO}.sh"
else
  echo "No package bootstrap for ${LINUX_DISTRO}; dotfile links are ready."
fi

cd ${CURRDIR}
