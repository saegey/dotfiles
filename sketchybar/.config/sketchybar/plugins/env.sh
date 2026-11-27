#!/bin/bash
# Homebrew services and Dinky hooks do not inherit an interactive shell's PATH.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin${PATH:+:$PATH}"

# Monochrome palette. Keep the existing accent names for the status plugins;
# brightness distinguishes active/attention, normal, and inactive states.
BASE=0xfffaf4ed
PANEL=0xccfffaf3
TEXT=0xff464261
MUTED=0xff9893a5
SURFACE=0xffcecacd
MAUVE=0xffd7827e
LAVENDER=0xff56949f
GREEN=0xff286983
RED=0xffb4637a
