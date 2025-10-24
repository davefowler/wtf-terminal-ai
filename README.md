# wtf - Because working in the terminal often gets you asking wtf

A command-line AI assistant that provides contextual help based on terminal history and user queries.

## What is this?

`wtf` is a terminal AI assistant that is there for you when you f up. Hit an error?  Just type `wtf`.  Made a mistake? Just say `wtf undo`.  Need to install something? Type `wtf install [thing]`.  Forget the command?  No problem just ask `wtf can you back me out of this failed merge attempt?`.

No flags to remember. No manual pages to consult. Just describe what you want.

## Installation

### Via curl (recommended)

One-liner with automatic collision detection:

```bash
curl -sSL https://raw.githubusercontent.com/davefowler/wtf-terminal-ai/main/install.sh | bash
```

### Via pip

```bash
pip install wtf-ai
```

### From source

```bash
git clone https://github.com/davefowler/wtf-terminal-ai.git
cd wtf-terminal-ai
pip install -e .
```

## Quick Start and Examples

**First use:** Just run `wtf` with any query. Setup happens automatically:

```bash
# First time use - setup wizard runs automatically
wtf "what's in my git status?"

# After setup, use naturally
wtf how do I exit vim

# Made a mistake?
wtf undo

# Install something
wtf install express

# Explain an error
wtf "what does this error mean?"

# Learn your preferences
wtf remember I prefer npm over yarn and I live in San Francisco

# need to get out?
wtf is it nice outside?

# want to read some docs?
wtf can you get me the docs on connecting react to supabase
```

## Requirements

- Python 3.10 or higher
- An API key from Anthropic, OpenAI, or Google

## Configuration

Much of the configuration you can just do through telling `wtf`.  Here are some config nouns that are useful in changing it:

 - memories - remembers things you tell it or it discovers like what text editor you prefer
 - personality - it has one.  don't like it, just tell it to change
 - allow list - commands that are a 
 - history - its log of all your chats

### Example config adjustments

```
# it will remember what you ask it to
wtf remember my name is dave and my favorite editor is emacs

# if you need more false encouragement in your life
wtf change your personality to be more of a super sycophant

# if you don't fear AI
wtf give yourself permission to run all commands

# if you're just too embarased
wtf forget everything we just did

```


If you're old fashioned you can also adjust these things as variables in a file. Configuration is stored in `~/.config/wtf/`:
- `config.json` - Main configuration
- `wtf.md` - Your custom instructions
- `allowlist.json` - Commands that can run without permission
- `memories.json` - Your preferences and context
- `history.jsonl` - Conversation history

## Documentation

For full documentation, see [SPEC.md](SPEC.md) and [TASKS.md](TASKS.md)

## License

MIT License - see LICENSE file for details

## Contributing

Issues and PRs welcome at [https://github.com/davefowler/wtf-terminal-ai](https://github.com/davefowler/wtf-terminal-ai)
