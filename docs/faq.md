# FAQ

## General

### Is this like GitHub Copilot for the terminal?

Sort of, but Copilot autocompletes code. We fix your mistakes after you've already made them. It's the difference between a copilot and a very sarcastic flight attendant who tells you how to use the emergency exit after you've already crashed.

### Why "wtf"?

Because that's what everyone says when something goes wrong in the terminal. We just made it actually useful instead of an expression of existential dread.

### Is my data sent to AI providers?

Yes. Your shell history, git status, and query are sent to the AI provider you chose (Anthropic, OpenAI, or Google). This is how the AI understands your context.

What's NOT sent:
- File contents (unless you explicitly ask)
- Environment variables
- Passwords or secrets

See each provider's privacy policy for how they handle data.

### Can I use this offline?

No. wtf requires an API connection to function. That's the trade-off for having an AI that actually understands your problems instead of just printing error codes.

### Does this work on Windows?

In theory, yes, if you're using WSL (Windows Subsystem for Linux). In practice, we haven't tested it because Windows already has its own wtf-inducing complexity.

## Setup & Configuration

### I already have a `wtf` alias. Can I still use this?

Yes! The installation script detects this and offers alternatives:

- `wtfai` - Full name, no confusion
- `wai` - Shorter, still unique

You can also manually create an alias:

```bash
alias wai='wtf'
```

### Can I change AI providers later?

Yes. Run the setup wizard again:

```bash
wtf --setup
```

### Where is my config stored?

`~/.config/wtf/` contains:

- `config.json` - Main configuration
- `allowlist.json` - Commands that run without permission
- `denylist.json` - Commands that are always blocked
- `memories.json` - Your preferences
- `history.jsonl` - Conversation history
- `wtf.md` - Custom instructions for the AI

### Can I customize the AI's personality?

Yes! Edit `~/.config/wtf/wtf.md` to add custom instructions:

```markdown
# My Custom Instructions

- Be more cheerful
- Always suggest Python over JavaScript
- Never use emojis
```

The AI will read this and adapt its responses.

### What commands can run without permission?

86 safe, read-only commands auto-execute:

- `git status`, `git log`, `git diff` (read-only git)
- `ls`, `cat`, `pwd`, `echo` (file viewing)
- `npm list`, `pip show` (package inspection)
- `which`, `command -v` (command checking)
- [Full list](config/allowlist.md)

You can add your own to the allowlist.

## Usage

### How do I undo something?

```bash
wtf undo
wtf undo that commit
wtf undo the last 3 commands
```

The AI analyzes your shell history and suggests safe reversal commands.

### Can wtf execute commands automatically?

Only safe, read-only commands. Everything else requires your permission.

You can mark commands as "always allow" to skip the prompt next time.

### What if I don't want wtf to remember something?

```bash
wtf forget about [thing]
wtf clear all memories
```

### Can I see my conversation history?

It's stored in `~/.config/wtf/history.jsonl`. Each line is a JSON object:

```json
{"timestamp": "2024-01-01T12:00:00", "query": "...", "response": "...", "commands": [...]}
```

### Does wtf work in Vim?

No, because if you're in Vim, you're already too far gone. Just type `:q!` and try again.

(Serious answer: wtf is a shell command, not a Vim plugin. Use it before or after Vim, not during.)

## Privacy & Security

### What data does wtf collect?

wtf itself collects nothing. Your data goes to whichever AI provider you chose:

- Anthropic: https://www.anthropic.com/legal/privacy
- OpenAI: https://openai.com/policies/privacy-policy
- Google: https://policies.google.com/privacy

All conversation history is stored locally in `~/.config/wtf/history.jsonl`.

### Can wtf run dangerous commands?

Not without your permission. Dangerous patterns are detected:

- `rm -rf /` - System deletion
- `chmod 777` - Permission bombs
- `:(){ :|:& };:` - Fork bombs
- Anything with `sudo` requires permission

You can add commands to the denylist to block them entirely.

### What if wtf suggests something wrong?

AI makes mistakes. Always review commands before approving.

- Read the explanation
- Check the command
- Use `[n]o` to decline
- Report bad suggestions as issues

### Can I audit what commands were run?

Yes. Check `~/.config/wtf/history.jsonl` for a complete log of queries, responses, and executed commands.

## Troubleshooting

### wtf is slow

- Check your internet connection
- Try a faster model (gpt-4o-mini, claude-haiku, gemini-flash)
- The AI provider might be experiencing issues

### API rate limit errors

You've hit your provider's rate limit. Wait a few minutes or upgrade your API plan.

### wtf suggests the same wrong thing repeatedly

The AI doesn't learn from your corrections within a conversation. If it keeps suggesting the wrong approach:

1. Use more specific queries
2. Add custom instructions in `~/.config/wtf/wtf.md`
3. Teach it your preferences: `wtf remember I use emacs`

### Commands aren't executing

Check if they're in the denylist:

```bash
cat ~/.config/wtf/denylist.json
```

Remove entries you want to allow.

## Philosophy

### Why the sarcastic personality?

Because dealing with terminal problems is already frustrating. Might as well have some fun with it.

Plus, Gilfoyle and Marvin are icons of technical competence mixed with world-weary resignation. Seemed fitting for a tool that helps you when you're asking "wtf?"

### Can I disable the personality?

You can tone it down with custom instructions:

```markdown
# ~/.config/wtf/wtf.md

Please be more straightforward and less sarcastic in your responses.
```

But where's the fun in that?

### Is this replacing Stack Overflow?

No. Stack Overflow is for when you have a specific question. wtf is for when you've already messed something up and need immediate help.

Think of it as the difference between reading a manual and calling a friend who's good at computers.

## Contributing

### I found a bug

Report it: https://github.com/davefowler/wtf-terminal-ai/issues

Include:
- Your wtf version (`wtf --version`)
- The command you ran
- What happened vs. what you expected
- The AI provider/model you're using

### I want to add a feature

PRs welcome! Check the existing issues first to see if it's already planned.

### Can I contribute to the allowlist of safe commands?

Yes! The allowlist is defined in `wtf/core/permissions.py`. Submit a PR with:

- The command pattern
- Why it's safe (read-only, no side effects)
- Example use cases

### The AI's personality isn't Gilfoyle enough

We're open to prompt improvements. Submit a PR to `wtf/ai/prompts.py` with specific examples of how the personality should change.

## Meta

### Who made this?

Developers who got tired of Googling the same error messages.

### Is this a joke?

No. It's real software that solves real problems. The jokes are just self-defense mechanisms.

### Can I use this for commercial projects?

Yes. MIT License. Go wild.
