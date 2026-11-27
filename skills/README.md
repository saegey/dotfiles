# Agent skills

Keep manually maintained skills here, with one source per skill:

| Folder | Installed for | Skills |
| --- | --- | --- |
| `shared/` | Codex and Claude Code | `send-email`, `supacode-cli`, `supacode-deeplinks` |
| `codex/` | Codex | `herdr`, `pr-description` |
| `claude/` | Claude Code | Add Claude-specific skills here when needed |

Run from the checkout:

```sh
./scripts/setup-agent-skills
./scripts/setup-agent-skills --apply
```

The installer links each skill into `~/.codex/skills/` and/or
`~/.claude/skills/`. It respects `CODEX_HOME` and `CLAUDE_CONFIG_DIR`.
It backs up identical installed copies under
`~/.local/state/dotfiles/skill-backups/` before replacing them with links.
Different existing skills cause an error before any links are changed.
Agent-managed system skills, plugins, and Claude's `synced/` folder stay
managed by their original tools. A skill name must be unique per agent.

Add a directory containing `SKILL.md` to the appropriate folder and rerun
the installer. Edit the files here to update both agents together. Codex
can discover newly installed skills on the next turn; start a new Claude
Code session after installation.

## Matcha email

`shared/send-email/` is the unmodified official skill from
[`floatpane/matcha`](https://github.com/floatpane/matcha/tree/3e7e79beb07c7f28fe145b34bee826ede080656c/SKILLS/send-email),
at commit `3e7e79beb07c7f28fe145b34bee826ede080656c`.
It uses `matcha send` with local configured accounts and supports Markdown,
CC/BCC, attachments, and sender selection. It instructs the agent to show
the send command for confirmation before execution. No account credentials
or OAuth tokens belong in this directory.

Examples: ask Codex to use `$send-email`, or use `/send-email` in Claude Code.
Installing the skill does not send a message.
