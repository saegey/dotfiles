#!/bin/bash

set -eo pipefail

CURRDIR=$(pwd)
SCRIPTDIR=$(cd $(dirname $0) && pwd)

. ${SCRIPTDIR}/config.sh

echo
echo 'symlinking dotfiles with stow'

mkdir -p ~/.config ~/.ssh

cd ${SCRIPTDIR}
stow --target="${HOME}" zsh bash git npm starship ghostty hunk gh-dash zed tools ssh claude

# run os-specific setup
echo
echo "bootstrapping ${BOOTSTRAP_OS}"
${SCRIPTDIR}/bootstrap.${BOOTSTRAP_OS}.sh

cd $CURRDIR

TMP_TODO="none"
if [[ -f ${HOME}/tmp/bootstrap_TODO ]]; then
  TMP_TODO=$(cat ${HOME}/tmp/bootstrap_TODO)
  rm -f ${HOME}/tmp/bootstrap_TODO
fi

echo
echo
echo
echo "bootstrap done."
echo

echo ${TMP_TODO}
