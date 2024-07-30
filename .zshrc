# Fig pre block. Keep at the top of this file.
[[ -f "$HOME/.fig/shell/zshrc.pre.zsh" ]] && builtin source "$HOME/.fig/shell/zshrc.pre.zsh"
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

# Fig post block. Keep at the bottom of this file.
[[ -f "$HOME/.fig/shell/zshrc.post.zsh" ]] && builtin source "$HOME/.fig/shell/zshrc.post.zsh"
