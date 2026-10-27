# dotfiles

Personal configuration files managed with [GNU Stow](https://www.gnu.org/software/stow/).

## What's included

| Directory | Target | Description |
|-----------|--------|-------------|
| `zsh/` | `~/.zshrc`, `~/.zshrc.darwin`, etc. | Zsh config with starship, zoxide, direnv, mise, Atuin |
| `git/` | `~/.gitconfig`, `~/.gitignore` | Git config with 1Password SSH signing |
| `starship/` | `~/.config/starship.toml` | Starship prompt |
| `ghostty/` | `~/.config/ghostty/config` | Ghostty terminal |
| `aerospace/` | `~/.config/aerospace/aerospace.toml` | Keyboard-driven tiling on macOS |
| `dinky/` | `~/.config/dinky/dinky.toml` | Optional Dinky trial with native macOS Spaces |
| `sketchybar/` | `~/.config/sketchybar/` | Catppuccin bar with Dinky workspaces and system status |
| `hammerspoon/` | `~/.hammerspoon/` | AeroSpace helpers, shortcut popup, and rounded screen corners |
| `karabiner/` | `~/.config/karabiner/karabiner.json` | Caps Lock as Hyper when held, Escape when tapped |
| `smb-archive/` | macOS LaunchAgent and `~/.local/bin/townhaus-archive-mount` | Reconnect the Townhaus SMB archive when Beelink is reachable |
| `ghzinga/` | `~/.config/ghzinga/config.toml` | Ghzinga UI with Catppuccin theme |
| `gh-dash/` | `~/.config/gh-dash/config.yml` | gh-dash config |
| `herdr/` | `~/.config/herdr/config.toml`, `~/.local/bin/herdr-repo-tasks` | Herdr config and repository task picker |
| `hunk/` | `~/.config/hunk/config.toml` | Hunk diff viewer |
| `zed/` | `~/.config/zed/` | Zed editor settings and keymaps |
| `ssh/` | `~/.ssh/config` | SSH config with per-machine 1Password agent selection for Home Assistant |
| `tools/` | `~/.config/mise/config.toml` | Global mise tool versions |
| `npm/` | `~/.npmrc` | npm config |
| `bash/` | `~/.bash_profile`, `~/.bashrc`, etc. | Bash config |
| `claude/` | `~/.claude/settings.json` | Claude Code settings |
| `ttt/` | `~/.config/ttt/themes/catppuccin-mocha.json` | Catppuccin Mocha theme for TTT Editor |
| `btop/` | `~/.config/btop/themes/catppuccin_mocha.theme` | Catppuccin Mocha theme for btop |
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
./bootstrap.sh --apply --packages aerospace hammerspoon # macOS only
./bootstrap.sh --apply --packages smb-archive       # optional macOS SMB auto-mount
./bootstrap.sh --apply --packages ttt                # TTT theme
./bootstrap.sh --apply --packages btop               # btop theme
./bootstrap.sh --apply --packages ghzinga            # Ghzinga theme
```

The TTT package links the Catppuccin Mocha theme without replacing your
`settings.json`. Select `catppuccin-mocha` in **View → Switch Theme**, or set
`"theme": "catppuccin-mocha"` in `~/.config/ttt/settings.json` to make it the
default.

The btop package links only the theme file, preserving your existing
`btop.conf`. In btop, press `Esc`, choose **Options**, then select
`catppuccin_mocha` as the color theme.

## Caps Lock / Hyper (macOS)

```sh
brew install --cask hammerspoon
./bootstrap.sh --apply --packages hammerspoon
open -a Hammerspoon
```

Grant Hammerspoon Accessibility permission. The `caps-hyper.lua` module uses
macOS's built-in `hidutil` to map Caps Lock to F18, then intercepts that key:
a quick tap (under 250 ms) sends Escape; holding it with another key adds
Control+Option+Shift+Command (Hyper), without a hold delay. Existing unrelated
`hidutil` mappings are preserved, and a conflicting Caps Lock mapping is refused.
Hammerspoon restores Caps Lock on a normal quit/reload, reapplies the mapping on
wake and USB connection, and starts at login. Leave Caps Lock unchanged in macOS
Keyboard → Modifier Keys. F18 is reserved for this mapping while it is active.
Secure Input can prevent Hammerspoon from intercepting keys in password fields.

The optional `karabiner` package and Brewfile cask remain available, but its
Caps Lock rule is disabled to avoid double remapping. This machine's extension
allowlist currently blocks its virtual keyboard driver. If switching back after
approval, remove the Hammerspoon Caps Hyper startup block before enabling the
Karabiner rule. Existing Karabiner configs must be merged or backed up before
linking; bootstrap will refuse a conflicting file.

With the Hammerspoon package linked and loaded, hold Caps Lock and press
**T** for Ghostty, **B** for Chrome, **L** for Linear, **S** for Slack,
**P** for 1Password, or **K** for Secretive. Each shortcut focuses or launches
the app; Dinky handles workspace switching and placement of new windows.
Command+Option+/ toggles the persistent two-column shortcut overlay, including
app launchers, dedicated spaces, window controls, and Herdr shortcuts. Escape
closes it. The panel centers inside the usable screen area, with text capped at
14pt and scaled down as needed. An open panel resizes when displays change.

Inside Herdr, Command+D splits right and Command+Shift+D splits down.
Command+Option+Arrow keys focus the pane in that direction; the original
Control+B then H/J/K/L bindings also work. Ghostty's own bindings for these
chords are unbound so Herdr can receive them. Reload
Ghostty's configuration and run `herdr server reload-config` after linking changes.

## Dinky trial (macOS)

Install [Dinky](https://dinky.rodeo/) and link its config:

```sh
brew install --cask mikker/tap/dinky
./bootstrap.sh --apply --packages dinky
```

Quit AeroSpace and JankyBorders before opening Dinky (`open -a dinky`), then
grant Accessibility access when asked. Hammerspoon can stay running: its
AeroSpace layout helper pauses while Dinky runs, and the Command-Option-/
shortcut popup shows Dinky's bindings. Reload Hammerspoon after updating its
config.

This config keeps the Option-based focus, movement, workspace, fullscreen,
resize and layout shortcuts, 20-point inner gaps, 10-point outer gaps (56 at
the top for SketchyBar), and Catppuccin borders. Dinky
creates nine native macOS Spaces for workspaces 1–9. Option-S cycles tiles
and scrolling; Option-Comma cycles accordion orientation. Option-Shift-N moves the window to the next display
and follows it. AeroSpace's Option-Shift-Tab command to move a whole workspace
to another monitor has no binding here.

Run `dinky doctor` to check the config and macOS settings. Turn off
**Automatically rearrange Spaces based on most recent use** in System Settings
→ Desktop & Dock → Mission Control so workspace numbers stay stable. Dinky
also offers to turn off automatic Space switching when activating an app;
that enables its faster Cmd-Tab Space switching.

Dinky's login startup is off during the trial. To return to AeroSpace, quit
Dinky, run `open -a AeroSpace`, and restart JankyBorders if desired. AeroSpace's
config and login startup remain in place. Dinky restores the windows it
managed on exit; additional native Spaces may remain if they contain windows.

## SketchyBar (macOS)

```sh
brew install felixkratz/formulae/sketchybar media-control switchaudio-osx jq
# If JetBrains Mono is not already installed:
brew install --cask font-jetbrains-mono
./bootstrap.sh --apply --packages sketchybar
brew services start sketchybar
```

The Catppuccin Mocha bar uses JetBrains Mono and shows clickable Dinky workspaces
1–9, the active app, Now Playing, network and Tailscale status, audio output,
Homebrew updates, volume, and a clock. Battery status appears only when the Mac
has a battery. Click volume to toggle mute, or the clock to open Calendar.

- **NET:** active connection type (Wi-Fi, LAN, or VPN), or Offline when there is
  no default route. Refreshes every 10 seconds; click to open Network settings.
  This reports the local connection, not an external internet connectivity test.
- **SLACK:** mirrors the running Slack app's Dock badge, showing a count or an
  unread dot. Hides when the badge clears or Slack is closed; refreshes every
  five seconds and when switching apps. Click to open Slack. Requires Slack's
  app-icon badge to be enabled, but no Slack API credentials. The count follows
  Slack's notification settings rather than counting every unread message.
- **TS:** Tailscale connection status, with Exit when using an online exit node.
  Refreshes every 15 seconds; click to open Tailscale. Uses the installed app's
  CLI, so no second Tailscale installation is needed.
- **OUT:** current audio output. Click to choose an available device; the current
  output is marked with a check. Refreshes every 15 seconds and on volume changes.
- **BREW:** number of outdated formulae and casks. Checks hourly and when clicked;
  click to see package names and available versions. Uses Homebrew's local index,
  refreshed by `brew update`, and never installs upgrades automatically.

The center music item uses `media-control` to read macOS Now Playing from apps
such as Music, Spotify, and supported browsers. It shows the title and artist,
refreshes every five seconds, and toggles play/pause when clicked. It hides when
no track metadata is available; apps playing audio without publishing Now Playing
information cannot provide track titles.

Dinky's workspace, focus, startup and display hooks update the bar. A 30-second
fallback refresh handles Dinky being stopped or relaunched. Keep **Displays
have separate Spaces** enabled, and set the native menu bar to automatically
hide so it can be revealed at the screen edge without overlapping SketchyBar.
The Dinky config reserves 56 points at the top for the 36-point floating bar.
On notched laptop displays, the bar fits in the 24-point strip beside the
camera housing. Two rounded Catppuccin panels span the left and right sides,
with a transparent 220-point gap around the notch. Workspaces and the active app stay on the left; shorter Now
Playing text and status items stay on the right. The name label, date/time,
volume, and audio-output widgets appear only on external displays, where the
full-width 36-point floating panel and centered Now Playing item remain available. Display
associations refresh automatically when docking or undocking. Dinky uses a
10-point top gap on the built-in screen to reclaim the space below the notch.

Reload changes with `sketchybar --reload`. Stop it with
`brew services stop sketchybar`; if keeping Dinky without the bar, set
`gaps.outer` back to `10` in `dinky/.config/dinky/dinky.toml`.

## macOS preferences

Hide desktop icons independently of the Desktop & Dock checkbox:

```sh
./scripts/macos-defaults.sh
```

This restarts Finder; files remain accessible in `~/Desktop`.
`bootstrap.darwin.sh` also applies this preference. `bootstrap.sh` only links
configs and does not apply system preferences.

To show icons again:

```sh
defaults write com.apple.finder CreateDesktop -bool true
killall Finder
```

## Coding CLIs

Codex and Claude Code use native binaries managed by the global mise config
in `tools/.config/mise/config.toml`. After linking the `tools` package, install
and update them with:

```sh
mise install codex claude
mise upgrade codex claude
```

Claude's background updater is disabled in `claude/.claude/settings.json` so
mise owns its version. Use mise for updates and avoid additional npm, pnpm,
Homebrew, or standalone installations of these CLIs.

## Groovenet CLI

The Stow-managed global mise config manages `@groovenet/cli` and
`@groovenet/player` with `latest`, making them available outside this dotfiles
checkout and independently of Node's global npm packages. Link it with
`./bootstrap.sh --apply --packages tools`; no root `mise.toml` is needed.
Its package-specific `allow_low_downloads` option permits installation despite
the CLI's low npm download count.

```sh
mise install npm:@groovenet/cli npm:@groovenet/player
groovenet --version
mise upgrade npm:@groovenet/cli npm:@groovenet/player
```

For an explicit version pin, change the entry in `tools/.config/mise/config.toml`
and commit it. Avoid also installing these tools with `npm install -g`.

## Townhaus archive mount (macOS)

The optional `smb-archive` Stow package checks Beelink's LAN address
`192.168.2.151`, then its Tailscale address `100.117.118.15`, on SMB port 445
at login and every two minutes. It mounts the first reachable address as the
`archive` share. Connect once in Finder and choose to save the `saegey` SMB
password in Keychain; the LaunchAgent can then reconnect without storing a
password in dotfiles. The first mount may prompt for credentials.

Install and load it with:

```sh
./bootstrap.sh --apply --packages smb-archive
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.saegey.townhaus-archive.plist"
```

The agent is reloaded automatically at the next login. To stop it, run
`launchctl bootout "gui/$(id -u)/com.saegey.townhaus-archive"`. iOS Files does not
automatically mount SMB shares from dotfiles; connect to
`smb://192.168.2.151/archive` at home or `smb://100.117.118.15/archive` over
Tailscale from **Browse → … → Connect to Server**, then save the server in Files.

On Omarchy, keep its `~/.bashrc`, Ghostty config, and other existing configurations unless you intentionally migrate them. In particular, do **not** Stow `bash` or `ghostty` over Omarchy's files. If staying on Bash, integrate `atuin init bash` into the existing `~/.bashrc` rather than replacing it. For Zsh, install it separately, link the `zsh` package, test with `zsh`, then optionally change the login shell. Git and SSH packages require review of local credentials and agents before opting in.

The shared SSH config uses `~/.1password/agent.sock` for Home Assistant (`homeassistant` / `192.168.2.91`) when no forwarded agent is active. `~/.ssh/config.local` is included at top level before the shared hosts, so its conditional forwarded-agent rule can select an active forwarded agent for remote sessions. Linux 1Password uses this socket path directly. On macOS, create the standard-path symlink once after enabling the 1Password SSH Agent:

```sh
mkdir -p ~/.1password
ln -s "$HOME/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock" ~/.1password/agent.sock
```

If `~/.1password/agent.sock` already exists, check it with `ls -l` before creating or changing it. The 1Password agent may ask you to authorize SSH clients on the machine running the command; its authorization settings control how often it asks. Forward the agent only to trusted hosts. The machine-local config can prefer a live forwarded agent for Home Assistant while retaining the local socket as a fallback.

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

## Herdr

After installing Herdr, link its configuration and task picker explicitly:

```sh
./bootstrap.sh --apply --packages herdr
```

Command+1–9 switches tabs. Control+Option+1–9 switches workspaces, and
Control+Option+J/K focuses the next/previous agent in the sidebar.
Command+[ hides or shows the Spaces and Agents sidebar completely.

Herdr's `cmd+p` shortcut opens `herdr-repo-tasks`, which uses jq and fzf
to select repository tasks. Machine-specific task definitions live in
`~/.config/herdr/repo-scripts.json`; otherwise it discovers Makefile targets and
npm scripts.

Run `herdr-wt-done` inside a linked worktree (or choose **Done (teardown
worktree)** from configured repository tasks) to remove it and close its Herdr
workspace. It uses that repository's executable `scripts/worktree-rm.sh`, falling
back to the same repository's main checkout for older worktrees. Repositories
without this script use Herdr's native removal, which refuses dirty worktrees;
the helper also refuses commits ahead of an upstream when one is configured.
Before removing either kind of worktree, it removes that checkout's Docker
Compose containers, volumes, and networks using their Compose labels. It leaves
other checkouts' stacks alone and refuses shared Compose projects or Docker
failures, even with `--force`, so a failed teardown keeps the worktree available.
`--force` overrides dirty-worktree and unpushed-commit checks. Main checkouts and mismatched workspace paths
are refused.

Install the Herdr command palette plugin after installing Herdr and the Brewfile
dependencies (Rust/Cargo is required to build it):

```sh
herdr plugin install ramarivera/herdr-palette
```

`prefix+space` opens the palette. Update it with
`herdr plugin update ramarivera.palette`.

Install the fuzzy tab, agent, workspace, and branch switcher with
`herdr plugin install jeffarese/herdr-bar`, then run
`herdr server reload-config`. Command+K opens it; `prefix+alt+k` is the fallback.
Ghostty translates Command+K to Ctrl+Alt+Shift+K for Herdr. Reload Ghostty's configuration after
linking this setting. The plugin automatically titles unnamed agent tabs;
start its watcher in an existing session with
`herdr plugin action invoke herdr-bar.start-titles`.

The Zsh `workon <TICKET-ID>` and `review <TICKET-ID>` helpers run inside Herdr.
They create and focus a worktree workspace, then start Claude in its root pane.
`workon` uses `${BRANCH_PREFIX:-adam}/<TICKET-ID>` and asks for an implementation
plan; `review` finds the ticket's PR with `gh`, fetches its branch, and runs
Claude Opus with `/pr-review <PR-number>`. Both require `herdr` and `jq`;
`review` also requires authenticated GitHub CLI access.

## PR review dashboard

In Herdr, **Command+Shift+R** (or `herdr-review`) opens the persistent review
workspace. The dashboard uses the `adam-skysafe` GitHub login and shows SkySafe
PRs across repositories: reviews requested, previously reviewed PRs, changes
requested on your PRs, failing CI, approved PRs with passing CI, and all your open
PRs. Queues refresh every two minutes; use gh-dash's refresh keys for an immediate
update.

The **Previously Reviewed** queue keeps open PRs you reviewed visible even when
the author hasn't requested another review. It sorts by latest update; updates
can include comments and other activity, so this isn't an exact list of PRs
with new commits since your review.

Press **w** on a PR to open its worktree in Herdr. An existing workspace is
focused, a parked checkout is reopened, and a missing checkout is created from
the PR's fetched head. Existing local branches and dirty files are preserved;
a differing local HEAD is reported. Fork PRs use `review/pr-<number>` branches
to avoid confusing them with local branches of the same name. No agents or
repository setup scripts are started automatically.

Local repositories are found under `~/Projects/<repo>` or
`~/Projects/<owner>/<repo>` and verified against their origin remote. Override
the root with `HERDR_PROJECTS_DIR`, or invoke
`herdr-pr-open --repo OWNER/REPO --pr NUMBER --repo-path PATH` manually.
`--dry-run` prints the plan without changing worktrees; `--no-focus` keeps focus.
New checkouts live under `~/.herdr/worktrees/<owner>/<repo>/pr-<number>`.

Press **Ctrl+R** on a PR to open its checkout and start Claude Opus in a dedicated
review tab with `/pr-review <PR number>`—the same workflow as the `review SKY-…`
shell helper. A review agent is remembered per repository/PR: subsequent presses
reuse it, and a busy or blocked session is focused without sending another
prompt. Existing terminals and agents are left alone. **R** keeps gh-dash's
normal refresh behavior. The command-line equivalent is
`herdr-pr-open --repo OWNER/REPO --pr NUMBER --review`.

```sh
./bootstrap.sh --apply --packages herdr gh-dash
herdr plugin link "$HOME/.config/herdr/plugins/review"
herdr server reload-config
herdr-review
```

Reload Ghostty's configuration to release Command+Shift+R. The review workspace
is remembered by metadata, so renaming it (for example, to **Dashboard**) keeps
the shortcut working. It remains open while its dashboard/shell is running.
Close inactive task workspaces to keep herdr-bar focused on active work; their
checkouts remain available to reopen. `herdr-wt-done` is for final teardown and
also removes stack resources. The general `gh dash` configuration is unchanged;
this work queue uses the separate `~/.config/gh-dash/review.yml` configuration.
Both dashboards use the shared Catppuccin Mocha palette with mauve accents.

## Dev stack status

The read-only monitor counts localdev Compose projects by their container
labels and checkout paths. Link both packages and register the local plugin:

```sh
./bootstrap.sh --apply --packages herdr sketchybar
herdr plugin link "$HOME/.config/herdr/plugins/dev-stack-status"
herdr server reload-config
dev-stack-status --herdr
sketchybar --reload
```

Herdr's workspace rows show the running container count as `[17]`, `[0]` for
a checkout with no running containers, or `[?]` when Docker is unavailable.
Badges refresh on workspace/worktree events and Herdr startup. Use
`prefix+alt+d` to refresh immediately after a stack changes without switching
workspaces. Unrelated repositories get no badge.

A yellow `[R]` badge marks worktrees whose current branch is neither `main` nor
prefixed with `adam/`. The Linear titles plugin refreshes this badge alongside ticket titles;
`prefix+alt+l` refreshes it manually. Detached or unreadable branches are unmarked.

SketchyBar's **STACKS** item polls every ten seconds and counts projects with
at least one running container, including stacks outside open Herdr workspaces.
Click it for each project's running/total count. Docker being unavailable shows
`?`, rather than a misleading zero. Only the current Docker context is queried.
One-off Compose jobs are excluded. Counts describe existing containers, not an
HTTP readiness check or an expected service count from Compose YAML; host Vite
processes started by `make dev` are not included.

No containers or volumes are started, stopped, removed, or pruned. Python 3,
Docker CLI, and jq (for SketchyBar) are required. `dev-stack-status --json`
prints the same status from any terminal.

## Linear workspace titles

Herdr can show each ticket's Linear title beneath the workspace name. Install
and authenticate the `linear` CLI, then link and register the local plugin:

```sh
./bootstrap.sh --apply --packages herdr
herdr plugin link "$HOME/.config/herdr/plugins/linear-titles"
herdr server reload-config
herdr-linear-titles
```

The lookup checks the Git branch first, then the checkout directory name and
workspace label, recognizing IDs such as `adam/SKY-6712`, `adam-sky-6712`, and
`sky-6712-description`. Names without an ID get no title. Ticket lookups use
the worktree's Linear configuration and credentials, without loading `.env`.
Neither worktree names nor Linear issues are changed.

Titles refresh on workspace/worktree events and Herdr startup. Successful
lookups are cached for five minutes; failures retry after a minute and keep
the last known title. Press `prefix+alt+l` (or run `herdr-linear-titles --force`)
to bypass the cache. The cache contains titles only under
`~/.cache/herdr-linear-titles` (or `$XDG_CACHE_HOME/herdr-linear-titles`), scoped
by repository and ticket ID. DEV badges appear beside the workspace name,
with the Linear title underneath, keeping each entry to two rows.

## Worktree visor

Press `cmd+i` to open a popup for the focused pane's Git worktree, with
the workspace checkout as a fallback. It shows the Linear ticket's title,
status and description; the matching branch PR and review/check status;
GitHub Actions for the checkout's current commit; and dev-stack container status.

```sh
./bootstrap.sh --apply --packages herdr
herdr plugin link "$HOME/.config/herdr/plugins/worktree-visor"
herdr server reload-config
```

App links come from allowlisted URL and port values in `docker/localdev/.env`
and the matching generated Caddy route under `~/.skysafe/proxy/conf.d` (or
`$SKYSAFE_CADDY_CONFD`). This includes the `.app.localhost` URL, API URL, and
configured OrbStack/direct address when present. Files are parsed as data;
setup scripts and `.env` files are never executed. A configured URL is not a
promise that its stack or Caddy is currently running.

Use Up/Down (or j/k) to select links, Enter to open them, Page Up/Down to scroll,
`r` to refresh, and Escape or `q` to close. The popup refreshes every 15 seconds
while open. It uses the existing `linear` and `gh` logins and is read-only.
Unpushed commits may have no Actions runs; PR-head checks are labeled separately
when the remote PR head differs from the local checkout.

For a noninteractive snapshot, run
`herdr-worktree-visor --json --cwd /path/to/worktree`. Python 3 with curses,
GitHub CLI, Linear CLI, and the `dev-stack-status` helper are required.

## Local overrides

Machine-specific config that shouldn't be committed goes in:
- `~/.zshrc.local` — sourced at the end of `.zshrc`
- `~/.gitconfig.local` — included at the end of `.gitconfig`; set `commit.gpgsign = true` and `gpg.ssh.program` to the OS-specific signer only where available
- `~/.ssh/config.local` — included before shared host entries; put machine-specific SSH settings and optional OrbStack/Colima includes there. Conditional `Match` rules can select a forwarded agent when one is available.
- `~/.bashrc.local` — sourced by the shared Bash config

GitHub account selection also belongs in `~/.ssh/config.local`. Set
`IdentityAgent` to the machine's 1Password socket, with `IdentitiesOnly yes`
and an `IdentityFile` pointing to the desired public key. Use `Host github.com`
for the default account and a separate alias such as `github-saegey`
(`HostName github.com`, `User git`) for personal repositories. Repositories
whose remotes use that alias need the corresponding local host entry.

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
