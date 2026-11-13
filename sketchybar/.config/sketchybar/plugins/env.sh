#!/bin/bash
# Homebrew services and Dinky hooks do not inherit an interactive shell's PATH.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin${PATH:+:$PATH}"

# Monochrome palette. Keep the existing accent names for the status plugins;
# brightness distinguishes active/attention, normal, and inactive states.
BASE=0xff181818
PANEL=0xcc181818
TEXT=0xffd8d8d8
MUTED=0xff808080
SURFACE=0xff404040
MAUVE=0xffffffff
LAVENDER=0xffe5e5e5
GREEN=0xffbfbfbf
RED=0xffffffff
