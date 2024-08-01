#!/bin/sh

# Create symlinks for Zsh configuration
ln -sf ~/.dotfiles/.zshrc ~/.zshrc

# Create symlinks for Starship configuration
mkdir -p ~/.config
ln -sf ~/.dotfiles/.config/starship.toml ~/.config/starship.toml

# Create symlinks for asdf configuration
ln -sf ~/.dotfiles/.tool-versions ~/.tool-versions

# Create symlinks for SSH configuration
mkdir -p ~/.ssh
ln -sf ~/.dotfiles/.ssh/config ~/.ssh/config

# Create symlinks for AWS CLI configuration
mkdir -p ~/.aws
ln -sf ~/.dotfiles/.aws/config ~/.aws/config

mkdir -p ~/.hammerspoon
ln -sf ~/.dotfiles/.hammerspoon/init.lua ~/.hammerspoon/init.lua
ln -sf ~/.dotfiles/.hammerspoon/grid.lua ~/.hammersppon/grid.lua

# Install Homebrew packages from Brewfile
if [ -f ~/.dotfiles/Brewfile ]; then
    brew bundle --file ~/.dotfiles/Brewfile
fi


echo "Dotfiles setup completed!"
