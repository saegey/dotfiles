# Source .bashrc if it exists
if [ -f ~/.bashrc ]; then
  . ~/.bashrc
fi

if command -v starship >/dev/null 2>&1; then
  eval "$(starship init bash)"
fi
