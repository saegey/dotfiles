# Keyboard workflow plan

Work through these items one at a time. Record decisions here before changing
bindings, and keep the shortcut visor in sync as each change is implemented.
Existing uncommitted visor, repo-task shortcut, and OrbStack changes are separate
work already in progress.

## 1. Dedicated spaces and display layouts

- [x] Keep the same app assignments and side-by-side layouts on laptop and external displays.
- [x] Use Command+Option+F to toggle the focused window filling the workspace,
      then restore the tiled layout. This is already bound in Dinky.
- [x] Spaces 1–4 prefer the LG HDR 4K external display, then the built-in display,
      then the main display. Dinky migrates assigned workspaces when displays change.
- [x] Rules route new normal windows only, leaving dialogs and panels alone.
      Existing windows are not continuously forced back, allowing occasional
      manual placement. Moved the existing Secretive window to space 4.
- [x] Implement app placement and layouts; validate with Dinky doctor and reload.
- [ ] Verify a physical unplug/reconnect cycle and laptop-only arrangement.

Spaces 1, 2, and 4 use Dinky's master layout with a 50/50 split: a single window
fills the area, the second sits beside it, and additional windows stack on the
other side. Space 3 keeps its existing tiling layout. No display-specific layout
override is used. New normal windows are routed by their installed bundle IDs.
Existing unrelated windows are left where they were; for example, Messages
currently shares space 4 and an existing Ghostty window remains on space 7.

Requested starting assignments:

| Space | Apps | Layout intent |
| --- | --- | --- |
| 1 | Ghostty | Fill the available area alone; allow another window beside it occasionally. |
| 2 | Linear and Chrome | Side by side on both laptop and external displays; Command+Option+F temporarily expands either app. |
| 3 | Slack | Dedicated communication space. |
| 4 | 1Password and Secretive | Dedicated credentials/tools space. |

Keep OrbStack's UI floating; use Lazydocker for routine container management.
Do not assume a display's native macOS Space numbers stay stable when docking.

## 2. Caps Lock as a Hyper key

- [x] Held Caps Lock = Hyper (Control+Option+Shift+Command), active with the next key.
- [x] Tapped Caps Lock = Escape (250 ms tap timeout).
- [x] Checked existing setup: Karabiner and its user config were absent.
- [x] Add the configuration to dotfiles, Brewfile, and bootstrap package allowlist.
- [x] Link the Karabiner configuration into `~/.config/karabiner/karabiner.json`.
- [x] Install Karabiner and finish first-run macOS permissions (user completed).
      Verified installation, linked config, and selected Dotfiles profile.
- [ ] Verify taps and Hyper chords on built-in and external keyboards.

Activation blocker (2026-10-22): background services and input permissions are
working, but macOS denies the driver with OSSystemExtensionErrorDomain code 10.
The sysextd log explicitly says its team ID and identifier are not in the allowed
extensions list. This rejection immediately removes the pending extension, which
explains why it never appears in Driver Extensions. Request approval from whoever
manages the system-extension policy for team `G43BCU2T37`, bundle
`org.pqrs.Karabiner-DriverKit-VirtualHIDDevice`, then retry activation. The profile
remains available if driver approval is obtained. Its Caps Lock rule is disabled
while the Hammerspoon fallback is active, to avoid double remapping.

- [x] Implement and activate the driver-free Hammerspoon fallback: hidutil maps
      Caps Lock to F18; Hammerspoon handles Escape taps and Hyper key chords.
      Preserve unrelated remaps and restore Caps Lock on normal quit/reload.
- [x] Validate tap/chord behavior, release order, ordinary typing, long holds,
      and mouse cancellation without sending keyboard input; verify live event tap.
- [x] User confirmed the Hammerspoon Caps Lock mapping is working (2026-10-22).
      Testing both built-in and external keyboards separately remains pending.
      Secure Input may block interception in password fields.

## 3. Direct app shortcuts

- [x] Hyper+T = Ghostty, B = Chrome, L = Linear, S = Slack,
      P = 1Password, K = Secretive (user approved).
- [x] Focus the app's existing window or launch it if closed. Dinky follows app
      activation and routes new normal windows to their assigned spaces; existing
      manually moved windows stay on their current space.
- [x] Implement in Hammerspoon using all four modifiers, preserving normal app
      commands. Generate the app shortcut overlay entries from the binding table.
- [ ] Verify physical Caps Lock chords on built-in and external keyboards.

## 4. Hammerspoon shortcut visor

- [x] Expand the existing Command+Option+/ shortcut overlay into a reference for
      app launching, spaces, window management, and Herdr.
- [x] Keep Command+Option+/ to toggle; Escape dismisses. No auto-dismiss timer.
- [x] Show modifier symbols, grouped commands, two columns, and an adaptive font
      capped at 14pt. Use a canvas centered inside the usable screen frame;
      recalculate an open visor on display changes so it fits the laptop screen.
- [x] Reflect current app, Dinky, and Herdr bindings; app entries come from the
      binding table. Keep the Herdr reference in sync when those keys change.

An existing Catppuccin overlay is in `hammerspoon/.hammerspoon/init.lua`;
extend it rather than introducing a second competing shortcut list.

## 5. Herdr splits and navigation

- [x] Replace the need to use Control+B for common split actions with direct
      Command shortcuts.
- [x] Command+D splits right; Command+Shift+D splits down.
- [ ] Decide whether split left/up also need direct bindings.
- [ ] Review pane focus, resizing, and closing shortcuts alongside splits.
- [x] Command+Option+Arrow keys focus the pane in that direction. Retain
      Control+B then H/J/K/L as alternatives; unbind Ghostty interception and
      document the direct shortcuts in the visor.
- [x] Unbind Ghostty's Command+D and Command+Shift+D shortcuts so Herdr receives them.
- [x] Update the shortcut visor; validate and reload Herdr, Ghostty, and Hammerspoon.
- [ ] Verify the physical split shortcuts in daily use.

Already configured: Command+I for worktree visor, Command+P for repo tasks,
Command+[ for sidebar, Command+T for a tab, and Command+1–9 for tabs.

## 6. Central PR review queue

- [x] Persistent gh-dash workspace for work PRs across SkySafe repositories.
- [x] Separate review config, work-account check, two-minute refresh, and queues
      for requested reviews, changes requested, failing CI, approved/passing PRs,
      and all authored open PRs.
- [x] W opens/reuses the selected PR's worktree; preserve existing local work,
      avoid switching the main checkout, and isolate fork branch names.
- [x] Ctrl+R starts/reuses a dedicated Claude Opus review session with
      `/pr-review <PR number>`; R remains the dashboard refresh binding.
- [x] Command+Shift+R opens the dashboard; remember the workspace with metadata
      so the user can keep its preferred name, Dashboard.
- [x] Live dashboard queries and reopening an existing parked checkout verified.
- [ ] Try the W action in daily use across other repositories and fork PRs.

## Working approach

Implement one agreed item at a time, try it in daily use, then refine it.
Favor consistent shortcuts across laptop and external displays. Keep the mouse
available as a fallback while learning, and avoid changing unrelated bindings.
