# dotfiles

Personal configuration files managed with [GNU Stow](https://www.gnu.org/software/stow/).

## What's included

| Directory | Target | Description |
|-----------|--------|-------------|
| `zsh/` | `~/.zshrc`, `~/.zshrc.darwin`, etc. | Zsh config with starship, zoxide, direnv, mise |
| `git/` | `~/.gitconfig`, `~/.gitignore` | Git config with 1Password SSH signing |
| `starship/` | `~/.config/starship.toml` | Starship prompt |
| `ghostty/` | `~/.config/ghostty/config` | Ghostty terminal |
| `gh-dash/` | `~/.config/gh-dash/config.yml` | gh-dash config |
| `hunk/` | `~/.config/hunk/config.toml` | Hunk diff viewer |
| `zed/` | `~/.config/zed/` | Zed editor settings and keymaps |
| `ssh/` | `~/.ssh/config` | SSH config with 1Password agent |
| `tools/` | `~/.config/mise/config.toml`, `~/.tool-versions` | mise version manager |
| `npm/` | `~/.npmrc` | npm config |
| `bash/` | `~/.bash_profile`, `~/.bashrc`, etc. | Bash config |
| `claude/` | `~/.claude/settings.json` | Claude Code settings |

## Installation

```sh
git clone https://github.com/saegey/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
./bootstrap.sh
```

`bootstrap.sh` uses `stow` to symlink everything into `$HOME`, then runs the OS-specific setup script (`bootstrap.darwin.sh` on macOS).

## Local overrides

Machine-specific config that shouldn't be committed goes in:
- `~/.zshrc.local` — sourced at the end of `.zshrc`
- `~/.gitconfig.local` — included at the end of `.gitconfig`

## Docker runtimes

- OrbStack remains the default Docker context when it is already selected.
- Colima is installed, but it does not start automatically.
- Use `colima-start` to start Colima and switch Docker to the `colima` context.
- `colima-start` defaults to `--cpu 4 --memory 8 --disk 100` unless you pass your own values.
- Override the defaults with `COLIMA_CPU`, `COLIMA_MEMORY`, or `COLIMA_DISK` in `~/.zshrc.local`.
- Use `colima-stop` to stop Colima and switch Docker back to `orbstack` when that context exists.
- Use `docker-orbstack`, `docker-colima`, or `docker-use <context>` for manual context switching.

## Notes

- Git commits are signed via SSH using 1Password. Set `user.signingkey` in `~/.gitconfig.local`.
- `~/.zshrc.local` is a good place for machine-specific PATH entries (gcloud, postgresql, etc.).

## License

MIT
