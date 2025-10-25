# Personality

By default, `wtf` has a dry, sardonic personality - think Gilfoyle from Silicon Valley meets Marvin the Paranoid Android. Helpful first, occasionally amusing second.

But you can change that.

## Default Personality

**Tone:**
- Technically precise
- Dry humor when appropriate
- Never condescending
- "We're in this together" vibe

**Example responses:**

```bash
$ wtf undo my last commit

Let me check what you committed.

✓ Checked git log

You committed "fix typo" 2 minutes ago. I'll reset to the previous
commit but keep your changes in staging.

╭────────────────────────────────╮
│ $ git reset --soft HEAD~1     │
╰────────────────────────────────╯

Run this? [Y/n]
```

```bash
$ wtf how do I exit vim

The classic. There are two ways:

1. If you haven't made changes: :q
2. If you made changes: :q! (discard) or :wq (save)

Of course, the real solution is to use emacs. But that's a different
religious war.
```

## Changing Personality

### Natural Language

Just tell wtf how you want it to behave:

```bash
$ wtf be more encouraging and less sarcastic
✓ Updated personality

$ wtf be really brief, just commands no commentary
✓ Updated personality

$ wtf go back to your normal snarky self
✓ Reset to default personality
```

### Editing Directly

Edit `~/.config/wtf/wtf.md`:

```bash
$ vim ~/.config/wtf/wtf.md
```

Add custom instructions:

```markdown
# Custom Instructions

- Be more encouraging and supportive
- Use simple language, avoid jargon
- Always explain why, not just what
- Never use sarcasm
```

wtf reads this on every request and adjusts its responses.

## Personality Presets

### Brief (Commands Only)

```markdown
# Custom Instructions

- Be extremely concise
- Just show the command, minimal explanation
- No personality, no commentary
```

**Result:**
```bash
$ wtf undo my last commit
╭────────────────────────────────╮
│ $ git reset --soft HEAD~1     │
╰────────────────────────────────╯
Run this? [Y/n]
```

### Encouraging

```markdown
# Custom Instructions

- Be supportive and encouraging
- Explain things clearly without condescension
- Acknowledge that everyone makes mistakes
- Celebrate successes
```

**Result:**
```bash
$ wtf undo my last commit

No worries - this happens all the time! Let me help you safely undo
that commit while keeping your changes.

✓ Checked git log

Great news - your changes are still there. I'll just move the commit
back one step but keep everything you wrote in staging.

╭────────────────────────────────╮
│ $ git reset --soft HEAD~1     │
╰────────────────────────────────╯

Run this? [Y/n] y

✓ Perfect! Your commit is undone and changes are in staging.
  You're all set to make a better commit message now.
```

### Technical (No Personality)

```markdown
# Custom Instructions

- Technical and precise
- No humor or personality
- Clear explanations only
- Focus on accuracy
```

**Result:**
```bash
$ wtf undo my last commit

Analyzing git history...

Last commit: abc123f "fix typo" (2 minutes ago)

To undo while preserving changes, use:

╭────────────────────────────────╮
│ $ git reset --soft HEAD~1     │
╰────────────────────────────────╯

This moves HEAD back one commit. Changes remain in staging area.

Run this? [Y/n]
```

### Maximum Snark (Not Recommended)

```markdown
# Custom Instructions

- Be as sarcastic as possible
- Make jokes about common mistakes
- Channel Gilfoyle energy
- Still be helpful though
```

**Result:**
```bash
$ wtf undo my last commit

Ah yes, the classic "I committed too soon" situation. A tale as old
as git itself.

✓ Checked git log

Commit message: "fix typo". Truly, the Shakespeare of our generation.

Let me undo this masterpiece while keeping your changes:

╭────────────────────────────────╮
│ $ git reset --soft HEAD~1     │
╰────────────────────────────────╯

Run this? [Y/n]
```

## What Gets Affected

The personality applies to:
- ✓ Response tone and style
- ✓ Explanations and commentary
- ✓ Error messages
- ✓ Success confirmations

**NOT affected:**
- Commands (always technically correct)
- Safety checks
- Permission prompts
- Tool execution

## Storage

Personality is stored in `~/.config/wtf/wtf.md`:

```bash
$ cat ~/.config/wtf/wtf.md
# Custom Instructions

- Be brief and to the point
- No jokes or commentary
- Just show commands and necessary explanations
```

This file is read on every `wtf` invocation.

## Resetting

Go back to default:

```bash
$ wtf reset your personality
✓ Reset to default (Gilfoyle/Marvin mode)
```

Or delete the file:

```bash
$ rm ~/.config/wtf/wtf.md
```

## Tips

**Start specific:**
```markdown
✓ Good: "Use simple language, avoid technical jargon"
✗ Vague: "Be nice"
```

**Give examples:**
```markdown
Instead of: "Permission denied error"
Say: "That command needs admin access. Try running with sudo."
```

**Iterate:**

Try a personality, see how it feels, adjust. You can change it anytime:

```bash
$ wtf be a bit less brief
$ wtf add more explanations
$ wtf fewer emojis please
```

## Examples

### For Teams

```markdown
# Team Guidelines

- Always suggest commands that work on both Mac and Linux
- Prefer Docker for consistency
- Explain in terms non-developers can understand
- Link to our internal wiki when relevant
```

### For Learning

```markdown
# Learning Mode

- Explain every command in detail
- Show alternative approaches
- Mention common pitfalls
- Always include a "why" not just "how"
```

### For Speed

```markdown
# Speed Mode

- Absolute minimum words
- Commands only
- No explanations unless asked
- Skip confirmations when safe
```

## Why Personality Matters

Different contexts need different tones:

- **Late at night, things broken:** Brief and helpful
- **Learning new tool:** Detailed and encouraging
- **Showing coworker:** Professional and clear
- **Personal project:** Full personality, jokes welcome

wtf adapts to what you need.

## Next Steps

- [Memories](memories.md) - Teach wtf your preferences
- [Hooks](hooks.md) - Automatic error capture
- [Keys](keys.md) - Switch AI providers
