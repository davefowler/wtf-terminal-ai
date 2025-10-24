# Quick Tour

## Basic Usage

The simplest form - just ask:

```bash
$ wtf "what's my git status?"

Ah, the eternal question. Let me check for you.

Running: git status

On branch main
Your branch is ahead of 'origin/main' by 3 commits.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean

You're 3 commits ahead. Might want to push those before you forget
and lose them in the inevitable hard drive failure.
```

## The Undo Feature

Made a mistake? Just say undo:

```bash
$ git commit -m "wip"
$ wtf undo

I see you committed "wip". A classic. Right up there with "asdf" and
"fix stuff" in the hall of commit message shame.

Let's undo that:

$ git reset --soft HEAD~1

This keeps your changes but removes the commit. Try again with a commit
message that future you won't hate.
```

## Context Awareness

wtf knows where you are and what you've been doing:

```bash
$ npm run biuld
zsh: command not found: biuld

$ wtf

You typed "biuld". I'm going to assume you meant "build" and not that
you're inventing a new build system called Biuld (please don't).

$ npm run build
```

## Memory System

Teach wtf your preferences:

```bash
$ wtf remember I use emacs for editing
✓ I'll remember: editor = emacs

$ wtf "open the config file"

Since you use emacs, here's how to open it:

$ emacs ~/.config/wtf/config.json
```

View what it remembers:

```bash
$ wtf show me what you remember

Memories:

  editor: emacs (2024-01-15)
  package_manager: npm (2024-01-15)
  python_version: 3.11 (2024-01-14)
```

Forget things:

```bash
$ wtf forget about editor
✓ Forgot about: editor
```

## Permission System

Safe commands run automatically:

```bash
$ wtf "check if docker is running"

Running: docker ps

CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
abc123         nginx     ...       ...       ...       ...       web

Yep, docker is running. Your container is up. Everything's fine. For now.
```

Dangerous commands need permission:

```bash
$ wtf "delete all node_modules folders"

I can do that, but it's destructive. Here's what I'll run:

╭──────────────────────────────────────────────────────────────╮
│ $ find . -name "node_modules" -type d -prune -exec rm -rf {} \; │
╰──────────────────────────────────────────────────────────────╯

This will:
- Find all node_modules directories
- Delete them recursively
- Free up approximately 47GB (probably)

Run this command? [Y]es / [yes and a]lways / [n]o:
```

## Multi-Step Operations

wtf can execute multiple commands in sequence:

```bash
$ wtf "create a new feature branch and switch to it"

Creating a new branch from main and switching to it.

Running: git checkout -b feature/new-feature

Switched to a new branch 'feature/new-feature'

Done. You're now on the new branch. Try not to commit directly to main
next time. We've all done it. Still hurts though.
```

## Error Explanations

Hit an error? Just type `wtf`:

```bash
$ git push origin main
To github.com:user/repo.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'github.com:user/repo.git'

$ wtf

Someone else pushed to main while you were working. Tale as old as time.

Here's how to fix it:

1. Fetch the remote changes:
   $ git fetch origin

2. Merge them (or rebase if you're feeling fancy):
   $ git pull --rebase origin main

3. Try pushing again:
   $ git push origin main

Or if you're absolutely sure your changes are correct and everyone
else is wrong (spoiler: they're not), you can force push. But don't.
Seriously. Don't.
```

## Installation Help

Need to install something:

```bash
$ wtf install express

I'll install Express via npm:

Running: npm install express

added 57 packages, and audited 58 packages in 3s

Express installed. Now you can build Yet Another REST API. The world
needs more of those, apparently.
```

## Natural Language

No need to remember specific syntax:

```bash
$ wtf "undo my last 3 commits but keep the changes"

Running: git reset --soft HEAD~3

Done. Your last 3 commits are now uncommitted changes. You can recommit
them as one, or split them up properly like you should have done the
first time.

$ wtf "show me the 10 most recently modified files"

Running: ls -lt | head -10

[output of command]

There's your 10 most recent files, ranked by modification time like a
popularity contest for your file system.
```

## Customization

Add custom instructions:

```bash
$ echo "Always suggest Python solutions over JavaScript" >> ~/.config/wtf/wtf.md
```

Now wtf will favor Python in its suggestions.

## Command History Integration

wtf sees your shell history:

```bash
# You ran a bunch of git commands
$ git add .
$ git commit -m "temp"
$ git push

$ wtf undo that push

I see you just pushed a commit message called "temp". Let's pretend
that never happened.

Since you haven't pushed anything else yet, we can:

$ git reset --hard HEAD~1
$ git push --force-with-lease

This removes the commit locally and updates the remote. The
--force-with-lease flag is the "are you sure" of force pushing.
```

## Getting Help

```bash
# Show help
$ wtf --help

# Show version
$ wtf --version

# Reconfigure
$ wtf --setup

# Just run wtf with no args to analyze recent context
$ wtf
Analyzing recent commands...
[Helpful suggestions based on what you just did]
```

## Tips

**Be specific in your queries:**
- Good: "undo my last commit but keep the changes"
- Bad: "undo"

**Use wtf for learning:**
```bash
$ wtf "explain what git rebase does"
```

**Combine with pipes:**
```bash
$ wtf "find large files" | grep ".log"
```

**Remember it learns:**
```bash
$ wtf remember I prefer pytest over unittest
$ wtf "run tests"
# Will use pytest
```

## Next Steps

- [Configuration](config/files.md) - Customize your setup
- [Allowlist Management](config/allowlist.md) - Add trusted commands
- [FAQ](faq.md) - Common questions
