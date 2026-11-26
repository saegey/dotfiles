# Source .bashrc if it exists
if [ -f ~/.bashrc ]; then
  . ~/.bashrc
fi

if command -v starship >/dev/null 2>&1; then
  eval "$(starship init bash)"
fi

# Added by Kiri: its docker and kiri commands (kiri setup --uninstall removes this)
case ":$PATH:" in *":$HOME/.kiri/bin:"*) ;; *) export PATH="$PATH:$HOME/.kiri/bin" ;; esac
