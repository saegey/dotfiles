#!/bin/bash
# Homebrew services and Dinky hooks do not inherit an interactive shell's PATH.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin${PATH:+:$PATH}"

# Monochrome palette. Keep the existing accent names for the status plugins;
# brightness distinguishes active/attention, normal, and inactive states.
BASE=0xff232136
PANEL=0xcc2a273f
TEXT=0xffe0def4
MUTED=0xff6e6a86
SURFACE=0xff56526e
MAUVE=0xffea9a97
LAVENDER=0xff9ccfd8
GREEN=0xff3e8fb0
RED=0xffeb6f92
