
eval "$(/opt/homebrew/bin/brew shellenv)"
# export SSH_AUTH_SOCK=/Users/adamsaegebarth/Library/Containers/com.maxgoedjen.Secretive.SecretAgent/Data/socket.ssh

# Prefer your custom FIDO-enabled ssh
export PATH="/usr/local/openssh-sk-provider/bin:$PATH"
# Ensure the right libfido2 is loaded at runtime
export DYLD_LIBRARY_PATH="$(brew --prefix libfido2)/lib:$DYLD_LIBRARY_PATH"

alias pip='pip3'

# Added by OrbStack: command-line tools and integration
# This won't be added again if you remove it.
source ~/.orbstack/shell/init.zsh 2>/dev/null || :
