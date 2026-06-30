HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000

setopt APPEND_HISTORY
setopt SHARE_HISTORY
setopt INC_APPEND_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_FIND_NO_DUPS
setopt HIST_SAVE_NO_DUPS
setopt HIST_REDUCE_BLANKS
setopt HIST_IGNORE_SPACE
setopt EXTENDED_HISTORY

setopt AUTO_CD
setopt INTERACTIVE_COMMENTS
setopt NO_BEEP

bindkey "^R" history-incremental-search-backward

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
alias v='zed .'

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

eval "$(mise activate zsh)"
