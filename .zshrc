eval "$(starship init zsh)"

# zsh options
setopt prompt_sp

export VISUAL=vscode
export EDITOR=$VISUAL

# helpful aliases
[ -x "$(which lsd)" ] && alias ls='lsd'
alias l='ls -alh'
alias la='ls -alh'
alias lt='ls -alrth'

# zoxide
eval "$(zoxide init zsh)"

export UNAME_S=$(uname | tr '[[:upper:]]' '[[:lower:]]')
echo $UNAME_S
[[ -s "${HOME}/.zshrc.${UNAME_S}" ]] && source "${HOME}/.zshrc.${UNAME_S}"
[[ -s "${HOME}/.zshrc.local" ]] && source "${HOME}/.zshrc.local"

# fzf
[[ -f "${HOME}/.fzf.zsh" ]] && source ~/.fzf.zsh

eval "$(direnv hook zsh)"

# Function to set the terminal title
function set_title() {
  local title="$1"
  echo -ne "\033]0;$title\007"
}

# Set the title based on whether the session is local or SSH
precmd() {
  if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    local title="${USER}@${HOST} ${PWD/#$HOME/~}"
  else
    local title="${PWD/#$HOME/~}"
  fi
  set_title "$title"
}

# Update the title while running commands
preexec() {
  if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    set_title "$(basename "$1")"
  else
    set_title "${PWD/#$HOME/~}"
  fi
}

# source os/airbnb/local stuff
export UNAME_S=$(uname | tr '[[:upper:]]' '[[:lower:]]')

echo "${UNAME}"

[[ -s "${HOME}/.zshrc.${UNAME_S}" ]] && source "${HOME}/.zshrc.${UNAME_S}"
