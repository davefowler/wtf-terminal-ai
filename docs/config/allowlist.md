# Allowlist - Commands wtf Can Run

The allowlist lets you control which commands wtf can execute without asking for permission.

## How It Works

When wtf wants to run a command, it checks:

1. **Denylist first** - Is it explicitly forbidden?
2. **Safe readonly commands** - Is it a safe command like `ls` or `git status`?
3. **Allowlist** - Did you previously approve it?
4. **Ask** - If none of the above, prompt you

## Location

`~/.config/wtf/allowlist.json`

## Format

```json
{
  "patterns": [
    "git *",
    "npm install*",
    "cat *"
  ],
  "denylist": [
    "rm -rf*",
    "dd*"
  ]
}
```

## Adding to Allowlist

### Interactively

When wtf asks for permission, press `a` for "Yes and always":

```
╭──────────────────────────────────╮
│ Permission Required              │
├──────────────────────────────────┤
│ Command: git push origin main    │
│                                  │
│ [y] Yes, once                    │
│ [a] Yes, and always allow        │
│ [n] No                           │
╰──────────────────────────────────╯
```

### Via Natural Language

```bash
wtf allow git commands
wtf give yourself permission to run npm commands
```

### Manually

Edit `~/.config/wtf/allowlist.json` and add patterns.

## Pattern Matching

Patterns use glob-style matching:

- `git *` - Allows all git commands
- `npm install*` - Allows npm install and npm install anything
- `ls` - Allows only `ls` with no arguments
- `cat *.txt` - Allows reading text files

## Safe Readonly Commands

These commands auto-execute without being in the allowlist:

**File inspection:**
- `ls`, `cat`, `head`, `tail`, `less`, `more`
- `file`, `stat`, `wc`, `diff`

**Git (readonly):**
- `git status`, `git log`, `git diff`, `git show`, `git branch`

**Project info:**
- `npm list`, `pip list`, `cargo --version`
- `command -v`, `which`, `type`

**System info:**
- `pwd`, `whoami`, `uname`, `date`, `env`

!!! warning "Chaining Blocks Auto-Execution"
    If a command contains `&&`, `||`, `;`, `$()`, or redirection (`>`, `|`),
    it's NOT auto-executed even if it's safe. You'll be prompted.

    Example: `git status && rm file` will ask permission (because of `&&`).

## Denylist

The denylist ALWAYS blocks commands, even if they're in the allowlist.

**Default dangerous patterns:**
- `rm -rf /`
- `dd if=*`
- `mkfs.*`
- `:(){:|:&};:`  (fork bomb)
- `chmod -R 777 /`
- `sudo rm *`

Add more patterns to the denylist in `allowlist.json`:

```json
{
  "patterns": [...],
  "denylist": [
    "rm -rf*",
    "dd*",
    "custom-dangerous-command*"
  ]
}
```

## Removing from Allowlist

### Via Natural Language

```bash
wtf stop auto-running git commands
wtf remove git from my allowlist
```

### Manually

Edit `~/.config/wtf/allowlist.json` and remove the pattern.

## Example Workflow

```bash
# First time
$ wtf "push my changes"
╭──────────────────────────────────╮
│ Permission Required              │
│ Command: git push origin main    │
│ [y] [a] [n]                      │
╰──────────────────────────────────╯
> a

# Now allowed
$ wtf "push again"
✓ Running: git push origin main
[... command output ...]

# If you change your mind
$ wtf stop auto-running git push
✓ Removed "git push*" from allowlist
```

## Security Notes

1. **Be specific** - Use `npm install express` not `npm *`
2. **Review periodically** - Check `allowlist.json` occasionally
3. **Never allowlist destructive commands** - Like `rm`, `dd`, `mkfs`
4. **Understand patterns** - `*` matches anything, be careful

## See Also

- [Permissions](/features/permissions/) - How permission system works
- [Security](/troubleshooting/#security) - Security best practices
