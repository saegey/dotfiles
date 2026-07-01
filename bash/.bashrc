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

docker-use() {
	local context="$1"

	if [[ -z "$context" ]]; then
		echo "usage: docker-use <orbstack|colima|default>" >&2
		return 1
	fi

	docker context use "$context"
}

colima-start() {
	local has_cpu=0
	local has_memory=0
	local has_disk=0
	local arg

	for arg in "$@"; do
		case "$arg" in
			--cpu|--cpu=*) has_cpu=1 ;;
			--memory|--memory=*) has_memory=1 ;;
			--disk|--disk=*) has_disk=1 ;;
		esac
	done

	local -a args
	args=("$@")

	(( has_cpu )) || args+=(--cpu "${COLIMA_CPU:-4}")
	(( has_memory )) || args+=(--memory "${COLIMA_MEMORY:-8}")
	(( has_disk )) || args+=(--disk "${COLIMA_DISK:-100}")

	command colima start "${args[@]}" || return $?
	docker context use colima >/dev/null 2>&1 || true
	docker context show
}

colima-stop() {
	command colima stop "$@" || return $?
	docker context inspect orbstack >/dev/null 2>&1 && docker context use orbstack >/dev/null 2>&1
	docker context show
}

alias docker-orbstack='docker-use orbstack'
alias docker-colima='docker-use colima'

export LINUX_DISTRO=$(cat /etc/os-release | grep -E '^ID' | sed -e 's/^ID=//g' | sed -n '1p')
[[ -s "${HOME}/.bashrc.${LINUX_DISTRO}" ]] && source "${HOME}/.bashrc.${LINUX_DISTRO}"
