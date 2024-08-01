# My Dotfiles

This repository contains my personal configuration files for various tools and applications.

## Contents

- **Zsh Configuration**: `.zshrc`
- **Starship Prompt Configuration**: `.config/starship.toml`
- **asdf Version Manager Configuration**: `.tool-versions`
- **Hammerspoon Configuration**: `hammerspoon/init.lua`

## Installation

```sh
cd; mkdir dotfiles; cd dotfiles; \
curl -#L https://github.com/saegey/dotfiles/tarball/main | \
tar -xzv --strip-components 1; \
./setup.sh
```

To set up your environment with these dotfiles, follow these steps:

1. **Clone the Repository**:

   ```sh
   git clone https://github.com/saegey/dotfiles.git ~/.dotfiles

2. **Run the Setup Script**:
   ```sh
   cd ~/.dotfiles
   chmod +x setup.sh
   ./setup.sh

This will create the necessary symlinks for the configuration files in your home directory.

3. **Set Up Hammerspoon:**

To use the Hammerspoon configuration:

Install Hammerspoon from the [official website](https://www.hammerspoon.org/).

Here's the directory structure of this repository:

```
├── .aws
│   └── config
├── .config
│   └── starship.toml
├── .gitconfig
├── .gitignore
├── .npmrc
├── .ssh
│   └── config
├── .tool-versions
├── .zshrc
├── Brewfile
├── Brewfile.lock.json
├── LICENSE
├── README.md
├── hammerspoon
│   ├── grid.lua
│   └── init.lua
└── setup.sh
```

## Customization

Feel free to customize the configuration files to suit your needs.

## License

This project is licensed under the MIT License.
