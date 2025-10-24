# Configuration

`wtf` has several things you can configure and customize. The point isn't to memorize commands - it's to know what's configurable so you can ask `wtf` to change it naturally.

## What Can You Configure?

Here are the main things you can control in `wtf`:

### Memories

What your preferences are. Things like "I use vim" or "I prefer npm over yarn".

**Why it matters:** `wtf` remembers these and uses them when suggesting commands.

**Change it naturally:**
```bash
$ wtf remember I use emacs for editing
$ wtf remember I prefer pytest over unittest
$ wtf forget about my editor preference
$ wtf show me what you remember
```

**CLI equivalent:**
```bash
$ wtf memories add "editor: emacs"
$ wtf memories list
$ wtf memories delete editor
```

**Stored in:** `~/.config/wtf/memories.json`

[Learn more about Memories →](../features/memories.md)

---

### Allowed Commands

Which commands can run automatically without asking for permission.

**Why it matters:** Safe commands (like `git status`) run instantly. Dangerous ones (like `rm -rf`) require approval. You control which is which.

**Change it naturally:**
```bash
$ wtf always allow "npm install"
$ wtf never allow "rm -rf"
$ wtf show me what commands are allowed
$ wtf remove "npm install" from the allowlist
```

**CLI equivalent:**
```bash
$ wtf allowlist add "npm install"
$ wtf allowlist remove "npm install"
$ wtf allowlist show
```

**Stored in:** `~/.config/wtf/allowlist.json`

[Learn more about Allowed Commands →](allowlist.md)

---

### Personality

How `wtf` talks to you - sarcastic, helpful, brief, verbose, etc.

**Why it matters:** Some people want dry wit. Some want encouragement. Some just want the command with no commentary.

**Change it naturally:**
```bash
$ wtf be more helpful and less sarcastic
$ wtf be really brief, just give me commands
$ wtf go back to your normal personality
$ wtf what personality are you using?
```

**CLI equivalent:**
```bash
$ wtf personality set helpful
$ wtf personality set sarcastic
$ wtf personality reset
```

**Stored in:** `~/.config/wtf/personality.txt`

[Learn more about Personality →](../features/personality.md)

---

### Hooks

Shell integration that captures commands better and can auto-run `wtf` after errors.

**Why it matters:** With hooks, `wtf` automatically runs when a command fails. No need to remember to type it.

**Change it naturally:**
```bash
$ wtf install shell hooks
$ wtf remove shell hooks
$ wtf are hooks installed?
```

**CLI equivalent:**
```bash
$ wtf hooks install
$ wtf hooks uninstall
$ wtf hooks status
```

**Stored in:** Your shell config (`~/.zshrc`, `~/.bashrc`, etc.)

[Learn more about Hooks →](../features/hooks.md)

---

### Keys

API keys for AI providers (Anthropic, OpenAI, Google).

**Why it matters:** You need at least one API key for `wtf` to work.

**Change it naturally:**
```bash
$ wtf switch to using OpenAI
$ wtf use gpt-4 as my default model
$ wtf show me what API key I'm using
```

**CLI equivalent:**
```bash
$ wtf config set provider openai
$ wtf config set model gpt-4
$ wtf config show
```

**Stored in:** System keychain (macOS/Linux) or `~/.config/wtf/config.yaml`

[Learn more about API Keys →](api-keys.md)

---

### Setup

Initial configuration - provider, model, basic settings.

**Why it matters:** This is the first thing that runs and sets everything up.

**Change it naturally:**
```bash
$ wtf reconfigure everything
$ wtf change my AI provider
$ wtf reset to default settings
```

**CLI equivalent:**
```bash
$ wtf --setup
$ wtf config reset
```

**Stored in:** `~/.config/wtf/config.yaml`

[Learn more about Setup →](../setup.md)

---

### Custom Instructions

Additional instructions that apply to every request (like "always prefer Python over JavaScript").

**Why it matters:** If you have project-specific or personal preferences, these apply universally.

**Change it naturally:**
```bash
$ wtf always suggest Python solutions
$ wtf remember I work on microservices, suggest Docker when relevant
$ wtf show me my custom instructions
$ wtf remove that Python instruction
```

**CLI equivalent:**
```bash
$ wtf instructions add "Prefer Python solutions"
$ wtf instructions list
$ wtf instructions remove 1
```

**Stored in:** `~/.config/wtf/instructions.txt`

[Learn more about Custom Instructions →](custom-instructions.md)

---

## The Point

You don't need to memorize any of these commands. Just know what's configurable:

- **Memories** - Your preferences
- **Allowed Commands** - What runs automatically
- **Personality** - How it talks
- **Hooks** - Shell integration
- **Keys** - Which AI to use
- **Setup** - Initial configuration
- **Custom Instructions** - Universal rules

Then just ask `wtf` to change them naturally:

```bash
$ wtf "change my personality to be more encouraging"
$ wtf "show me what you remember about me"
$ wtf "let npm install run automatically"
```

The CLI commands exist for scripting and advanced users. But you can ignore them completely.

## Configuration Files

All config lives in `~/.config/wtf/`:

```
~/.config/wtf/
├── config.yaml          # Main config (provider, model, settings)
├── memories.json        # Your preferences
├── allowlist.json       # Auto-allowed commands
├── personality.txt      # Custom personality instructions
├── instructions.txt     # Custom universal instructions
└── conversation.jsonl   # Conversation history
```

## Editing Directly

Want to edit config files manually? Go ahead:

```bash
$ vim ~/.config/wtf/config.yaml
$ code ~/.config/wtf/memories.json
```

`wtf` picks up changes automatically. No restart needed.

## Next Steps

- [Memories](../features/memories.md) - Teach `wtf` your workflow
- [Permissions](../features/permissions.md) - Fine-tune auto-execution
- [API Keys](api-keys.md) - Switch providers or models

