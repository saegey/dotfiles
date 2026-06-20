# Function to set the terminal title
function set_title() {
	local title="$1"
	echo -ne "\033]0;$title\007"
}

function update_title() {
	if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
		set_title "${USER}@${HOSTNAME}"
	else
		set_title "${PWD##*/}"
	fi
}

PROMPT_COMMAND='update_title'
trap 'update_title' DEBUG
update_title

[ -x "$(which lsd)" ] && alias ls='lsd'
alias l='ls -alh'
alias la='ls -alh'
alias lt='ls -alrth'

export LINUX_DISTRO=$(cat /etc/os-release | grep -E '^ID' | sed -e 's/^ID=//g' | sed -n '1p')
[[ -s "${HOME}/.bashrc.${LINUX_DISTRO}" ]] && source "${HOME}/.bashrc.${LINUX_DISTRO}"
