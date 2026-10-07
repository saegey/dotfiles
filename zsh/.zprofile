
if [[ -x /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi
# export SSH_AUTH_SOCK=/Users/adamsaegebarth/Library/Containers/com.maxgoedjen.Secretive.SecretAgent/Data/socket.ssh

# Prefer your custom FIDO-enabled ssh
[[ -d /usr/local/openssh-sk-provider/bin ]] && export PATH="/usr/local/openssh-sk-provider/bin:$PATH"
# Ensure the right libfido2 is loaded at runtime
if [[ $OSTYPE == darwin* ]] && command -v brew >/dev/null 2>&1; then
  export DYLD_LIBRARY_PATH="$(brew --prefix libfido2)/lib:${DYLD_LIBRARY_PATH:-}"
fi

alias pip='pip3'

# Added by OrbStack: command-line tools and integration
# This won't be added again if you remove it.
[[ -r ~/.orbstack/shell/init.zsh ]] && source ~/.orbstack/shell/init.zsh
