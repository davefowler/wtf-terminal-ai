# Troubleshooting

Common issues and how to fix them.

## Installation Issues

### `command not found: wtf`

**Problem:** Shell can't find wtf after installation.

**Solutions:**

1. **Restart your shell:**
   ```bash
   exec $SHELL
   ```

2. **Check if installed:**
   ```bash
   which wtf
   pip list | grep wtf
   ```

3. **Install in user mode:**
   ```bash
   pip install --user wtf-ai
   ```

4. **Check PATH:**
   ```bash
   echo $PATH | grep -o "[^:]*python[^:]*"
   ```

### Name collision with existing `wtf` command

**Problem:** You already have a `wtf` command or alias.

**Solutions:**

The installer detects collisions automatically. If you see a warning:

```
⚠ Name collision detected!
  'wtf' is already defined in ~/.zshrc

Would you like to:
  1. Use 'wtfai' instead
  2. Use 'wai' instead
  3. Choose custom name
  4. Cancel installation
```

Pick an alternative, or manually resolve:

```bash
# Option 1: Remove old alias
vim ~/.zshrc  # Remove old 'alias wtf=...'

# Option 2: Install with different name
pip install git+https://github.com/davefowler/wtf-terminal-ai.git
ln -s $(which wtf) ~/bin/wai
```

## API Issues

### `Invalid API key`

**Problem:** wtf can't authenticate with AI provider.

**Solutions:**

1. **Re-run setup:**
   ```bash
   wtf --setup
   ```

2. **Check environment variables:**
   ```bash
   echo $ANTHROPIC_API_KEY
   echo $OPENAI_API_KEY
   echo $GOOGLE_API_KEY
   ```

3. **Set manually:**
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

4. **Get a new key:**
   - Anthropic: [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
   - OpenAI: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Google: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

### `Rate limit exceeded`

**Problem:** Too many requests to AI API.

**Solutions:**

1. **Wait a bit** - Limits reset over time
2. **Upgrade your API plan** - Free tiers have lower limits
3. **Switch providers temporarily:**
   ```bash
   wtf --setup  # Choose different provider
   ```

### `Network error`

**Problem:** Can't reach AI service.

**Solutions:**

1. **Check internet connection:**
   ```bash
   ping google.com
   ```

2. **Check service status:**
   - Anthropic: [https://status.anthropic.com](https://status.anthropic.com)
   - OpenAI: [https://status.openai.com](https://status.openai.com)

3. **Try different provider:**
   ```bash
   wtf --setup
   ```

4. **Check proxy settings** if behind corporate firewall

## Permission Issues

### Commands always ask for permission

**Problem:** wtf asks every time even after saying "yes always".

**Solutions:**

1. **Check allowlist file exists:**
   ```bash
   ls ~/.config/wtf/allowlist.json
   ```

2. **Verify pattern was added:**
   ```bash
   cat ~/.config/wtf/allowlist.json
   ```

3. **Add manually:**
   ```bash
   echo '{
     "patterns": ["git *", "npm *"],
     "denylist": []
   }' > ~/.config/wtf/allowlist.json
   ```

### wtf won't run safe commands

**Problem:** Even `git status` asks for permission.

**Cause:** Command might be chained or have redirection.

**Solutions:**

- Check command isn't chained: `git status && other` (will ask)
- Check no redirection: `git status > file` (will ask)
- Single commands should auto-execute: `git status` (won't ask)

## Shell History Issues

### wtf says "No shell history available"

**Problem:** Can't access your command history.

**Solutions:**

1. **Check history is enabled:**
   ```bash
   # For zsh
   echo $HISTFILE

   # For bash
   echo $HISTFILE
   ```

2. **Enable history:**
   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   export HISTFILE=~/.zsh_history  # or ~/.bash_history
   export HISTSIZE=10000
   export SAVEHIST=10000
   ```

3. **Check file permissions:**
   ```bash
   ls -la ~/.zsh_history
   chmod 600 ~/.zsh_history
   ```

4. **Restart shell after changes:**
   ```bash
   exec $SHELL
   ```

## Memory Issues

### wtf forgets things I told it

**Problem:** Memories not persisting.

**Solutions:**

1. **Check memories file:**
   ```bash
   cat ~/.config/wtf/memories.json
   ```

2. **Verify save worked:**
   ```bash
   wtf remember test memory
   cat ~/.config/wtf/memories.json
   ```

3. **Check file permissions:**
   ```bash
   ls -la ~/.config/wtf/
   chmod 700 ~/.config/wtf
   ```

4. **Manually fix broken file:**
   ```bash
   echo '{}' > ~/.config/wtf/memories.json
   ```

## Hook Issues

### Error hook not triggering

**Problem:** Installed error hook but nothing happens on failures.

**Solutions:**

1. **Source your shell config:**
   ```bash
   source ~/.zshrc  # or ~/.bashrc
   ```

2. **Verify hook was added:**
   ```bash
   grep -A 10 "wtf-error-hook" ~/.zshrc
   ```

3. **Re-install hook:**
   ```bash
   wtf --remove-hooks
   wtf --setup-error-hook
   ```

4. **Check shell compatibility** - Hooks work in zsh, bash, fish

## Performance Issues

### wtf is slow

**Problem:** Takes a long time to respond.

**Causes & Solutions:**

1. **Slow AI provider** - Try different model:
   ```bash
   wtf --setup  # Choose faster model
   ```

2. **Large context** - Reduce history size:
   ```bash
   # Edit ~/.config/wtf/config.json
   {
     "behavior": {
       "context_history_size": 3  # Default is 5
     }
   }
   ```

3. **Network latency** - Check connection quality

4. **Large git repo** - git status might be slow

## Security

### Is it safe to give wtf my API key?

**Yes.** Your API key is stored locally in `~/.config/wtf/config.json` (mode 600).

It's never sent anywhere except to the AI provider you chose.

**Best practices:**
1. Use API keys with spending limits
2. Don't commit `config.json` to git (it's in .gitignore)
3. Rotate keys periodically
4. Use separate keys for different tools

### Can wtf run dangerous commands?

**Mostly no, but be careful.**

**Built-in protections:**
- Denylist blocks dangerous patterns (`rm -rf /`, `dd`, etc.)
- Permission prompts for non-safe commands
- Safe readonly commands auto-execute

**You can override:**
- Allowlist can permit anything (be careful!)
- You can say "yes" to prompts

**Best practices:**
1. Review commands before saying yes
2. Don't allowlist destructive commands
3. Use denylist for commands you never want
4. Read command explanations

## Still Stuck?

1. **Check logs:**
   ```bash
   cat ~/.config/wtf/history.jsonl | tail -20
   ```

2. **Reset config:**
   ```bash
   mv ~/.config/wtf ~/.config/wtf.backup
   wtf --setup
   ```

3. **Report bug:**
   [https://github.com/davefowler/wtf-terminal-ai/issues](https://github.com/davefowler/wtf-terminal-ai/issues)

Include:
- Python version: `python --version`
- wtf version: `wtf --version`
- Shell: `echo $SHELL`
- OS: `uname -a`
- Error message and steps to reproduce
