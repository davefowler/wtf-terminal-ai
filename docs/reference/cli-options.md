# CLI Options Reference

Complete list of all `wtf` command-line flags and options.

## Quick Reference

```bash
wtf [OPTIONS] [QUERY]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--version` | `-v` | Show version number |
| `--config` | | Show config file location |
| `--setup` | | Run setup wizard |
| `--reset` | | Reset all configuration |
| `--model MODEL` | | Override AI model for this query |
| `--verbose` | | Show diagnostic information |
| `--setup-error-hook` | | Install error hook in shell |
| `--setup-not-found-hook` | | Install command-not-found hook |
| `--remove-hooks` | | Remove all shell hooks |

---

## General Options

### `--help`, `-h`

Show help message and exit.

```bash
$ wtf --help
```

Displays usage information, available flags, and examples.

### `--version`, `-v`

Show version number and exit.

```bash
$ wtf --version
wtf 0.1.0
```

### `--config`

Show configuration file location.

```bash
$ wtf --config

Configuration:
  Config directory: ~/.config/wtf/
  Config file: ~/.config/wtf/config.json

To edit, open the file in your editor or run:
  $EDITOR ~/.config/wtf/config.json
```

Useful for finding where your config is stored or checking if config exists.

---

## Setup Options

### `--setup`

Run the setup wizard.

```bash
$ wtf --setup
```

Walks you through:
1. Choosing an AI provider (Anthropic, OpenAI, Google)
2. Entering your API key
3. Selecting a default model

Use this to:
- Configure wtf for the first time
- Switch AI providers
- Update your API key

### `--reset`

Reset all configuration to defaults.

```bash
$ wtf --reset

⚠ Warning: This will delete ALL wtf configuration

This includes:
  • API keys and model settings
  • Memories (learned preferences)
  • Conversation history
  • Allowlist/denylist

Are you sure? [y/N]
```

**This is destructive!** It deletes:
- API keys and model configuration
- All memories
- Conversation history
- Allowlist and denylist
- Custom instructions

After reset, run `wtf --setup` to reconfigure.

---

## Query Options

### `--model MODEL`

Override the default AI model for this query only.

```bash
# Use GPT-4 for this query (if you have OpenAI configured)
$ wtf --model gpt-4 "explain quantum computing"

# Use Claude Opus for a complex task
$ wtf --model claude-3-opus "refactor this code..."

# Use a faster model for simple queries
$ wtf --model claude-3-haiku "what's my git status?"
```

The model must be:
- From your configured provider
- Available via the `llm` library
- A valid model ID

**Examples:**
- Anthropic: `claude-3.5-sonnet`, `claude-3-opus`, `claude-3-haiku`
- OpenAI: `gpt-4o`, `gpt-4`, `gpt-3.5-turbo`
- Google: `gemini-pro`, `gemini-flash`

### `--verbose`

Show diagnostic information during execution.

```bash
$ wtf --verbose "what's my git status?"

[DEBUG] Using model: claude-3.5-sonnet
[DEBUG] Context gathered: 150 chars
[DEBUG] Calling tool: git_status
[DEBUG] Tool result: 45 chars
...
```

Useful for:
- Debugging issues
- Understanding what wtf is doing
- Reporting bugs

Sets `WTF_DEBUG=1` environment variable internally.

---

## Hook Options

### `--setup-error-hook`

Install error hook in your shell.

```bash
$ wtf --setup-error-hook

✓ Error hook installed for zsh
  Restart your shell or run: source ~/.zshrc
```

After installation, failed commands show:

```bash
$ npm run biuld
npm error Missing script: "biuld"

💥 Command failed with exit code 1
   Run 'wtf' to analyze what went wrong
```

**Supported shells:** zsh, bash, fish

[Learn more about hooks →](../properties/hooks.md)

### `--setup-not-found-hook`

Install command-not-found hook in your shell.

```bash
$ wtf --setup-not-found-hook

✓ Command-not-found hook installed for zsh
  Restart your shell or run: source ~/.zshrc
```

After installation, mistyped commands show:

```bash
$ gti status
zsh: command not found: gti

❌ Command not found: gti
   Try: wtf how do I gti
```

**Supported shells:** zsh, bash, fish

[Learn more about hooks →](../properties/hooks.md)

### `--remove-hooks`

Remove all shell hooks.

```bash
$ wtf --remove-hooks

✓ Removed wtf hooks from zsh
  Restart your shell to apply changes
```

Removes both error and command-not-found hooks from your shell config.

---

## Query Syntax

After any flags, you can provide a query:

```bash
# Simple query
$ wtf "what's my git status?"

# Multiple words (quotes optional)
$ wtf how do I exit vim

# With flags
$ wtf --verbose --model gpt-4 "explain this error"

# No query (shows help)
$ wtf
No query provided. Try:
  wtf "your question here"
  wtf undo
  wtf --help
```

**Special queries:**
- `wtf undo` - Undo last command
- `wtf remember X` - Save a preference
- `wtf forget X` - Remove a memory
- `wtf show memories` - View all memories
- `wtf clear memories` - Delete all memories

---

## Flag Order

Flags can appear before or after the query:

```bash
✓ wtf --verbose "my query"
✓ wtf "my query" --verbose
✓ wtf --model gpt-4 --verbose "query"
```

However, some flags exit immediately:

```bash
# These always exit, ignoring other flags/query
wtf --help
wtf --version
wtf --config
wtf --reset
wtf --setup
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (config missing, API error, etc.) |
| 2 | Invalid arguments |
| 130 | Interrupted (Ctrl+C) |

---

## Environment Variables

Some flags can also be set via environment variables:

```bash
# Enable verbose mode
export WTF_DEBUG=1
wtf "my query"  # Automatically verbose

# Override model
export WTF_MODEL=gpt-4
wtf "my query"  # Uses GPT-4
```

---

## Examples

### First Time Setup

```bash
$ wtf "what's my git status?"
No configuration found. Running setup wizard...

Which AI provider? [1] Anthropic
API key: sk-ant-...

✓ Setup complete!
```

### Quick Query

```bash
$ wtf undo my last commit

Let me check your git history.

✓ Checked git log

╭────────────────────────────────╮
│ $ git reset --soft HEAD~1     │
╰────────────────────────────────╯

Run this? [Y/n]
```

### Using Different Model

```bash
$ wtf --model gpt-4o "complex task..."

# Uses GPT-4o instead of default model
```

### Checking Config

```bash
$ wtf --config

Configuration:
  Config directory: ~/.config/wtf/
  Config file: ~/.config/wtf/config.json

Current settings:
  Model: claude-3.5-sonnet
  Key source: llm
```

### Installing Hooks

```bash
$ wtf --setup-error-hook
✓ Error hook installed

$ wtf --setup-not-found-hook
✓ Command-not-found hook installed

$ exec zsh  # Restart shell
```

---

## See Also

- [Getting Started](../getting-started.md) - Installation and first run
- [Properties](../properties/keys.md) - Configurable settings
- [Hooks](../properties/hooks.md) - Shell integration
- [FAQ](../faq.md) - Common questions
