# Using Claude Code Safely with Sandbox Runtime

This guide explains how to use Claude Code in "dangerous mode" (full agent capabilities) safely using Anthropic's [sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime).

## What is Sandbox Runtime?

`srt` (sandbox runtime) is Anthropic's tool that Claude Code uses under the hood to:
- **Restrict filesystem access** (read/write only to approved paths)
- **Filter network requests** (only allow approved domains)
- **Monitor violations** (catch unauthorized access attempts)

It's designed specifically for AI agents to prevent them from:
- Reading your SSH keys or cloud credentials
- Writing to system directories
- Accessing arbitrary websites
- Modifying files outside the project

## Setup

### 1. Install Sandbox Runtime (if not auto-installed by Claude Code)

```bash
npm install -g @anthropic-ai/sandbox-runtime
```

**Linux users also need:**
```bash
# Ubuntu/Debian
sudo apt-get install bubblewrap socat ripgrep

# Arch
sudo pacman -S bubblewrap socat ripgrep
```

**macOS users also need:**
```bash
brew install ripgrep
```

### 2. Verify Installation

```bash
srt "echo hello"
# Should output: hello
```

## Configuration for WTF Development

This repo includes `.sandbox-config.json` which defines development-friendly permissions:

```json
{
  "permissions": {
    "allow": [
      "Edit(.)",           // Can write to project directory
      "Read(.)",           // Can read project directory
      "Edit(/tmp)",        // Can write to /tmp (tests, temp files)
      "Edit(/var/tmp)",    // Can write to /var/tmp
      "Read(/usr)",        // Can read system Python, libraries
      "Read(/Library)",    // Can read macOS system libraries
      "WebFetch(domain:pypi.org)",      // Install Python packages
      "WebFetch(domain:anthropic.com)", // AI API
      "WebFetch(domain:openai.com)",    // AI API
      "WebFetch(domain:github.com)"     // Git operations
    ],
    "deny": [
      "Edit(~/.ssh)",           // Can't modify SSH config
      "Edit(~/.bashrc)",        // Can't modify shell config
      "Read(~/.ssh/id_rsa)",    // Can't read SSH keys
      "Read(~/.aws/credentials)", // Can't read AWS credentials
      "Read(~/.docker/config.json)" // Can't read Docker creds
    ]
  }
}
```

### Key Design Decisions

**Permissive for development:**
- ✅ Full access to project directory
- ✅ /tmp and /var/tmp for tests and temporary files
- ✅ Read access to system libraries (Python, etc.)
- ✅ All network domains needed for development

**Strict on credentials:**
- ❌ All SSH keys blocked
- ❌ All cloud credentials blocked (AWS, GCP, Docker)
- ❌ Shell config files blocked (prevents code execution persistence)

This balance lets Python, pip, pytest, git, and all development tools work normally while preventing credential theft.

### What This Allows

✅ **All development operations:**
- Create/modify files in project directory
- Write to /tmp and /var/tmp (for tests, temp files)
- Read system libraries (/usr, /Library, etc.)
- Install Python packages from PyPI
- Run Python, pip, pytest, coverage, all dev tools
- Make API calls to Anthropic, OpenAI, Google AI
- Git operations (push, pull, clone)
- Run tests with temp files
- Create virtual environments
- Read any file (except explicitly denied credentials)

❌ **Only credentials blocked:**
- Reading SSH private keys (~/.ssh/id_*)
- Reading cloud credentials (~/.aws, ~/.config/gcloud)
- Reading Docker credentials (~/.docker/config.json)
- Modifying shell config files (prevents persistence attacks)
- Network requests to non-approved domains

## Using Claude Code with Sandbox

### Option 1: Automatic (Recommended)

Claude Code automatically detects `.sandbox-config.json` and uses it. Just:

1. Open Claude Code web interface
2. Give it the prompt from `CLAUDE_CODE_PROMPT.md`
3. It will run sandboxed automatically

### Option 2: Manual Testing

Test sandbox restrictions before giving to Claude Code:

```bash
# This should work (in project directory)
srt "touch test.txt"

# This should be blocked (outside project)
srt "touch /tmp/test.txt"

# This should be blocked (reading SSH key)
srt "cat ~/.ssh/id_rsa"

# This should work (installing package)
srt "pip install rich"
```

## Monitoring Violations

### macOS

Real-time violation monitoring:
```bash
log stream --predicate 'process == "sandbox-exec"' --style syslog
```

Run this in a separate terminal while Claude Code works. You'll see:
```
sandbox-exec[1234]: Sandbox: python(5678) deny(1) file-read-data /Users/you/.ssh/id_rsa
```

### Linux

Use `strace` to see blocked operations:
```bash
strace -f srt "cat ~/.ssh/id_rsa" 2>&1 | grep EPERM
```

## Adjusting Permissions

If Claude Code needs access to something legitimate, update `.sandbox-config.json`:

### Example: Allow access to a specific directory

```json
{
  "permissions": {
    "allow": [
      "Edit(.)",
      "Edit(/tmp/wtf-test)",  // Add this
      "Read(.)"
    ]
  }
}
```

### Example: Allow a new API domain

```json
{
  "permissions": {
    "allow": [
      "WebFetch(domain:pypi.org)",
      "WebFetch(domain:docs.python.org)"  // Add this
    ]
  }
}
```

After updating, restart Claude Code or re-run the sandboxed command.

## Common Issues

### Issue: Command fails with "Operation not permitted"

**Cause:** Sandbox blocking the operation

**Solution:** 
1. Check if operation is legitimate
2. If yes, add permission to `.sandbox-config.json`
3. If no, the sandbox is working correctly!

### Issue: "Command not found: srt"

**Cause:** Sandbox runtime not installed

**Solution:**
```bash
npm install -g @anthropic-ai/sandbox-runtime
```

### Issue: Linux bubblewrap errors

**Cause:** Missing dependencies

**Solution:**
```bash
sudo apt-get install bubblewrap socat ripgrep
```

### Issue: Can't install packages

**Cause:** PyPI domain not allowed

**Solution:** Already in `.sandbox-config.json` - make sure it's loaded

## Security Best Practices

### ✅ DO:
- Keep the default deny list (SSH keys, credentials)
- Review Claude Code's proposed commands before approving
- Monitor violations log during development
- Start with minimal permissions, add as needed
- Test sandbox config before long-running tasks

### ❌ DON'T:
- Allow broad write access outside project (`Edit(~)`)
- Allow all network domains (`WebFetch(domain:*)`)
- Disable sandbox for convenience
- Allow write access to `.bashrc` or `.zshrc` (code execution risk)
- Allow access to Docker socket without careful consideration

## Advanced: Custom Proxy for Traffic Inspection

For paranoid security, use a MITM proxy to inspect all network traffic:

```bash
# Install mitmproxy
pip install mitmproxy

# Start with custom filtering
mitmproxy -s custom_filter.py --listen-port 8888
```

Update `.sandbox-config.json`:
```json
{
  "sandbox": {
    "network": {
      "httpProxyPort": 8888
    }
  }
}
```

Now you can see and block specific API calls (e.g., allow GitHub reads but block pushes).

## Why This Matters

Building wtf is meta: you're building an AI agent that executes commands. The irony of using an AI agent (Claude Code) to build it isn't lost on us.

Sandbox runtime ensures:
1. Claude Code can't accidentally leak your credentials
2. Bugs in Claude Code don't compromise your system
3. You can confidently use "dangerous mode" (full agent capabilities)
4. Failed experiments don't escape the project directory

This is the same safety system Claude Code uses for all users. By using it explicitly, you get:
- **Transparency**: See exactly what's allowed/denied
- **Control**: Adjust permissions for your use case
- **Confidence**: Know the AI can't do anything harmful

## Testing the Sandbox

Before giving Claude Code the full prompt, test the sandbox:

```bash
# Should succeed (project file)
srt "cat SPEC.md" | head -n 5

# Should succeed (installing package)
srt "pip install rich --dry-run"

# Should fail (SSH key)
srt "cat ~/.ssh/id_rsa"

# Should fail (outside project)
srt "rm -rf /tmp/*"

# Should succeed (allowed domain)
srt "curl https://pypi.org"

# Should fail (blocked domain)
srt "curl https://evil.com"
```

If all tests pass, you're good to go with Claude Code!

## Summary

**TL;DR:**
1. Install: `npm install -g @anthropic-ai/sandbox-runtime`
2. Config already exists: `.sandbox-config.json`
3. Claude Code uses it automatically
4. Monitor with: `log stream` (macOS) or `strace` (Linux)
5. Adjust permissions only if legitimately needed

**You can now safely use Claude Code in "dangerous mode" to build wtf.** 🎉

The sandbox ensures that even if Claude Code goes rogue or makes mistakes, it:
- ✅ Can build the project
- ✅ Can run tests
- ✅ Can commit and push
- ❌ Can't steal your credentials
- ❌ Can't modify system files
- ❌ Can't exfiltrate data to arbitrary domains

---

For more details: https://github.com/anthropic-experimental/sandbox-runtime

