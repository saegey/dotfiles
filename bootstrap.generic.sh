#!/bin/bash

set -eo pipefail

CURRDIR=$(pwd)
SCRIPTDIR=$(cd $(dirname $0) && pwd)

. ${SCRIPTDIR}/config.sh

# setup prezto
# echo
# echo 'setting up prezto'
# cd ~
# [[ ! -d .zprezto ]] && git clone --recursive https://github.com/sorin-ionescu/prezto.git "${HOME}/.zprezto"
# [[ ! -L .zlogin ]] && ln -s .zprezto/runcoms/zlogin .zlogin
# [[ ! -L .zlogout ]] && ln -s .zprezto/runcoms/zlogout .zlogout
# [[ ! -L .zprofile ]] && ln -s .zprezto/runcoms/zprofile .zprofile
# [[ ! -L .zshenv ]] && ln -s .zprezto/runcoms/zshenv .zshenv
# cd .zprezto
# git pull
# git submodule update --init --recursive
# mkdir -p contrib
# cd contrib
# [[ ! -d fzf-tab ]] && git clone https://github.com/Aloxaf/fzf-tab
# cd fzf-tab
# git pull

# create links
echo
echo 'symlinking dotfiles'
cd ~
[[ ! -L .gitconfig ]] && ln -s ${SCRIPTDIR}/gitconfig .gitconfig
[[ ! -L .git-global-ignore ]] && ln -s ${SCRIPTDIR}/git-global-ignore .git-global-ignore
# [[ ! -L .p10k.zsh ]] && ln -s ${SCRIPTDIR}/p10k.${BOOTSTRAP_OS}.zsh .p10k.zsh
# [[ ! -L .zpreztorc ]] && ln -s ${SCRIPTDIR}/zpreztorc .zpreztorc
[[ ! -L .zshrc ]] && ln -s ${SCRIPTDIR}/zshrc .zshrc
[[ ! -L ".zshrc.${BOOTSTRAP_OS}" ]] && ln -s ${SCRIPTDIR}/zshrc.${BOOTSTRAP_OS} .zshrc.${BOOTSTRAP_OS}
[[ -f "${SCRIPTDIR}/zshrc.${LINUX_DISTRO}" && ! -L ".zshrc.${LINUX_DISTRO}" ]] && ln -s ${SCRIPTDIR}/zshrc.${LINUX_DISTRO} .zshrc.${LINUX_DISTRO}
mkdir -p .config
cd .config

ln -sf ~/.dotfiles/.config/starship.toml ~/.config/starship.toml
ln -sf ~/.dotfiles/.tool-versions ~/.tool-versions

mkdir -p ~/.ssh
ln -sf ~/.dotfiles/.ssh/config ~/.ssh/config

# create links for custom scrips
# echo
# echo 'symlinking custom scripts'
# cd ~
# mkdir -p bin
# cd bin
# for f in $(find ${SCRIPTDIR}/bin -maxdepth 1 -type f); do
#   [[ ! -L $(basename ${f}) ]] && ln -s ${f}
# done
# if [[ -d ${SCRIPTDIR}/bin/${BOOTSTRAP_OS} ]]; then
#   for f in $(find ${SCRIPTDIR}/bin/${BOOTSTRAP_OS} -type f); do
#     [[ ! -L $(basename ${f}) ]] && ln -s ${f}
#   done
# fi
if [[ ! -z ${LINUX_DISTRO} && -d ${SCRIPTDIR}/bin/linux/${LINUX_DISTRO} ]]; then
	for f in $(find ${SCRIPTDIR}/bin/linux/${LINUX_DISTRO} -type f); do
		[[ ! -L $(basename ${f}) ]] && ln -s ${f}
	done
fi

# run os-specific shit
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
