HISTFILE="${ZDOTDIR:-$HOME}/.zsh_history"
HISTSIZE=100000
SAVEHIST=100000

# SHARE_HISTORY is the single writer/reader mode for the native history file.
# Do not combine it with APPEND_HISTORY or INC_APPEND_HISTORY.
setopt SHARE_HISTORY
setopt HIST_EXPIRE_DUPS_FIRST
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_SAVE_NO_DUPS
setopt HIST_REDUCE_BLANKS
setopt HIST_IGNORE_SPACE
setopt EXTENDED_HISTORY

setopt AUTO_CD
setopt INTERACTIVE_COMMENTS
setopt NO_BEEP

# completion (native)
autoload -Uz compinit
compinit -d "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/.zcompdump"
zstyle ':completion:*:*:make:*' tag-order 'targets'
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

eval "$(starship init zsh)"

setopt prompt_sp

export VISUAL=zed
export EDITOR=zed

[ -x "$(which lsd)" ] && alias ls='lsd'
alias l='ls -alh'
alias la='ls -alh'
alias lt='ls -alrth'
alias ll='ls -la'
alias l1='ls -1'

alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias grep='grep --color=auto'

alias c='codex'
alias m='mise'
alias g='git'
alias gc='git commit'
alias gp='git push'
alias gco='git checkout'
alias gf='git fetch'
alias gpl='git pull'
alias v='zed .'

# Page Terraform plans with color intact. -X keeps the output visible after
# quitting the pager; all Terraform plan flags can be passed to this function.
tfplan() {
  setopt localoptions pipefail
  command terraform plan "$@" | command less -R -X
}

# Move the last unpushed commit from main onto a new branch. This intentionally
# refuses dirty worktrees and commits already present on main's upstream.
gmove() {
  local new_branch="$1"
  local current_branch

  if (( $# != 1 )) || [[ -z "$new_branch" ]]; then
    echo "usage: gmove <new-branch>" >&2
    return 2
  fi

  current_branch="$(command git branch --show-current)" || return
  if [[ "$current_branch" != "main" ]]; then
    echo "gmove must be run from main (currently on ${current_branch:-detached HEAD})" >&2
    return 1
  fi

  if [[ -n "$(command git status --porcelain)" ]]; then
    echo "gmove requires a clean worktree" >&2
    return 1
  fi

  command git check-ref-format --branch "$new_branch" >/dev/null || {
    echo "invalid branch name: $new_branch" >&2
    return 2
  }
  if command git show-ref --verify --quiet "refs/heads/$new_branch"; then
    echo "branch already exists: $new_branch" >&2
    return 1
  fi

  command git rev-parse --verify --quiet HEAD^ >/dev/null || {
    echo "main has no commit to move" >&2
    return 1
  }
  if command git rev-parse --verify --quiet '@{upstream}' >/dev/null &&
    command git merge-base --is-ancestor HEAD '@{upstream}'; then
    echo "HEAD is already pushed to main's upstream; revert it on main instead" >&2
    return 1
  fi

  command git branch -- "$new_branch" HEAD || return
  if ! command git reset --keep HEAD^; then
    echo "created $new_branch but left main unchanged" >&2
    return 1
  fi
  command git switch "$new_branch"
}

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

[ -x "$(which bat)" ] && alias cat='bat'
[ -x "$(which lsd)" ] && alias tree='lsd --tree'

eval "$(zoxide init zsh)"

export UNAME_S=$(uname | tr '[[:upper:]]' '[[:lower:]]')
[[ -s "${HOME}/.zshrc.${UNAME_S}" ]] && source "${HOME}/.zshrc.${UNAME_S}"
[[ -s "${HOME}/.zshrc.local" ]] && source "${HOME}/.zshrc.local"

export FZF_DEFAULT_OPTS=" \
--color=bg+:#414559,bg:#303446,spinner:#f4b8e4,hl:#8caaee \
--color=fg:#c6d0f5,header:#8caaee,info:#ca9ee6,pointer:#f4b8e4 \
--color=marker:#a6d189,fg+:#c6d0f5,prompt:#ca9ee6,hl+:#8caaee \
--color=border:#414559 \
--preview 'bat --style=numbers --color=always --line-range=:200 {}'"

[[ -f "${HOME}/.fzf.zsh" ]] && source ~/.fzf.zsh

function set_title() {
  local title="$1"
  echo -ne "\033]0;$title\007"
}

precmd() {
  if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    local title="${USER}@${HOST} ${PWD/#$HOME/~}"
  else
    local title="${PWD/#$HOME/~}"
  fi
  set_title "$title"
}

preexec() {
  if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    set_title "$(basename "$1")"
  else
    set_title "${PWD/#$HOME/~}"
  fi
}

workon() {
  local ticket="${1:?usage: workon <TICKET-ID>}"

  local prefix="${BRANCH_PREFIX:-adam}"
  local branch="${prefix}/${ticket}"

  local wt_id
  wt_id=$(supacode repo worktree-new --branch "$branch" --pin) || {
    echo "error: failed to create worktree" >&2
    return 1
  }

  supacode worktree focus -w "$wt_id"

  supacode tab new -w "$wt_id" -i "claude \"Lets work on ticket ${ticket} and come up with a plan to implement. Lets discuss.\""
}

review() {
  local ticket="${1:?usage: review <TICKET-ID>}"

  local pr_info
  pr_info=$(gh pr list --search "$ticket" --json number,headRefName --jq '.[0]') || {
    echo "error: could not find PR for $ticket" >&2
    return 1
  }

  local pr_number=$(echo "$pr_info" | jq -r '.number')
  local branch=$(echo "$pr_info" | jq -r '.headRefName')

  if [[ -z "$pr_number" || "$pr_number" == "null" ]]; then
    echo "error: no PR found for $ticket" >&2
    return 1
  fi

  git fetch origin "$branch" || {
    echo "error: could not fetch branch $branch" >&2
    return 1
  }

  local wt_id
  wt_id=$(supacode repo worktree-new --branch "$branch" --base "origin/${branch}" --upstream "origin/${branch}" --pin) || {
    echo "error: failed to create worktree" >&2
    return 1
  }

  supacode worktree focus -w "$wt_id"

  supacode tab new -w "$wt_id" -i "claude --model opus \"/pr-review ${pr_number}\""
}

eval "$(mise activate zsh)"

fpath+=~/.zfunc; autoload -Uz compinit; compinit

if (( $+commands[atuin] )); then
  eval "$(atuin init zsh)"
fi
