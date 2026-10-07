# dotfiles

Personal configuration files managed with [GNU Stow](https://www.gnu.org/software/stow/).

## What's included

| Directory | Target | Description |
|-----------|--------|-------------|
| `zsh/` | `~/.zshrc`, `~/.zshrc.darwin`, etc. | Zsh config with starship, zoxide, direnv, mise, Atuin |
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

`./bootstrap.sh` previews the safe starter set (`zsh`, `npm`, `hunk`, `gh-dash`) without changing anything. `./bootstrap.sh --apply` links only those packages. GNU Stow must already be installed; any conflicting existing file aborts the entire operation. Bootstrap does **not** install software, change your login shell, or run the macOS/Homebrew or Linux package scripts.

Select additional packages explicitly after reviewing their configs and existing files:

```sh
./bootstrap.sh --packages git ssh         # preview
./bootstrap.sh --apply --packages git ssh # link only if conflict-free
```

On Omarchy, keep its `~/.bashrc`, Ghostty config, and other existing configurations unless you intentionally migrate them. In particular, do **not** Stow `bash` or `ghostty` over Omarchy's files. If staying on Bash, integrate `atuin init bash` into the existing `~/.bashrc` rather than replacing it. For Zsh, install it separately, link the `zsh` package, test with `zsh`, then optionally change the login shell. Git and SSH packages require review of local credentials and agents before opting in.

## Shell history

Zsh keeps a shared, extended history file at `~/.zsh_history`; Atuin also records
commands with their timestamp, directory, host, exit status, and duration.
`.zshrc` initializes Atuin when it is installed. Install Atuin separately. On a
new machine, import the existing Zsh history once (if there is any):

```sh
atuin import zsh
```

To share encrypted Atuin history across machines, complete Atuin's optional account
setup with `atuin account login` (or `atuin account register`) and run `atuin sync`.

`scripts/history-review` writes a chronological, tab-separated export suitable for
reviewing repeated commands and command sequences. It writes to standard output by
default, so choose an appropriately protected destination:

```sh
./scripts/history-review 500 > recent-atuin-history.tsv
```

The columns are timestamp, exit status, duration, host, directory, and command. Pass
an output path as the second argument to have the script create a mode-0600 file.

## Local overrides

Machine-specific config that shouldn't be committed goes in:
- `~/.zshrc.local` — sourced at the end of `.zshrc`
- `~/.gitconfig.local` — included at the end of `.gitconfig`; set `commit.gpgsign = true` and `gpg.ssh.program` to the OS-specific signer only where available
- `~/.ssh/config.local` — included first in `.ssh/config`; put OS-specific `IdentityAgent` and optional OrbStack/Colima includes there
- `~/.bashrc.local` — sourced by the shared Bash config

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

- Git SSH signing is opt-in per machine: set `user.signingkey`, `commit.gpgsign` and the OS-specific `gpg.ssh.program` in `~/.gitconfig.local`. On macOS the signer is `/Applications/1Password.app/Contents/MacOS/op-ssh-sign`; Linux installations must use their own installed path.
- `~/.zshrc.local` is a good place for machine-specific PATH entries (gcloud, postgresql, etc.).

## License

MIT
