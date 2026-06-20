HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000

setopt APPEND_HISTORY
setopt SHARE_HISTORY
setopt INC_APPEND_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_REDUCE_BLANKS
setopt HIST_IGNORE_SPACE

bindkey "^R" history-incremental-search-backward

eval "$(starship init zsh)"

setopt prompt_sp

export VISUAL=code
export EDITOR=$VISUAL

[ -x "$(which lsd)" ] && alias ls='lsd'
alias l='ls -alh'
alias la='ls -alh'
alias lt='ls -alrth'

eval "$(zoxide init zsh)"

export UNAME_S=$(uname | tr '[[:upper:]]' '[[:lower:]]')
[[ -s "${HOME}/.zshrc.${UNAME_S}" ]] && source "${HOME}/.zshrc.${UNAME_S}"
[[ -s "${HOME}/.zshrc.local" ]] && source "${HOME}/.zshrc.local"

[[ -f "${HOME}/.fzf.zsh" ]] && source ~/.fzf.zsh

eval "$(direnv hook zsh)"

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
