#!/bin/bash

# Function to check if the operating system is macOS
is_macos() {
  [[ "$(uname)" == "Darwin" ]]
}

# Function to install macOS-specific tools
install_macos_tools() {
  echo "Installing macOS-specific tools..."

  # Install Homebrew if not already installed
  if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi

  # Install packages from Brewfile
  if [ -f "~/.dotfiles/Brewfile" ]; then
    echo "Installing packages from Brewfile..."
    brew bundle --file ~/.dotfiles/Brewfile
  fi

  # Setup Hammerspoon configuration
  mkdir -p ~/.hammerspoon
  ln -sf ~/.dotfiles/hammerspoon/init.lua ~/.hammerspoon/init.lua
  ln -sf ~/.dotfiles/hammerspoon/grid.lua ~/.hammerspoon/grid.lua

  # Add any other macOS-specific installation commands here
  echo "macOS-specific tools installed."
}

# Main script execution
echo "Starting setup script..."

# Install general tools and configurations
echo "Setting up general tools and configurations..."
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

# Install macOS-specific tools if on macOS
if is_macos; then
  install_macos_tools
else
  echo "Not running on macOS. Skipping macOS-specific installations."
fi

echo "Dotfiles setup completed!"
