#!/bin/bash
# Homebrew services and Dinky hooks do not inherit an interactive shell's PATH.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin${PATH:+:$PATH}"

# Monochrome palette. Keep the existing accent names for the status plugins;
# brightness distinguishes active/attention, normal, and inactive states.
BASE=0xff272e33
PANEL=0xcc2e383c
TEXT=0xffd3c6aa
MUTED=0xff859289
SURFACE=0xff414b50
MAUVE=0xffa7c080
LAVENDER=0xff7fbbb3
GREEN=0xffa7c080
RED=0xffe67e80
