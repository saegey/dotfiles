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
| `supacode/settings.shared.json` | applied to `~/.supacode/settings.json` | Shared Supacode global preferences |

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

Supacode's live settings file (`~/.supacode/settings.json`) is deliberately local and is never symlinked or committed. It stores repository roots, per-repository scripts, pinned worktrees, and other machine-specific state.

`supacode/settings.shared.json` is the explicitly allowlisted set of shared global preferences. Apply it after installing Supacode (or after cloning these dotfiles):

```sh
./scripts/sync_supacode_settings.sh apply
```

To update the committed preferences from this machine, run the following and review the diff before committing. The script exports only keys already present in the shared template, so newly introduced local fields cannot be committed accidentally.

```sh
./scripts/sync_supacode_settings.sh export
```

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
