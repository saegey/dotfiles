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

# distro-specific boostrap
echo
LINUX_DISTRO=$(echo "${LINUX_DISTRO}" | sed -n '1p')

if [[ -f ${SCRIPTDIR}/bootstrap.${LINUX_DISTRO}.sh ]]; then
	echo "bootstrapping ${LINUX_DISTRO}"
	${SCRIPTDIR}/bootstrap.${LINUX_DISTRO}.sh
else
	echo "don't know how to bootstrap ${LINUX_DISTRO}: no bootstrap.${LINUX_DISTRO}.sh" >&2
	exit 1
fi

cd ${CURRDIR}
