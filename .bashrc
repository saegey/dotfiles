# Function to set the terminal title
function set_title() {
	local title="$1"
	echo -ne "\033]0;$title\007"
}

# Function to update the title based on whether the session is SSH or local
function update_title() {
	if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
		set_title "${USER}@${HOSTNAME}"
	else
		set_title "${PWD##*/}"
	fi
}

# Update the title before each command prompt
PROMPT_COMMAND='update_title'

# Update the title when a command is executed
trap 'update_title' DEBUG

# Initial title update
update_title

# helpful aliases
alias ls='lsd'
alias l='ls -alh'
alias la='ls -alh'
alias lt='ls -alrth'

export LINUX_DISTRO=$(cat /etc/os-release | grep -E '^ID' | sed -e 's/^ID=//g' | sed -n '1p')

echo "LINUX DISTRO: ${LINUX_DISTRO}"

[[ -s "${HOME}/.bashrc.${LINUX_DISTRO}" ]] && source "${HOME}/.bashrc.${LINUX_DISTRO}"
