# Setup

So you've installed `wtf`. Now what? Don't worry, it's not complicated.

## First Run

The first time you run `wtf`, it'll walk you through a brief setup. No forms to fill out. No accounts to create. Just three questions.

```bash
$ wtf "help me"
```

## The Setup Wizard

`wtf` will ask you:

1. **Choose your AI provider** (Anthropic, OpenAI, or Google)
2. **Enter your API key** 
3. **Select your default model**

That's it. Takes about 30 seconds.

!!! tip "API Keys"
    Don't have an API key? See [API Keys](config/api-keys.md) for where to get one.

## What Gets Configured

The wizard creates a config file at `~/.config/wtf/config.yaml` with:

- Your chosen AI provider
- Your default model
- Basic settings (all sane defaults)

Your API key is stored securely in your system keychain when possible, or in the config file with appropriate permissions.

## Testing It Out

Once setup is complete, try a simple command:

```bash
$ wtf "show my git status"
```

If you see `wtf` respond with something helpful (or sarcastic), you're good to go.

## Configuration Files Created

After first run, you'll have:

```
~/.config/wtf/
├── config.yaml          # Main configuration
├── conversation.jsonl   # Conversation history
└── allowlist.json       # Auto-execute permissions (created as needed)
```

## Next Steps

- **[Quick Tour](quick-tour.md)** - See what `wtf` can do
- **[Memories](features/memories.md)** - Teach `wtf` your preferences
- **[Permissions](features/permissions.md)** - Control what runs automatically

## Reconfiguring

Want to change providers or models later? Just run:

```bash
$ wtf "use a different model"
```

Or edit `~/.config/wtf/config.yaml` directly. We're not picky.

## Troubleshooting Setup

### "API key invalid"

- Double-check you copied the key correctly
- Make sure the key has the right permissions
- Some providers have separate keys for different models

### "Can't find config directory"

`wtf` creates `~/.config/wtf/` automatically. If it fails:

- Check you have write permissions to `~/.config/`
- Try creating it manually: `mkdir -p ~/.config/wtf`

### "Model not available"

Your API key might not have access to that model. Try a different one or check your provider's console.

Need more help? Check [Troubleshooting](troubleshooting.md).

