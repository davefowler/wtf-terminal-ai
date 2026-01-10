# wtf - Because working in the terminal often gets you asking wtf

A command-line AI assistant that provides contextual help based on terminal history and user queries.

📚 **[Full Documentation](https://davefowler.github.io/wtf-terminal-ai/)** | 🚀 **[Quick Start Guide](https://davefowler.github.io/wtf-terminal-ai/getting-started/)** | ❓ **[FAQ](https://davefowler.github.io/wtf-terminal-ai/faq/)**

### Quick install

```bash
curl -sSL https://raw.githubusercontent.com/davefowler/wtf-terminal-ai/main/install.sh | bash
```

---

**⏪ Made a mistake?** Just say `wtf undo` - it analyzes your history and reverses your last command intelligently. Works for git commits, file deletions, package installs, and more.

## What is this?

`wtf` is a terminal AI assistant that is there for you when you f up. Hit an error?  Just type `wtf`.  Made a mistake? Just say `wtf undo`.  Need to install something? Type `wtf install [thing]`.  Forget the command?  No problem just ask `wtf can you back me out of this failed merge attempt?`.

No flags to remember. No manual pages to consult. Just describe what you want.

## Who is wtf for?

### Non-engineers

More and more people are now able to work with code and command lines: data analysts using git for dbt models, designers and product managers vibe coding prototype features, marketers working with static sites.  `wtf` helps with setups, remembering commands, and gets them out of jams.

### Engineers

There are so many tools and commands to remember.  You get stuck, you make mistakes, you get slowed down having to go read docs or switch over to ask your llm of choice.  But now you can just stay in your terminal and have it answer or even fix your problems as they come up.

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

### From source (for development)

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

# Find documentation
wtf find me the react docs

# Get general knowledge
wtf what is rust programming language
```

## Requirements

- Python 3.9 or higher
- An API key from Anthropic, OpenAI, or Google — **OR run locally with Ollama (free, no API key needed!)**

## Optional: Web Search

wtf has limited web search by default (encyclopedic facts only). For full web search (weather, news, current events, documentation):

**Get a free Brave Search API key:**
1. Sign up at https://brave.com/search/api/ (free tier: 2,000 searches/month, no credit card)
2. Save your key: `wtf here is my brave search api key YOUR_KEY_HERE`

That's it! Now wtf can search for anything.

## Hooks - Want wtf all the time?

Add wtf to your shell hooks for automatic assistance:

### Error Hook
Automatically suggest wtf when commands fail:
```bash
wtf --setup-error-hook
```

Now whenever a command fails, you'll see:
```
💥 Command failed with exit code 1
   Run 'wtf' to analyze what went wrong
```

### Command Not Found Hook
Suggest wtf when you mistype commands:
```bash
wtf --setup-not-found-hook
```

When you type a non-existent command:
```
❌ Command not found: gti
   Try: wtf how do I gti
```

### Remove Hooks
Changed your mind?
```bash
wtf --remove-hooks
```

**Supported shells:** zsh, bash, fish

## Configuration

Much of the configuration you can just do through telling `wtf`.  Here are some config nouns that are useful in changing it:

 - memories - remembers things you tell it or it discovers like what text editor you prefer
 - personality - it has one.  don't like it, just tell it to change
 - allow list - commands that can run without asking
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

📖 **[Read the full documentation](https://davefowler.github.io/wtf-terminal-ai/)** with terminal-style theming!

Topics covered:
- [Getting Started](https://davefowler.github.io/wtf-terminal-ai/getting-started/) - Installation and first run
- [Features](https://davefowler.github.io/wtf-terminal-ai/quick-tour/) - What wtf can do
- [Configuration](https://davefowler.github.io/wtf-terminal-ai/faq/) - Customization options
- [FAQ](https://davefowler.github.io/wtf-terminal-ai/faq/) - Common questions

For developers: See [SPEC.md](SPEC.md) and [TASKS.md](./instructions_from_the_creator/TASKS.md)

## License

MIT License - see LICENSE file for details

## Acknowledgments

wtf stands on the shoulders of:

- **[tAI](https://github.com/AbanteAI/tAI)** - Original terminal AI inspiration
- **[Aider](https://github.com/paul-gauthier/aider)** - Proved AI + version control works
- **[llm](https://github.com/simonw/llm)** - Model abstraction by Simon Willison
- **[Rich](https://github.com/Textualize/rich)** - Terminal UI that doesn't suck

See [full acknowledgments](https://davefowler.github.io/wtf-terminal-ai/acknowledgments/) for details.

## Contributing

Issues and PRs welcome at [https://github.com/davefowler/wtf-terminal-ai](https://github.com/davefowler/wtf-terminal-ai)
