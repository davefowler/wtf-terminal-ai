# WTF v0.1 - Task Breakdown for AI Implementation

**How to use this:** Give each task to Claude-Code one at a time. Each task is self-contained and creates specific files.

---

## 🤖 Instructions for AI Agent

**Workflow:**
1. Read SPEC.md first to understand the full context
2. Work through tasks in order (1 → 32)
3. Create/modify files as specified in each task
4. After completing each task, show me what you did
5. **Commit after each MILESTONE** (not after each task)
6. Run the code after each milestone to verify it works

**Git Workflow:**
- ✅ **DO commit** after completing each milestone (tasks 1-2, 3-4, 5-7, etc.)
- ✅ **DO push** after each milestone is tested and working
- ❌ **DON'T commit** after every single task (too granular)
- ❌ **DON'T push** code that hasn't been tested

**Commit message format:**
```
feat: [MILESTONE NAME] - brief description

- Task X: what was done
- Task Y: what was done

Milestone X/11 complete
```

**Testing strategy:**
- After milestone 1: Test that `wtf --help` works
- After milestone 2: Test that config gets created
- After milestone 3: Test that context gathering works
- After milestone 4: Test that AI responds
- After milestone 5: Test that commands execute with permissions
- And so on...

**If you get stuck:**
- Check SPEC.md for implementation details
- Look at the acceptance criteria
- Ask me for clarification
- Don't make up behavior - stick to the spec

**Progress tracking:**
- At the start of each milestone, say: "Starting Milestone X: [NAME]"
- After each task, say: "✅ Task X complete"
- After each milestone, say: "🎉 Milestone X complete. Ready to commit."

**Code quality:**
- Add type hints to all functions (Python 3.10+)
- Add docstrings to public functions
- Keep functions focused and small
- Extract duplicated logic
- Use `rich` for all terminal output
- Handle errors gracefully

**What NOT to do:**
- Don't skip tasks or milestones
- Don't deviate from the spec
- Don't add features not in the spec
- Don't commit broken code
- Don't make assumptions - refer to SPEC.md

---

## 🟢 MILESTONE 1: "Hello World" (Can run wtf --help)

### Task 1: Initialize Python Project Structure
**Files to create:**
```
wtf/
  __init__.py
  __main__.py
  cli.py
tests/
  __init__.py
pyproject.toml
requirements.txt
.gitignore
LICENSE
README.md
```

**Acceptance criteria:**
- [ ] Can run `python -m wtf` without errors
- [ ] `pyproject.toml` has correct metadata (name: wtf-ai, version: 0.1.0)
- [ ] `LICENSE` contains MIT license text
- [ ] `README.md` has basic installation instructions
- [ ] `.gitignore` covers Python (*.pyc, __pycache__, .env, etc.)

**Requirements.txt should include:**
```
anthropic>=0.18.0
openai>=1.12.0
google-generativeai>=0.3.0
llm>=0.13.0
rich>=13.7.0
```

---

### Task 2: Implement Basic CLI with Help Output
**Files to modify:**
- `wtf/cli.py` - Implement argument parsing and --help
- `wtf/__main__.py` - Entry point that calls cli.main()

**Acceptance criteria:**
- [ ] `wtf --help` displays the full hilarious help message from SPEC.md section 8.3
- [ ] `wtf --version` prints "wtf 0.1.0"
- [ ] `wtf` with no args prints "Not implemented yet"
- [ ] `wtf "any query"` prints "Not implemented yet"

**Use `rich.console.Console` for output formatting**

---

## 🟢 MILESTONE 2: "Config Works" (Can create and load config)

### Task 3: Create Configuration System
**Files to create:**
- `wtf/core/__init__.py`
- `wtf/core/config.py`

**What `config.py` needs:**
- `get_config_dir()` → returns `~/.config/wtf/`
- `create_default_config()` → creates config.json, allowlist.json, wtf.md
- `load_config()` → loads config.json with validation
- `save_config(config_dict)` → saves with backup
- Default config structure (from SPEC.md section 3.1)

**Acceptance criteria:**
- [ ] First run creates `~/.config/wtf/` directory
- [ ] Creates `config.json` with defaults
- [ ] Creates `allowlist.json` as `{"patterns": [], "denylist": []}`
- [ ] Creates `wtf.md` template for custom instructions
- [ ] `load_config()` returns dict with all expected keys
- [ ] Backup created before overwriting config

---

### Task 4: Implement Interactive Setup Wizard
**Files to modify:**
- `wtf/cli.py` - Add setup wizard on first run

**What it needs to do:**
1. Detect if config exists, if not run setup
2. Ask for API provider (Anthropic, OpenAI, Google)
3. Ask for API key (with validation)
4. Ask for default model
5. Save to config.json
6. Print success message

**Acceptance criteria:**
- [ ] First run prompts for setup
- [ ] Can configure Anthropic with API key
- [ ] Can configure OpenAI with API key
- [ ] Config saved successfully
- [ ] `wtf --setup` reruns setup wizard

---

## 🟢 MILESTONE 3: "Has Context" (Can gather shell history and git status)

### Task 5: Implement Shell Detection and History Gathering
**Files to create:**
- `wtf/context/__init__.py`
- `wtf/context/shell.py`

**What `shell.py` needs:**
- `detect_shell()` → returns "zsh", "bash", "fish", or "unknown"
- `get_shell_history(count=5)` → returns list of recent commands
  - Try `fc -ln -count` first
  - Fall back to file parsing if that fails
- `HistoryFailureReason` enum (from SPEC.md section 13)
- `build_history_context(failure_reason, shell_type)` → returns context string for AI

**Acceptance criteria:**
- [ ] Detects current shell correctly
- [ ] `get_shell_history(5)` returns list of 5 recent commands
- [ ] Returns empty list + failure reason if history unavailable
- [ ] Works in zsh
- [ ] Works in bash
- [ ] Handles "history disabled" case gracefully

---

### Task 6: Implement Git Context Gathering
**Files to create:**
- `wtf/context/git.py`

**What `git.py` needs:**
- `is_git_repo(path)` → bool
- `get_git_status(path)` → dict with:
  - `branch`: current branch name
  - `status`: output of `git status --short`
  - `has_changes`: bool
  - `ahead_behind`: commits ahead/behind remote
- Returns None if not a git repo

**Acceptance criteria:**
- [ ] Detects if current directory is git repo
- [ ] Returns current branch name
- [ ] Returns short status
- [ ] Returns None if not a git repo
- [ ] Doesn't crash if git not installed

---

### Task 7: Implement Environment Detection
**Files to create:**
- `wtf/context/env.py`

**What `env.py` needs:**
- `detect_project_type(path)` → returns "python", "node", "ruby", "go", "rust", "unknown"
  - Look for: requirements.txt, package.json, Gemfile, go.mod, Cargo.toml
- `get_environment_context()` → dict with:
  - `cwd`: current working directory
  - `project_type`: detected type
  - `project_files`: list of relevant files found

**Acceptance criteria:**
- [ ] Detects Python projects (requirements.txt, pyproject.toml)
- [ ] Detects Node projects (package.json)
- [ ] Returns cwd
- [ ] Returns list of config files found

---

## 🟢 MILESTONE 4: "AI Responds" (Can send context to AI and get response)

### Task 8: Integrate LLM Library
**Files to create:**
- `wtf/ai/__init__.py`
- `wtf/ai/client.py`

**What `client.py` needs:**
- `query_ai(prompt, model=None, stream=True)` → generator or string
- Uses `llm` library (Simon Willison's package)
- Loads API keys from config (or uses `llm`'s own config)
- Handles streaming responses
- Falls back to non-streaming if not supported

**Implementation note:**
The `llm` library handles:
- All API provider differences (Anthropic, OpenAI, Google)
- Local model support via plugins (no special code needed)
- API key management (can use `llm keys set` or our config)
- Streaming, rate limiting, retries

We just need a thin wrapper that:
1. Calls `llm.get_model(model_name)`
2. Calls `model.prompt(prompt, stream=True)`
3. Yields/returns the response

**Acceptance criteria:**
- [ ] Can query Anthropic Claude
- [ ] Can query OpenAI GPT
- [ ] Can query local models (if user has plugins installed)
- [ ] Returns streaming response (generator)
- [ ] Handles non-streaming fallback
- [ ] Respects model override from config

---

### Task 9: Create System Prompts
**Files to create:**
- `wtf/ai/prompts.py`

**What `prompts.py` needs:**
- `build_system_prompt()` → full system prompt from SPEC.md section 5.4
- `build_context_prompt(history, git_status, env, memories)` → context section
- `load_custom_instructions()` → reads wtf.md if exists
- Includes Gilfoyle/Marvin personality instructions
- Includes UNDO instructions from SPEC.md section 4.1.1

**Acceptance criteria:**
- [ ] System prompt matches SPEC.md section 5.4
- [ ] Includes custom instructions from wtf.md
- [ ] Includes shell history in context
- [ ] Includes git status in context
- [ ] Includes UNDO handling instructions

---

### Task 10: Wire Up Context → AI → Output
**Files to modify:**
- `wtf/cli.py` - Main flow

**What it needs to do:**
1. Parse user query from args
2. Gather context (shell history, git status, env)
3. Build prompt with context
4. Query AI
5. Print response with streaming

**Acceptance criteria:**
- [ ] `wtf "test query"` sends query to AI
- [ ] Response streams to terminal
- [ ] Shell history included in context
- [ ] Git status included in context (if in repo)
- [ ] Handles API errors gracefully

---

## 🟢 MILESTONE 5: "Can Execute Commands" (Permission system + execution)

### Task 11: Implement Permission System
**Files to create:**
- `wtf/core/permissions.py`

**What `permissions.py` needs:**
- `load_allowlist()` → loads patterns from allowlist.json
- `load_denylist()` → loads patterns from allowlist.json's denylist array
- `is_command_allowed(cmd, allowlist)` → bool
- `is_command_denied(cmd, denylist)` → bool
- `prompt_for_permission(cmd, explanation)` → "yes", "yes_always", "no"
  - Shows command in nice box (using `rich`)
  - Offers [Y]es / Yes and [a]lways / [n]o
- `add_to_allowlist(pattern)`

**Acceptance criteria:**
- [ ] Loads allowlist patterns
- [ ] Matches commands by prefix
- [ ] Shows permission prompt with formatted box
- [ ] Handles user input (y/a/n)
- [ ] Can add pattern to allowlist
- [ ] Denies if in denylist (overrides allowlist)

---

### Task 12: Implement Safe Read-Only Commands
**Files to modify:**
- `wtf/core/permissions.py`

**What to add:**
- `SAFE_READONLY_COMMANDS` set (from SPEC.md section 3.4.1)
- `is_safe_readonly_command(cmd)` → bool
  - Checks if command in safe set
  - Also checks no chaining (`&&`, `||`, `;`, `$()`, etc.)
  - Checks no redirection (`>`, `>>`, `|`)
- `should_auto_execute(cmd, allowlist, denylist)` → "auto", "ask", "deny"
  - Priority: denylist > safe_readonly > allowlist > ask

**Acceptance criteria:**
- [ ] `command -v node` is auto-allowed
- [ ] `git status` is auto-allowed
- [ ] `cat package.json` is auto-allowed
- [ ] `rm file.txt` is NOT auto-allowed
- [ ] `git status && rm file` is NOT auto-allowed (chaining detected)

---

### Task 13: Implement Command Execution
**Files to create:**
- `wtf/core/executor.py`

**What `executor.py` needs:**
- `execute_command(cmd, timeout=30)` → tuple (stdout+stderr, exit_code)
- Uses `subprocess.run()` with timeout
- Captures stdout and stderr
- Shows spinner while running (using `rich.spinner`)
- Handles timeouts gracefully

**Acceptance criteria:**
- [ ] Executes commands with timeout
- [ ] Captures output
- [ ] Returns exit code
- [ ] Shows spinner for long commands
- [ ] Timeout shows helpful error

---

### Task 14: Implement Command Security Checks
**Files to create:**
- `wtf/utils/__init__.py`
- `wtf/utils/security.py`

**What `security.py` needs:**
- `is_command_chained(cmd)` → bool (checks for `;`, `&&`, `||`, `$()`, backticks)
- `is_command_dangerous(cmd)` → bool (checks against dangerous patterns)
- `DANGEROUS_PATTERNS` list from SPEC.md section 3.4.2

**Acceptance criteria:**
- [ ] Detects `&&` chaining
- [ ] Detects `;` chaining
- [ ] Detects command substitution `$()`
- [ ] Detects dangerous patterns (`rm -rf /`, `dd if=`, etc.)
- [ ] Returns False for safe single commands

---

### Task 15: Parse AI Response for Commands
**Files to create:**
- `wtf/ai/response_parser.py`

**What `response_parser.py` needs:**
- `extract_commands(ai_response)` → list of dicts
  - Each dict: `{command: str, explanation: str, allowlist_pattern: str}`
- Handle both structured (JSON-ish) and unstructured responses
- Look for command boxes in markdown (```bash blocks or ╭─ boxes)

**Acceptance criteria:**
- [ ] Extracts commands from AI response
- [ ] Parses explanation text
- [ ] Extracts allowlist pattern suggestion
- [ ] Handles multiple commands in one response
- [ ] Handles plain text responses without commands

---

### Task 16: Wire Up Full Execution Flow
**Files to modify:**
- `wtf/cli.py` - Connect AI response → permission → execution

**What it needs to do:**
1. Get AI response
2. Parse for commands
3. For each command:
   - Check if auto-executable (safe readonly / allowlist)
   - If not, prompt for permission
   - If approved, execute command
   - Show output
   - Continue to next command or query AI with results

**Acceptance criteria:**
- [ ] AI suggests command → shows permission prompt
- [ ] User approves → command executes
- [ ] Output displayed
- [ ] Safe commands auto-execute without prompt
- [ ] Denied commands don't execute
- [ ] Can add pattern to allowlist with [a]

---

## 🟢 MILESTONE 6: "Multi-Step Works" (State machine)

### Task 17: Implement Conversation State Machine
**Files to create:**
- `wtf/conversation/__init__.py`
- `wtf/conversation/state.py`

**What `state.py` needs:**
- `ConversationState` enum (from SPEC.md section 11.1)
- `ConversationContext` dataclass (from SPEC.md section 11.3)
- `ConversationStateMachine` class (from SPEC.md section 11.3)
  - `__init__(context)`
  - `run()` → executes state machine loop
  - `_execute_current_state()` → handles each state
  - State-specific methods for each state

**Acceptance criteria:**
- [ ] State machine transitions through states
- [ ] INITIALIZING → QUERYING_AI → STREAMING_RESPONSE
- [ ] AWAITING_PERMISSION → EXECUTING_COMMAND
- [ ] Handles multi-step flows
- [ ] Error state catches exceptions

---

### Task 18: Refactor CLI to Use State Machine
**Files to modify:**
- `wtf/cli.py` - Replace linear flow with state machine

**What to change:**
- Create `ConversationContext` with all gathered info
- Instantiate `ConversationStateMachine`
- Call `state_machine.run()`
- Let state machine handle the flow

**Acceptance criteria:**
- [ ] CLI uses state machine for all operations
- [ ] Multi-step commands work
- [ ] Can execute → get output → query AI again → execute more
- [ ] State machine handles errors

---

## 🟢 MILESTONE 7: "Remembers Things" (History & Memory)

### Task 19: Implement Conversation History (JSONL)
**Files to create:**
- `wtf/conversation/history.py`

**What `history.py` needs:**
- `append_to_history(conversation_dict)` → appends to history.jsonl
- `get_recent_conversations(count=10)` → reads last N from file
- `maybe_rotate_history()` → rotates if > 10MB
- `cleanup_old_history(keep_n=5)` → removes old rotation files

**Format (from SPEC.md section 5.1):**
```json
{"timestamp": "...", "query": "...", "response": "...", "commands": [...], "exit_code": 0}
```

**Acceptance criteria:**
- [ ] Appends to history.jsonl after each conversation
- [ ] Can read recent conversations
- [ ] Rotates file when > 10MB
- [ ] Keeps last 5 rotated files
- [ ] Efficient reading from end of file

---

### Task 20: Implement Memory System
**Files to create:**
- `wtf/conversation/memory.py`

**What `memory.py` needs:**
- `extract_memory(ai_response)` → looks for memory instructions in response
- `save_memory(key, value, confidence)` → saves to memories.json
- `load_memories()` → returns dict of all memories
- `search_memories(query)` → finds relevant memories
- `delete_memory(key)` → removes memory
- `clear_recent_history(count=5)` → removes last N history entries

**Acceptance criteria:**
- [ ] AI can say "I'll remember that you prefer X"
- [ ] Memory saved to memories.json
- [ ] Memories included in future prompts
- [ ] `wtf show me what you remember` lists memories
- [ ] `wtf forget about X` removes memory
- [ ] `wtf forget everything we just did` clears recent history

---

### Task 21: Add Natural Language Memory Commands & Self-Configuration
**Files to modify:**
- `wtf/ai/prompts.py` - Add memory + self-config instructions to system prompt
- `wtf/cli.py` - Handle memory queries and meta commands
- `wtf/core/config.py` - Add personality loading/saving

**What to add:**

**Memory commands:**
- Detect "remember" in user query → extract and save
- Detect "show me what you remember" → list memories
- Detect "forget about" → delete memory
- Detect "forget everything we just did" → clear recent history

**Personality commands:**
- Detect "change your personality to X" → write to personality.txt
- Detect "be more X" → write personality instructions
- Detect "reset your personality" → delete personality.txt
- `load_personality()` → reads personality.txt if exists

**Permission commands:**
- Detect "give yourself permission to X" → add to allowlist with warning
- Detect "allow X without asking" → add to allowlist
- Detect "stop auto-running X" → remove from allowlist

**Acceptance criteria:**
- [ ] `wtf remember I use emacs` saves memory
- [ ] `wtf show me what you remember` lists all memories
- [ ] `wtf forget about my editor preference` removes it
- [ ] `wtf forget everything we just did` clears recent history
- [ ] `wtf change your personality to be more encouraging` creates personality.txt
- [ ] `wtf reset your personality` deletes personality.txt
- [ ] `wtf allow git commands` adds to allowlist with warning
- [ ] All meta commands show what they changed
- [ ] Memories and personality persist across sessions

---

## 🟢 MILESTONE 8: "Handles Errors Well" (Error handling & recovery)

### Task 22: Implement Error Handling & Retry Logic
**Files to create:**
- `wtf/ai/errors.py`

**What `errors.py` needs:**
- `RateLimitError` exception
- `NetworkError` exception
- `InvalidAPIKeyError` exception
- `query_ai_with_retry(prompt, max_retries=3)` wrapper
- Exponential backoff: 1s, 2s, 4s
- Parse error responses from API providers

**Acceptance criteria:**
- [ ] Retries on network failure
- [ ] Shows rate limit wait time
- [ ] Shows helpful error for invalid API key
- [ ] Exponential backoff works
- [ ] Max retries respected

---

### Task 23: Add Progress Indicators
**Files to modify:**
- All files that have long operations

**What to add:**
- Use `rich.console.status()` for spinners
- "🔍 Gathering context..." when gathering context
- "🤖 Thinking..." when querying AI
- "⚙️ Running command..." when executing
- Only show for operations > 1 second

**Acceptance criteria:**
- [ ] Spinners show for long operations
- [ ] Don't show for quick operations
- [ ] Use subtle emoji + text
- [ ] Spinner stops when operation completes

---

### Task 24: Improve Error Messages
**Files to modify:**
- All error handling code

**What to improve:**
- Network error → show "Can't reach API" + retry info
- Timeout → show "Command timed out" + alternatives
- API key error → show how to fix + link to get key
- Permission denied → show why + suggest fix
- All errors should be helpful, not just stack traces

**Acceptance criteria:**
- [ ] All errors show actionable fix
- [ ] No raw exceptions shown to user
- [ ] Maintains Gilfoyle/Marvin personality in errors
- [ ] Includes links where helpful

---

## 🟢 MILESTONE 9: "Undo Works" (The killer feature)

### Task 25: Implement "wtf undo" Feature
**Files to modify:**
- `wtf/ai/prompts.py` - Add UNDO section to system prompt (from SPEC.md 4.1.1)

**What to add to system prompt:**
```
UNDO REQUESTS:
When user says "undo", "undo that", "undo this [action]":
1. Look at recent shell history (last 10-20 commands)
2. Identify what action they want to undo
3. Determine how to reverse it safely
4. Propose the undo commands
[Full prompt from SPEC.md section 4.1.1]
```

**Acceptance criteria:**
- [ ] `wtf undo` analyzes last command and suggests reversal
- [ ] Works for git commits (git reset --soft HEAD~1)
- [ ] Works for file deletions (git checkout HEAD -- file)
- [ ] Works for npm installs (npm uninstall package)
- [ ] Explains what it's undoing
- [ ] Asks permission before undoing

---

## 🟢 MILESTONE 10: "Install Friendly" (Setup & collision detection)

### Task 26: Implement Name Collision Detection
**Files to create:**
- `wtf/setup/__init__.py`
- `wtf/setup/collision.py`

**What `collision.py` needs:**
- `detect_wtf_collision()` → dict with collision info (from SPEC.md 2.2)
- Check shell config files (~/.zshrc, ~/.bashrc, etc.)
- Check for common VCS aliases (git, hg, svn)
- Return collision type, location, line number
- `handle_collision(collision_info)` → prompt user for resolution

**Acceptance criteria:**
- [ ] Detects existing `alias wtf='git status'`
- [ ] Detects wtf functions
- [ ] Shows collision during setup
- [ ] Offers alternatives (wtfai, wai, custom)
- [ ] Can create symlink for alternative name

---

### Task 27: Add Shell Hook Setup (Optional)
**Files to create:**
- `wtf/setup/hooks.py`

**What `hooks.py` needs:**
- `setup_error_hook(shell_type)` → adds preexec/PROMPT_COMMAND hook
- `setup_not_found_hook(shell_type)` → adds command_not_found_handler
- `remove_hooks(shell_type)` → removes wtf hooks from shell config
- Shell-specific implementations (zsh, bash)

**Acceptance criteria:**
- [ ] `wtf --setup-error-hook` adds hook to ~/.zshrc
- [ ] Hook triggers wtf on command failures
- [ ] `wtf --remove-hooks` removes hooks cleanly
- [ ] Works in zsh and bash

---

## 🟢 MILESTONE 11: "Production Ready" (Tests + docs)

### Task 28: Write Unit Tests
**Files to create:**
- `tests/test_config.py`
- `tests/test_history.py`
- `tests/test_permissions.py`
- `tests/test_security.py`
- `tests/test_state_machine.py`
- `tests/test_meta_commands.py` (see SPEC.md for full test file)

**What to test:**
- Config loading/saving
- History parsing (zsh, bash formats)
- Allowlist pattern matching
- Command chaining detection
- Dangerous command detection
- State machine transitions
- **Meta commands (self-configuration):**
  - Memory: remember, show, forget
  - Personality: change, reset
  - Permissions: allow, deny
  
**Testing approach:**
- Unit tests: Mock AI responses
- Integration tests: Run against real AI (when API key available)
- Meta command tests use real AI to verify end-to-end behavior

**Example meta command tests:**
```python
def test_remember_command():
    result = main(["remember", "my", "name", "is", "dave"])
    memories = load_memories()
    assert "dave" in json.dumps(memories).lower()

def test_personality_change():
    result = main(["be", "more", "encouraging"])
    personality = load_personality()
    assert "encouraging" in personality.lower()
```

**Acceptance criteria:**
- [ ] All core modules have unit tests
- [ ] Meta commands have integration tests
- [ ] Tests run with `pytest`
- [ ] Integration tests skip if no API key
- [ ] Coverage > 70%

---

### Task 29: Write Integration Tests
**Files to create:**
- `tests/integration/test_full_flow.py`

**What to test:**
- Full conversation flow with mocked AI
- Multi-step execution
- Permission prompts
- Error recovery

**Acceptance criteria:**
- [ ] Can run full flow end-to-end
- [ ] Tests work with mocked AI responses
- [ ] All major flows covered

---

### Task 30: Set Up Documentation Site
**Files to create:**
- `docs/index.md` (from SPEC.md section 12.4)
- `docs/faq.md` (from SPEC.md)
- `docs/getting-started.md`
- `docs/allowlist.md`
- `docs/troubleshooting.md`
- `docs/comparison.md`
- `docs/acknowledgments.md`
- `mkdocs.yml` (from SPEC.md section 12.2)

**Acceptance criteria:**
- [ ] All doc pages created with Gilfoyle/Marvin personality
- [ ] MkDocs builds without errors
- [ ] Material theme applied
- [ ] Can view locally with `mkdocs serve`

---

### Task 31: Create README.md
**Files to modify:**
- `README.md` - Write full README (from SPEC.md section 12.5)

**What to include:**
- Project description
- Quick installation
- 30-second tour with examples
- Key features
- Link to full docs
- Requirements
- Contributing
- License
- Acknowledgments to influencing projects

**Acceptance criteria:**
- [ ] README is comprehensive but concise
- [ ] Includes "Made a mistake? Just say wtf undo" callout
- [ ] Links to docs site
- [ ] Credits tAI, Aider, etc.

---

### Task 32: Release Preparation
**Files to create:**
- `CHANGELOG.md` - v0.1.0 release notes
- GitHub release

**What to do:**
- Test installation via `pip install -e .`
- Create git tag `v0.1.0`
- Write release notes
- Build package for PyPI
- Test package installation

**Acceptance criteria:**
- [ ] Can install via pip
- [ ] All features work after install
- [ ] Help output correct
- [ ] Setup wizard works

---

## 🎯 Critical Path (Minimum Working Version)

If you want the absolute minimum to be functional:

**Day 1 tasks:** 1, 2, 3, 4
**Day 2 tasks:** 5, 6, 7, 8, 9, 10
**Day 3 tasks:** 11, 12, 13, 14, 15, 16

After these 16 tasks, you have a working `wtf` that can:
- Take queries
- Gather context
- Ask AI
- Execute commands with permissions
- Handle safe read-only commands

Everything else is enhancement. But the state machine (task 17-18) is highly recommended for reliability.

---

## Tips for AI Implementation

**For Claude-Code:**
1. Give it one task at a time
2. Always include "refer to SPEC.md section X.Y" in the task
3. Ask it to show you the files it created/modified
4. Test after each task before moving to next
5. If a task is too big, break it down further

**Good task format:**
```
Implement Task 5: Shell Detection and History Gathering

Create wtf/context/shell.py with the following functions:
- detect_shell() that returns "zsh", "bash", "fish", or "unknown"
- get_shell_history(count=5) that tries fc command first, falls back to file parsing

Refer to SPEC.md section 7.3 for full implementation details.

Acceptance criteria:
- Works in zsh
- Works in bash  
- Returns empty list if history unavailable
```

**After each task:**
1. Review the code
2. Test it manually
3. Fix any issues
4. Then move to next task

---

## Progress Tracking

Create a GitHub project or checklist to track progress. Each task = 1 checkbox.

Estimated total time: 15-25 hours of implementation (spread over however long)

**You got this!** 🚀

