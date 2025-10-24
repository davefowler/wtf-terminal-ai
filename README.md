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
git clone https://github.com/username/wtf-terminal-ai.git
cd wtf-terminal-ai
pip install -e .
```

## First Run Setup

On first run, `wtf` will guide you through a simple setup:

1. Choose your AI provider (Anthropic, OpenAI, or Google)
2. Enter your API key
3. Select your default model

That's it. You're ready to go.

## Quick Start

```bash
# Get help with anything
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

For full documentation, visit [https://wtf-ai.dev](https://wtf-ai.dev)

## License

MIT License - see LICENSE file for details

## Contributing

Issues and PRs welcome at [https://github.com/username/wtf-terminal-ai](https://github.com/username/wtf-terminal-ai)
