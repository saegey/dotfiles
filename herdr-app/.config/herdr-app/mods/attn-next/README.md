Attn next by iml885203 (MIT), vendored unchanged from commit 9f272dd:
https://github.com/iml885203/herdr-mods/tree/9f272dd/attn-next

Tap Cmd-Shift-J to focus the next agent needing attention. Hold Cmd-Shift and
tap J/K to move down/up in the popup; release Cmd to jump. Esc cancels.
Blocked agents come first, then done, working and idle. Without blocked/done
agents, it follows Herdr's agent order. Uses macOS osascript to read modifier
flags for quick taps; no network or file access.
