# Amazon Q pre block. Keep at the top of this file.
[[ -f "${HOME}/Library/Application Support/amazon-q/shell/zshrc.pre.zsh" ]] && builtin source "${HOME}/Library/Application Support/amazon-q/shell/zshrc.pre.zsh"
# ~/.zshrc

# eval "$(starship init zsh)"

. "$HOME/.asdf/asdf.sh"

eval "$(starship init zsh)"

# bit
case ":$PATH:" in
  *":/Users/asaegebarth/bin:"*) ;;
  *) export PATH="$PATH:/Users/asaegebarth/bin" ;;
esac
# bit end


[[ -f "$HOME/fig-export/dotfiles/dotfile.zsh" ]] && builtin source "$HOME/fig-export/dotfiles/dotfile.zsh"

# Amazon Q post block. Keep at the bottom of this file.
[[ -f "${HOME}/Library/Application Support/amazon-q/shell/zshrc.post.zsh" ]] && builtin source "${HOME}/Library/Application Support/amazon-q/shell/zshrc.post.zsh"
