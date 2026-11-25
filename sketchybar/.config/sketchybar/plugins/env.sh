#!/bin/bash
# Homebrew services and Dinky hooks do not inherit an interactive shell's PATH.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin${PATH:+:$PATH}"

# Monochrome palette. Keep the existing accent names for the status plugins;
# brightness distinguishes active/attention, normal, and inactive states.
BASE=0xff2e3440
PANEL=0xcc2e3440
TEXT=0xffd8dee9
MUTED=0xff4c566a
SURFACE=0xff434c5e
MAUVE=0xff88c0d0
LAVENDER=0xff81a1c1
GREEN=0xffa3be8c
RED=0xffbf616a
