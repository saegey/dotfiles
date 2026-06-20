#!/bin/bash

SCRIPTDIR=$(cd $(dirname $0) && pwd)

mkdir -p ~/bin
cd ~/bin
# [[ ! -L spotify ]] && ln -s ${SCRIPTDIR}/bin/spotify
# [[ ! -L rebrew ]] && ln -s ${SCRIPTDIR}/bin/rebrew

# set up brew & pip
${SCRIPTDIR}/bootstrap.brew.sh

# bootstrap fzf (install completions, etc)
# ${SCRIPTDIR}/bootstrap.fzf.sh

# installing rust
# $SCRIPTDIR/bootstrap.darwin.rust.sh

# installing fonts
# $SCRIPTDIR/bootstrap.darwin.fonts.sh

