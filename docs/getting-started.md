# Getting Started

## Installation

Welcome to the last manual installation you'll ever need.  In the future you'll just be able to do ```wtf install X```.  

Take your time. Read through and debate the 3 different options. Reminice on the changing of an era.  

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

**Local Models (Ollama)** - No API key needed!
- 100% private - runs on your machine
- Free forever
- Works offline
- Install: https://ollama.ai

```bash
# Install Ollama, then pull a model
ollama pull llama3.2

# wtf will auto-detect it
wtf --setup
```

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
- claude-sonnet-4 (Recommended) - Latest, best balance
- claude-3-5-sonnet - Previous generation Sonnet
- claude-opus-4 - Most capable
- claude-3-5-haiku - Fastest, cheapest

**OpenAI:**
- gpt-4o (Recommended) - Great balance of speed and capability
- gpt-4o-mini - Faster, cheaper
- o1 / o3 - Advanced reasoning models
- gpt-5 / gpt-4.5 - Latest generation (when available)

**Google:**
- gemini-2.0 - Latest generation
- gemini-1.5-pro - Most capable
- gemini-1.5-flash - Faster responses

**Local (Ollama) - Free, Private:**
- llama3.2 - Latest Llama, great all-around
- llama3.1 / llama3 - Previous Llama versions
- mistral - Fast and capable
- qwen2.5 - Strong multilingual support
- deepseek-r1 - Advanced reasoning
- codellama - Optimized for code

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
