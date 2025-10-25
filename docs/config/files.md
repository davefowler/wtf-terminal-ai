# Configuration

`wtf` has several things you can configure and customize. The point isn't to memorize commands - it's to know what's configurable so you can ask `wtf` to change it naturally.

## What Can You Configure?

Here are the main things you can control in `wtf`:

### Memories

What your preferences are. Things like "I use vim" or "I prefer npm over yarn".

**Why it matters:** `wtf` remembers these and uses them when suggesting commands.

**How to use:**
```bash
$ wtf remember I use emacs for editing
$ wtf remember I prefer pytest over unittest
$ wtf forget about my editor preference
$ wtf show me what you remember
```

**Stored in:** `~/.config/wtf/memories.json`

[Learn more about Memories →](../properties/memories.md)

---

### Allowed Commands

Which commands can run automatically without asking for permission.

**Why it matters:** Safe commands (like `git status`) run instantly. Dangerous ones (like `rm -rf`) require approval. You control which is which.

**How to use:**
```bash
$ wtf always allow "npm install"
$ wtf never allow "rm -rf"
$ wtf show me what commands are allowed
```

**Stored in:** `~/.config/wtf/allowlist.json`

[Learn more about Allowlist →](allowlist.md)

---

### Personality

How `wtf` talks to you - sarcastic, helpful, brief, verbose, etc.

**Why it matters:** Some people want dry wit. Some want encouragement. Some just want the command with no commentary.

**How to use:**
```bash
$ wtf be more helpful and less sarcastic
$ wtf be really brief, just give me commands
$ wtf go back to your normal personality
```

**Stored in:** `~/.config/wtf/wtf.md` (custom instructions file)

[Learn more about Personality →](../properties/personality.md)

---

### Hooks

Shell integration that captures commands better and can auto-run `wtf` after errors.

**Why it matters:** With hooks, `wtf` automatically runs when a command fails. No need to remember to type it.

**How to use:**
```bash
$ wtf --setup-error-hook
$ wtf --setup-not-found-hook
$ wtf --remove-hooks
```

**Stored in:** Your shell config (`~/.zshrc`, `~/.bashrc`, etc.)

[Learn more about Hooks →](../properties/hooks.md)

---

### Keys

API keys for AI providers (Anthropic, OpenAI, Google).

**Why it matters:** You need at least one API key for `wtf` to work.

**How to use:**
```bash
$ wtf --setup              # Run setup wizard to change provider/model
$ wtf --config             # Show current config location
```

Or manage via the `llm` library:
```bash
$ llm keys set anthropic   # Set API key
$ llm models               # List available models
```

**Stored in:** `~/.config/wtf/config.json` and `~/.config/io.datasette.llm/keys.json`

[Learn more about API Keys →](api-keys.md)

---

### Setup

Initial configuration - provider, model, basic settings.

**Why it matters:** This is the first thing that runs and sets everything up.

**How to use:**
```bash
$ wtf --setup              # Run setup wizard
$ wtf --reset              # Delete all config (requires confirmation)
```

**Stored in:** `~/.config/wtf/config.json`

[Learn more about Setup →](../setup.md)

---

## The Point

You don't need to memorize commands. Just know what's configurable:

- **Memories** - Your preferences (`wtf remember I use vim`)
- **Allowed Commands** - What runs automatically (`wtf always allow git status`)
- **Personality** - How it talks (`wtf be more encouraging`)
- **Hooks** - Shell integration (`wtf --setup-error-hook`)
- **Keys** - Which AI to use (`wtf --setup`)
- **Setup** - Initial configuration (`wtf --setup`, `wtf --reset`)

Most things can be changed naturally by just asking:

```bash
$ wtf "change my personality to be more encouraging"
$ wtf "show me what you remember about me"
```

System actions use CLI flags:

```bash
$ wtf --setup              # Setup wizard
$ wtf --config             # Show config location
$ wtf --setup-error-hook   # Install hooks
```

## Configuration Files

All config lives in `~/.config/wtf/`:

```
~/.config/wtf/
├── config.json          # Main config (provider, model, settings)
├── memories.json        # Your preferences
├── allowlist.json       # Auto-allowed commands
├── wtf.md               # Custom personality/instructions
└── history.jsonl        # Conversation history
```

## Editing Directly

Want to edit config files manually? Go ahead:

```bash
$ vim ~/.config/wtf/config.json
$ vim ~/.config/wtf/wtf.md
$ code ~/.config/wtf/memories.json
```

`wtf` picks up changes automatically. No restart needed.

## CLI Reference

For all CLI flags and options, see:

- [CLI Options Reference](../reference/cli-options.md) - Complete flag documentation

## Next Steps

- [Memories](../properties/memories.md) - Teach `wtf` your workflow
- [Hooks](../properties/hooks.md) - Shell integration
- [API Keys](api-keys.md) - Switch providers or models

