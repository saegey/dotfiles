#!/bin/bash

# Function to check if the operating system is macOS
is_macos() {
  [[ "$(uname)" == "Darwin" ]]
}

# Function to check if the operating system is Debian
is_debian() {
  grep -q "Debian" /etc/os-release
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

  # Install Starship
  if ! command -v starship &> /dev/null; then
    echo "Installing Starship..."
    brew install starship
  fi

  # Ensure .zshrc exists and add Starship initialization
  if [ ! -f ~/.zshrc ]; then
    touch ~/.zshrc
  fi

  if ! grep -q 'eval "$(starship init zsh)"' ~/.zshrc; then
    echo 'eval "$(starship init zsh)"' >> ~/.zshrc
  fi

  echo "macOS-specific tools installed."
}

# Function to set up Zsh on Debian
setup_zsh_on_debian() {
  echo "Setting up Zsh on Debian..."

  # Install zsh if not already installed
  if ! command -v zsh &> /dev/null; then
    echo "Installing zsh..."
    sudo apt update
    sudo apt install -y zsh
  fi

  # Verify zsh is listed in /etc/shells
  if ! grep -q "/usr/bin/zsh" /etc/shells; then
    echo "/usr/bin/zsh is not listed in /etc/shells. Adding it..."
    echo "/usr/bin/zsh" | sudo tee -a /etc/shells
  fi

  # Change default shell to zsh
  if [ "$SHELL" != "/usr/bin/zsh" ]; then
    echo "Changing default shell to zsh..."
    chsh -s /usr/bin/zsh
    zsh
  else
    echo "Default shell is already zsh."
  fi

  # Install Starship
  if ! command -v starship &> /dev/null; then
    echo "Installing Starship..."
    curl -fsSL https://starship.rs/install.sh | sh
  fi

  # Install asdf
  if [ ! -d "$HOME/.asdf" ]; then
    echo "Installing asdf..."
    git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.10.0
  fi

  # Ensure .zshrc exists and add asdf and Starship initialization
  if [ ! -f ~/.zshrc ]; then
    touch ~/.zshrc
  fi

  if ! grep -q 'source $HOME/.asdf/asdf.sh' ~/.zshrc; then
    echo 'source $HOME/.asdf/asdf.sh' >> ~/.zshrc
  fi

  if ! grep -q 'eval "$(starship init zsh)"' ~/.zshrc; then
    echo 'eval "$(starship init zsh)"' >> ~/.zshrc
  fi

  echo "Zsh setup completed."
}

# Main script execution
echo "Starting setup script..."

# Install general tools and configurations
echo "Setting up general tools and configurations..."
# Create symlinks for Zsh configuration
if [ -f ~/.dotfiles/.zshrc ]; then
  rm -f ~/.zshrc
  ln -sf ~/.dotfiles/.zshrc ~/.zshrc
fi

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
fi

# Set up Zsh and install Starship if on Debian
if is_debian; then
  setup_zsh_on_debian
fi

echo "Dotfiles setup completed!"

source ~/.zshrc
