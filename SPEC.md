# WTF Terminal AI - Technical Specification

## 1. Project Overview

**Name:** wtf
**Version:** 0.1.0
**Purpose:** A command-line AI assistant that provides contextual help based on terminal history and user queries.

### 1.1 Core Concept

Users can invoke AI assistance directly from their terminal using the `wtf` command, which intelligently understands their terminal context and provides relevant help, suggestions, or executes commands on their behalf.

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

### 2.2 Post-Installation Setup

- First run triggers interactive setup wizard
- Config directory created at `~/.config/wtf/`
- Shell integration automatically added to `.zshrc` (or `.bashrc`)

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

### 3.4 allowlist.json Schema

```json
{
  "commands": [
    "git status",
    "git log",
    "git diff",
    "ls",
    "pwd",
    "cat"
  ],
  "patterns": [
    "git status*",
    "git log*",
    "git diff*",
    "ls*"
  ]
}
```

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
   - Memories are included in agent context for every invocation
   - High-confidence memories weighted more heavily
   - Agent can reference memories in responses: "I know you prefer emacs, so..."

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

### 4.2 Context Gathering

**Automatic Context:**
- Last 5 commands from shell history (configurable)
- Current working directory
- Git repository status (if in a git repo)
- Environment variables (selective, non-sensitive)
- Agent memories (learned preferences, tools, and context)

**Command Re-execution for Context:**
When the agent needs more information, it can request to re-run recent commands to see their output:

```
I need to see the output of `git status` to help you.
May I run it? [Y/n]
```

### 4.3 Command Execution Flow

When the agent wants to execute a command:

1. **Check Allowlist:**
   - If command is in allowlist → Execute automatically (if configured)
   - If not in allowlist → Request user permission

2. **Permission Request UI:**
   ```
   Resolving merge conflict

   I need to abort the merge in progress.

   ╭─────────────────────────────────────────────╮
   │ $ git merge --abort                        │
   ╰─────────────────────────────────────────────╯

   Run this command?
   [Y]es | Yes and [a]lways allow | [n]o
   ```

3. **User Response:**
   - `Y` or `Enter`: Execute once
   - `a`: Execute and add to allowlist
   - `n`: Skip execution, continue without running

4. **Execution & Output:**
   - Run command
   - Show output to user
   - Continue with agent response

### 4.4 Response Generation

**Response Types:**

1. **Simple Answer** (no command execution needed)
   ```
   To exit vim:
   - Press ESC
   - Type :q! to quit without saving
   - Or :wq to save and quit
   ```

2. **Command Execution** (with explanation)
   ```
   You're in the middle of a merge conflict. Let me abort it for you.

   [Command execution UI]

   ✓ Merge aborted successfully. Your branch is now clean.
   ```

3. **Diagnostic** (after re-running commands)
   ```
   Based on your git status, you have 3 conflicted files:
   - src/app.py
   - src/utils.py
   - README.md

   Here's how to resolve them:
   [detailed instructions]
   ```

## 5. Conversation History & Context Management

### 5.1 History Storage Format (JSONL)

Each line in `history.jsonl` is a complete conversation session:

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

## 6. API Provider Support

### 6.1 Provider Detection & Setup

On first run, check for API keys in environment variables:
1. `ANTHROPIC_API_KEY`
2. `OPENAI_API_KEY`
3. `GOOGLE_API_KEY` or `GEMINI_API_KEY`

**If multiple keys found:**
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

**If single key found:**
```
Welcome to wtf! Let's set up your AI provider.

Checking for API keys...
✓ Found ANTHROPIC_API_KEY

Use this API key? [Y/n]
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

After provider selection, prompt for API key:
```
Please enter your Anthropic API key: _
```

### 6.2 Integration with LLM Package

Use Simon Willison's `llm` package as the backend:
- Provides unified interface across providers
- Handles API key management
- Supports multiple models
- User can leverage existing `llm` configuration
- Built-in model discovery via `llm.get_models()`

**Listing Models Programmatically:**
```python
import llm

# Get all available models
for model in llm.get_models():
    print(model.model_id)
```

**CLI Command:**
```bash
llm models  # Shows all available models
```

### 6.3 Model Configuration & Selection

After API key is configured, show available models for that provider:

```
Available models for Anthropic:
1. claude-3-5-sonnet-20241022 [recommended]
2. claude-3-opus-20240229
3. claude-3-sonnet-20240229
4. claude-3-haiku-20240307

Select a model [1]: _
```

**Default Models:**
- **Anthropic:** `claude-3-5-sonnet-20241022`
- **OpenAI:** `gpt-4o`
- **Gemini:** `gemini-pro`

**Runtime Override:**
Users can override the configured model via command line:
```bash
wtf --model gpt-4 "explain this error"
wtf --model claude-opus "review this code"
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

### 7.3 History Parsing

Handle different history formats:
- Zsh with timestamps: `: 1710509422:0;git status`
- Bash: `git status`

## 8. Command-Line Interface

### 8.1 Main Command

```bash
wtf [OPTIONS] [QUERY...]
```

### 8.2 Options

- `--help, -h`: Show help message
- `--version, -v`: Show version
- `--config`: Open config file in editor
- `--edit-instructions`: Open wtf.md in editor
- `--edit-allowlist`: Open allowlist.json in editor
- `--list-models`: Show available AI models
- `--show-memories`: Display learned preferences and context
- `--clear-memories`: Clear all learned memories
- `--history`: Show conversation history
- `--clear-history`: Clear conversation history
- `--model MODEL`: Override default model
- `--verbose`: Show detailed execution info
- `--no-execute`: Don't execute any commands (dry-run)
- `--reset`: Reset configuration to defaults

### 8.3 Examples

```bash
# Basic query
wtf how do I undo my last commit?

# Without query (context-aware)
wtf

# View history
wtf --history

# Edit custom instructions
wtf --edit-instructions

# List available models
wtf --list-models

# View learned memories
wtf --show-memories

# Use specific model
wtf --model gpt-4 "explain this docker error"

# Dry run mode
wtf --no-execute "fix my git merge"
```

## 9. Error Handling

### 9.1 API Errors

- Network failures: Retry with exponential backoff
- Rate limits: Show clear message, suggest waiting
- Invalid API key: Prompt to reconfigure

### 9.2 Command Execution Errors

- Permission denied: Explain and suggest alternatives
- Command not found: Offer to install or suggest alternatives
- Non-zero exit code: Show error output to AI for analysis

### 9.3 Configuration Errors

- Corrupt config: Offer to reset to defaults
- Missing config: Create automatically
- Invalid syntax: Show specific error and fix suggestion

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

## 11. Testing Strategy

### 11.1 Unit Tests

- Configuration loading/saving
- History parsing (zsh/bash formats)
- Command allowlist matching
- Context gathering

### 11.2 Integration Tests

- Full command execution flow
- API provider integration (mocked)
- Shell history reading
- Conversation continuity

### 11.3 E2E Tests

- Complete user flows
- Installation process
- First-run configuration
- Command execution with permission prompts

## 12. Future Enhancements (Out of Scope for v0.1)

- Support for fish shell
- Integration with terminal multiplexers (tmux, screen)
- Plugin system for custom commands
- Web dashboard for history visualization
- Team/shared allowlists
- Streaming responses for long outputs
- Voice input support
- Integration with terminal emulators for better UI
