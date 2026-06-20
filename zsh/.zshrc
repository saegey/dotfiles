# History Configuration

# Path to the history file
HISTFILE=~/.zsh_history

# Number of commands to remember in the history
HISTSIZE=10000
SAVEHIST=10000

# Append to the history file, don't overwrite it
setopt APPEND_HISTORY

# Share history across all sessions
setopt SHARE_HISTORY

# Save each command as it's entered
setopt INC_APPEND_HISTORY

# Remove duplicate entries from history
setopt HIST_IGNORE_DUPS
setopt HIST_REDUCE_BLANKS

# Don't store commands that start with a space
setopt HIST_IGNORE_SPACE

# Enable incremental search
bindkey "^R" history-incremental-search-backward

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
# echo $UNAME_S
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

eval "$(mise activate zsh)"

export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"

# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/saegey/Downloads/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/saegey/Downloads/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/saegey/Downloads/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/saegey/Downloads/google-cloud-sdk/completion.zsh.inc'; fi


# Created by `pipx` on 2025-07-11 16:51:11
export PATH="$PATH:/Users/saegey/.local/bin"
# The following lines have been added by Docker Desktop to enable Docker CLI completions.
fpath=(/Users/saegey/.docker/completions $fpath)
autoload -Uz compinit
compinit
# End of Docker CLI completions
