# API Keys

`wtf` needs an AI provider to work. You pick: Anthropic (Claude), OpenAI (GPT), Google (Gemini), or **run locally with Ollama** (no API key needed!).

## Supported Providers

| Provider | Models | Best For |
|----------|--------|----------|
| **Anthropic** | Claude Sonnet 4, Claude Opus 4, Claude 3.5 Sonnet/Haiku | Best overall, great at following instructions |
| **OpenAI** | GPT-4o, GPT-4o Mini, o1, o3, GPT-5 | Fast, widely available, reasoning models |
| **Google** | Gemini 2.0, Gemini 1.5 Pro/Flash | Good balance of speed and quality |
| **Local (Ollama)** | Llama 3.2, Mistral, Qwen, DeepSeek, CodeLlama | Free, private, offline - no API key needed |

## Getting an API Key

### Anthropic (Recommended)

1. Sign up at https://console.anthropic.com
2. Go to Settings → API Keys
3. Create a new key
4. Free tier: $5 credit, then pay-as-you-go

```bash
$ wtf here is my anthropic api key sk-ant-...
✓ API key saved
✓ Using claude-3.5-sonnet as default model
```

### OpenAI

1. Sign up at https://platform.openai.com
2. Go to API Keys
3. Create a new secret key
4. Pricing: Pay-as-you-go

```bash
$ wtf here is my openai api key sk-...
✓ API key saved
✓ Using gpt-4o as default model
```

### Google

1. Go to https://makersuite.google.com/app/apikey
2. Create an API key
3. Free tier: 60 requests/minute

```bash
$ wtf here is my google api key AIza...
✓ API key saved
✓ Using gemini-pro as default model
```

### Local Models (Ollama) - No API Key Needed!

Run AI completely locally on your machine. Free, private, and works offline.

1. Install Ollama from https://ollama.ai
2. Pull a model:

```bash
# Pick one (or several!)
ollama pull llama3.2        # Best all-around
ollama pull mistral         # Fast and capable
ollama pull codellama       # Great for coding
ollama pull deepseek-r1     # Advanced reasoning
ollama pull qwen2.5         # Strong multilingual
```

3. Run setup - wtf will auto-detect your models:

```bash
$ wtf --setup
✓ Local models detected (Ollama)

  1. Ollama Llama 3.2 (local, free)
  2. Ollama Mistral (local, free)
  ...
```

**Why local?**
- 🔒 **100% private** - nothing leaves your machine
- 💰 **Free forever** - no API costs
- 🌐 **Works offline** - no internet needed
- ⚡ **Fast** - no network latency (if you have good hardware)

## Setup During First Run

The first time you run `wtf`, it asks you to pick a provider:

```bash
$ wtf what's my git status?

No API key configured. Let's set one up.

Which AI provider do you want to use?
  1. Anthropic (Claude) - Recommended
  2. OpenAI (GPT-4)
  3. Google (Gemini)

Choose [1-3]: 1

Great! Get your API key from:
https://console.anthropic.com/settings/keys

Paste your API key: sk-ant-...
✓ API key saved
```

## Switching Providers

Change providers anytime:

```bash
$ wtf switch to OpenAI
What's your OpenAI API key?
Paste it here: sk-...
✓ Switched to OpenAI (gpt-4o)
```

Or re-run setup:

```bash
$ wtf --setup
```

## Changing Models

Use a different model from the same provider:

```bash
$ wtf use claude-opus as my model
✓ Switched to claude-opus

$ wtf use gpt-3.5-turbo
✓ Switched to gpt-3.5-turbo (faster, cheaper)
```

## Where Keys Are Stored

### Via llm Library (Recommended)

By default, wtf uses Simon Willison's `llm` library for key management:

```bash
# Keys stored in llm's keyring
~/.config/io.datasette.llm/keys.json
```

This is secure and shared with other llm-based tools.

### Via Environment Variables

You can also use environment variables:

```bash
# Add to ~/.zshrc or ~/.bashrc
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."
```

Then:

```bash
$ source ~/.zshrc
$ wtf --setup
```

wtf will detect the environment variable automatically.

### In Config File (Not Recommended)

Keys can be stored in `~/.config/wtf/config.json`, but this is less secure:

```json
{
  "api": {
    "model": "claude-3.5-sonnet",
    "key_source": "config",
    "key": "sk-ant-..."
  }
}
```

**We don't recommend this.** Use llm's keyring or environment variables instead.

## Checking Your Setup

```bash
$ wtf what API key am I using?
You're using Anthropic (claude-3.5-sonnet)
API key: sk-ant-...xyz (last 3 chars)
```

Or check the config:

```bash
$ wtf --config
Config directory: ~/.config/wtf/
Config file: ~/.config/wtf/config.json

Current settings:
  Model: claude-3.5-sonnet
  Key source: llm
```

## Model Costs

Approximate costs per 1M tokens (as of 2024):

| Model | Input | Output | Speed |
|-------|-------|--------|-------|
| GPT-4o | $5 | $15 | Fast |
| Claude Sonnet 3.5 | $3 | $15 | Medium |
| Claude Haiku | $0.25 | $1.25 | Very fast |
| Gemini Pro | $0.50 | $1.50 | Fast |

For typical wtf usage: **~$0.01-0.05 per query**

## Troubleshooting

### "Invalid API key" error

```bash
$ wtf test my setup
✗ Error: Invalid API key

Fix:
1. Double-check you copied the full key
2. Make sure the key is active (check provider dashboard)
3. Re-run setup: wtf --setup
```

### "Rate limit exceeded"

```bash
✗ Error: Rate limit exceeded

Fix:
1. Wait a few minutes
2. Check your provider's rate limits
3. Upgrade your API plan if needed
```

### Key not being detected

```bash
$ echo $ANTHROPIC_API_KEY
# (should show your key)

# If empty:
$ export ANTHROPIC_API_KEY="sk-ant-..."
$ source ~/.zshrc
```

## Security Best Practices

✓ **Do:**
- Use environment variables or llm's keyring
- Keep keys in `.env` files (add to `.gitignore`)
- Rotate keys periodically
- Use separate keys for different projects

✗ **Don't:**
- Commit keys to git
- Share keys in Slack/email
- Store keys in plain text files
- Use the same key everywhere

## Next Steps

- [Web Search](../config/web-search.md) - Add Brave Search for current info
- [Memories](memories.md) - Teach wtf your preferences
- [Quick Tour](../quick-tour.md) - See what wtf can do
