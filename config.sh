#!/bin/bash

set -eo pipefail

get_latest_release() {
	curl --silent "https://api.github.com/repos/$1/releases/latest" |
		grep '"tag_name":' |
		sed -E 's/.*"([^"]+)".*/\1/'
}

export BOOTSTRAP_OS=$(uname | tr '[[:upper:]]' '[[:lower:]]')
if [[ "${BOOTSTRAP_OS}" = "linux" ]]; then
	if [[ -f /etc/os-release ]]; then
		export LINUX_DISTRO=$(cat /etc/os-release | grep -E '^ID' | sed -e 's/^ID=//g' | sed -n '1p')
	else
		echo "no /etc/os-release found" >&2
		exit 1
	fi
elif [[ "${BOOTSTRAP_OS}" = "darwin" ]]; then
	export LINUX_DISTRO=na
else
	echo "unsupported OS: ${BOOTSTRAP_OS}" >&2
	exit 1
fi

if [[ -n "${NOCONFIRM}" ]]; then
	export NOCONFIRM=--noconfirm
fi
