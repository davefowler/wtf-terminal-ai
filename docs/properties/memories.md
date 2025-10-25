# Memories

`wtf` remembers your preferences. Things like "I use vim" or "I prefer npm over yarn". These memories help it give better, more personalized suggestions.

## What Gets Remembered?

- **Editor preferences:** vim, emacs, VS Code, etc.
- **Tool preferences:** npm vs yarn, pip vs poetry, etc.
- **Environment details:** OS, timezone, common directories
- **Workflow patterns:** How you typically work

## How to Use Memories

### Teaching wtf Your Preferences

Just tell it naturally:

```bash
$ wtf remember I use emacs for editing
✓ Remembered: editor = emacs

$ wtf remember I prefer pytest over unittest
✓ Remembered: test_framework = pytest

$ wtf remember I live in San Francisco
✓ Remembered: location = San Francisco
```

### Viewing Your Memories

```bash
$ wtf show me what you remember
Your memories:
- editor: emacs
- test_framework: pytest
- location: San Francisco
```

### Forgetting Things

```bash
$ wtf forget about my editor preference
✓ Forgot: editor

$ wtf clear all memories
⚠ This will delete all stored preferences. Continue? [y/N]
```

## How Memories Work

When you ask `wtf` for help, it includes your memories in the context:

```bash
$ wtf how do I run my tests?

# Without memories:
→ Suggests: python -m unittest

# With memory (test_framework: pytest):
→ Suggests: pytest
```

The AI uses memories to:
- Skip questions it already knows the answer to
- Suggest tools you actually use
- Format output the way you prefer

## Storage

Memories are stored in `~/.config/wtf/memories.json`:

```json
{
  "editor": {
    "value": "emacs",
    "confidence": 1.0,
    "learned_from": "explicit_instruction",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "test_framework": {
    "value": "pytest",
    "confidence": 1.0,
    "learned_from": "explicit_instruction",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

## Confidence Scores

Some memories have confidence scores:

- **1.0:** Explicitly told (you said "remember I use vim")
- **0.8:** Strong inference (you always use `pytest`)
- **0.5:** Weak inference (you used `yarn` once)

Lower confidence memories may be double-checked before being used.

## Privacy

- Memories are stored **locally only** in `~/.config/wtf/`
- They're sent to the AI provider as context with your queries
- No memories are sent to wtf servers (there are no wtf servers)

## Examples

### Workflow Preferences

```bash
$ wtf remember I always rebase instead of merge
$ wtf remember I use Docker for all my projects
$ wtf remember I work on microservices
```

Then when you ask:

```bash
$ wtf how do I update my feature branch?
→ Suggests: git pull --rebase origin main
# (Instead of git merge)
```

### Environment Details

```bash
$ wtf remember I use zsh on macOS
$ wtf remember my projects are in ~/code/
$ wtf remember I use pyenv for Python
```

## Clearing Everything

Need a fresh start?

```bash
$ wtf --reset
```

This deletes all config, including memories.

## Tips

**Be specific:**
```bash
✓ Good: "remember I use pytest with coverage"
✗ Vague: "remember I like testing"
```

**Update when things change:**
```bash
$ wtf remember I switched to pnpm from npm
```

**Don't over-specify:**
```bash
✗ Too much: "remember I use vim with these exact plugins..."
✓ Enough: "remember I use vim"
```

## Next Steps

- [Personality](personality.md) - Customize how wtf talks
- [Hooks](hooks.md) - Automatic error capture
- [Keys](keys.md) - Switch AI providers
