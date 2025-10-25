# Hooks

Shell hooks let `wtf` integrate deeply with your terminal. When enabled, `wtf` can automatically capture errors and suggest fixes without you typing anything.

## What Are Hooks?

Hooks are functions added to your shell config (`~/.zshrc`, `~/.bashrc`, etc.) that run:
- **After every command** (error hook)
- **When a command isn't found** (command-not-found hook)

This lets `wtf` detect problems automatically and offer help.

## Available Hooks

### Error Hook

Suggests running `wtf` when commands fail:

```bash
$ npm run biuld
npm error Missing script: "biuld"

💥 Command failed with exit code 1
   Run 'wtf' to analyze what went wrong
```

Then you just type `wtf` and it already knows the context.

### Command Not Found Hook

Suggests using `wtf` when you mistype commands:

```bash
$ gti status
zsh: command not found: gti

❌ Command not found: gti
   Try: wtf how do I gti
```

## Installing Hooks

### Automatic Setup

Run the setup commands:

```bash
# Install error hook
$ wtf --setup-error-hook
✓ Error hook installed for zsh
  Restart your shell or run: source ~/.zshrc

# Install command-not-found hook
$ wtf --setup-not-found-hook
✓ Command-not-found hook installed for zsh
  Restart your shell or run: source ~/.zshrc
```

Then restart your shell:

```bash
$ exec zsh
# or
$ source ~/.zshrc
```

### Natural Language

You can also ask naturally:

```bash
$ wtf install shell hooks
✓ Installed both hooks (error + command-not-found)
  Restart your shell to activate
```

## What Gets Added to Your Shell Config

The hooks add small functions to your shell config:

**Error Hook (~/.zshrc):**

```bash
# wtf error hook
precmd() {
  local exit_code=$?
  if [ $exit_code -ne 0 ]; then
    echo "💥 Command failed with exit code $exit_code"
    echo "   Run 'wtf' to analyze what went wrong"
  fi
}
```

**Command Not Found Hook (~/.zshrc):**

```bash
# wtf command-not-found hook
command_not_found_handler() {
  echo "❌ Command not found: $1"
  echo "   Try: wtf how do I $1"
  return 127
}
```

These are non-invasive - they just print suggestions, they don't run anything automatically.

## Removing Hooks

Remove all hooks:

```bash
$ wtf --remove-hooks
✓ Removed wtf hooks from zsh
  Restart your shell to apply changes
```

Or remove manually:

```bash
# Edit your shell config
$ vim ~/.zshrc

# Delete the wtf hook sections
# (marked with "# wtf error hook" and "# wtf command-not-found hook")

# Restart shell
$ exec zsh
```

## Supported Shells

- ✓ **zsh** - Full support
- ✓ **bash** - Full support
- ✓ **fish** - Full support
- ⚠️ **Windows (PowerShell/CMD)** - Not supported yet

## How Hooks Help

### Without Hooks

```bash
$ npm run biuld
npm error Missing script: "biuld"

$ wtf
What's your question?

$ what was wrong with my last command?
Let me check...
```

### With Hooks

```bash
$ npm run biuld
npm error Missing script: "biuld"

💥 Command failed with exit code 1
   Run 'wtf' to analyze what went wrong

$ wtf
I see you tried 'npm run biuld'. You meant 'npm run build'.

╭────────────────────────────────╮
│ $ npm run build               │
╰────────────────────────────────╯

Run this? [Y/n]
```

The difference: **wtf already knows what went wrong** because the hook captured it.

## Privacy & Performance

**Do hooks slow down my terminal?**
No. They're tiny functions that only run when needed (command fails or isn't found).

**What data do hooks collect?**
Nothing. They just print messages. They don't send data anywhere.

**Can I customize the messages?**
Yes! Edit the hook functions in your shell config to change the text.

## Checking if Hooks Are Installed

```bash
$ wtf are hooks installed?
Error hook: ✓ Installed (zsh)
Command-not-found hook: ✓ Installed (zsh)
```

Or check manually:

```bash
$ grep "wtf" ~/.zshrc
# If you see hook code, they're installed
```

## Troubleshooting

### Hooks not working after install

Make sure you restarted your shell:

```bash
$ exec zsh
# or
$ source ~/.zshrc
```

### Hooks installed but not triggering

Check if your shell config sources correctly:

```bash
$ which zsh
/bin/zsh

$ echo $SHELL
/bin/zsh

# Should match
```

### Conflicts with other tools

Some tools also use `precmd` or `command_not_found_handler`. If you have conflicts:

1. Check what else is using those functions
2. Combine them manually in your shell config
3. Or disable wtf hooks and use `wtf` manually

### Removing old hook versions

If you upgraded wtf and hooks behave oddly:

```bash
$ wtf --remove-hooks
$ wtf --setup-error-hook
$ wtf --setup-not-found-hook
```

This removes old hooks and installs fresh ones.

## Tips

**Start with just error hook:**

The error hook is the most useful. Try that first:

```bash
$ wtf --setup-error-hook
```

**Customize the messages:**

Edit `~/.zshrc` to change what the hooks say:

```bash
# Instead of:
echo "💥 Command failed"

# Change to:
echo "Oops! Something broke. Type 'wtf' for help."
```

**Disable temporarily:**

Comment out the hooks in your shell config:

```bash
# # wtf error hook
# precmd() { ... }
```

Then reload: `source ~/.zshrc`

## Should You Use Hooks?

**Use hooks if:**
- ✓ You want automatic error detection
- ✓ You often forget what command failed
- ✓ You want seamless wtf integration

**Skip hooks if:**
- ✗ You prefer explicit invocation
- ✗ You have conflicts with other tools
- ✗ You want minimal shell config

Hooks are optional. `wtf` works great without them.

## Next Steps

- [Memories](memories.md) - Teach wtf your preferences
- [Personality](personality.md) - Customize how wtf talks
- [Keys](keys.md) - Switch AI providers
