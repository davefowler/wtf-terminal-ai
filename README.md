# wtf - Because working in the terminal often gets you asking wtf

A command-line AI assistant that provides contextual help based on terminal history and user queries.

## What is this?

`wtf` is a terminal AI assistant that understands your terminal context. Made a mistake? Just say `wtf undo`. Hit an error? Just type `wtf`. Need to install something? Type `wtf install [thing]`.

No flags to remember. No manual pages to consult. Just describe what you want.

## Installation

### Via pip (recommended)

```bash
pip install wtf-ai
```

### From source

```bash
git clone https://github.com/davefowler/wtf-terminal-ai.git
cd wtf-terminal-ai
pip install -e .
```

## Quick Start

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
wtf remember I prefer npm over yarn
```

## Requirements

- Python 3.10 or higher
- An API key from Anthropic, OpenAI, or Google

## Configuration

Configuration is stored in `~/.config/wtf/`:
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
