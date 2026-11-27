#!/bin/bash
# Homebrew services and Dinky hooks do not inherit an interactive shell's PATH.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin${PATH:+:$PATH}"

# Monochrome palette. Keep the existing accent names for the status plugins;
# brightness distinguishes active/attention, normal, and inactive states.
BASE=0xcc000000
PANEL=0xcc000000
TEXT=0xffffffff
MUTED=0x99ffffff
SURFACE=0x33ffffff
MAUVE=0xffffffff
LAVENDER=0xffffffff
GREEN=0xffffffff
RED=0xffffffff
