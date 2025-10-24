# Getting Started

## Installation

### Option 1: curl (Recommended)

The installation script handles everything, including collision detection:

```bash
curl -sSL https://raw.githubusercontent.com/davefowler/wtf-terminal-ai/main/install.sh | bash
```

This will:

- Check for Python 3.10+
- Install wtf-ai via pip
- Detect if you already have a `wtf` alias/command
- Offer alternative names (wtfai, wai) if collision detected
- Set up PATH if needed

### Option 2: pip

```bash
pip install wtf-ai
```

Simple. Direct. No frills. Just like we like our coffee.

### Option 3: From Source

For the brave souls who like living on the edge:

```bash
git clone https://github.com/davefowler/wtf-terminal-ai.git
cd wtf-terminal-ai
pip install -e .
```

## First Run

On first use, wtf automatically runs a setup wizard:

```bash
$ wtf "what's wrong?"

⚠  No configuration found. Running setup wizard...

Welcome to wtf setup!

Let's get you configured. This will only take a moment.

Step 1: Choose your AI provider

  1. Anthropic (Claude)
  2. OpenAI (GPT)
  3. Google (Gemini)

Select provider [1]: _
```

### Choose Your Provider

**Anthropic Claude** (Recommended)
- Best at understanding context
- Most "Gilfoyle-like" responses
- Get key: https://console.anthropic.com/settings/keys

**OpenAI GPT**
- Fastest responses
- Most widely available
- Get key: https://platform.openai.com/api-keys

**Google Gemini**
- Good multimodal support
- Free tier available
- Get key: https://makersuite.google.com/app/apikey

### API Key Setup

You can store your API key in two ways:

**Environment Variable (Recommended)**
```bash
export ANTHROPIC_API_KEY='your-key-here'
export OPENAI_API_KEY='your-key-here'
export GOOGLE_API_KEY='your-key-here'
```

Add to your `~/.zshrc` or `~/.bashrc` to persist.

**Config File**
The wizard can store it in `~/.config/wtf/config.json` for you.

!!! warning
    Config file storage is convenient but less secure. Use environment variables in production.

### Model Selection

Each provider offers multiple models:

**Anthropic:**
- claude-3.5-sonnet (Recommended) - Best balance
- claude-3-opus - Most capable, slower
- claude-3-haiku - Fastest, lighter

**OpenAI:**
- gpt-4o (Recommended) - Latest, best
- gpt-4o-mini - Faster, cheaper
- gpt-4-turbo - Previous generation

**Google:**
- gemini-1.5-pro (Recommended) - Most capable
- gemini-1.5-flash - Faster responses

## Verify Installation

```bash
wtf --version
# wtf 0.1.0

wtf "hello"
# [AI responds with personality]
```

## Shell Integration (Important!)

To use wtf without quotes around every query, add this to your `~/.zshrc` or `~/.bashrc`:

```bash
alias wtf='noglob wtf'
```

Then restart your shell: `source ~/.zshrc`

**Why?** Without this, zsh/bash will try to expand `?` and `*` as glob patterns:

```bash
# Without alias - ERROR
wtf are you there?
# zsh: no matches found: there?

# With alias - WORKS
wtf are you there?
# [AI responds]

# Always works with quotes
wtf "are you there?"
# [AI responds]
```

The curl installation script adds this alias automatically.

## Next Steps

- [Quick Tour](quick-tour.md) - See what wtf can do
- [Configuration](config/files.md) - Customize your setup
- [FAQ](faq.md) - Common questions

## Troubleshooting

**wtf: command not found**

Your PATH doesn't include the pip installation directory. Add this to `~/.zshrc` or `~/.bashrc`:

```bash
export PATH="$PATH:$HOME/.local/bin"
```

Then: `source ~/.zshrc`

**API key errors**

Make sure your API key is set:

```bash
echo $ANTHROPIC_API_KEY  # Should print your key
```

If empty, set it in your shell config or run: `wtf --setup`

**Python version issues**

wtf requires Python 3.10+. Check your version:

```bash
python3 --version
```

If too old, install a newer Python:

```bash
# macOS
brew install python3

# Ubuntu
sudo apt install python3.11

# Fedora
sudo dnf install python3.11
```
