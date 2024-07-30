#!/bin/sh

# Create symlinks for Zsh configuration
ln -sf ~/.dotfiles/.zshrc ~/.zshrc

# Create symlinks for Starship configuration
mkdir -p ~/.config
ln -sf ~/.dotfiles/.config/starship.toml ~/.config/starship.toml

# Create symlinks for asdf configuration
ln -sf ~/.dotfiles/.tool-versions ~/.tool-versions


echo "Dotfiles setup completed!"
