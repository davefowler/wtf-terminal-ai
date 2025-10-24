# Comparison to Other Tools

Because you're probably wondering if this is just another ChatGPT wrapper.

## vs. GitHub Copilot CLI

**Copilot CLI:** Suggests commands. You copy-paste.

**wtf:** Suggests commands. Executes them. Learns your preferences. Remembers context.

Copilot is a suggestion engine. wtf is an execution engine.

## vs. Aider

**Aider:** Edits code files. Great for refactoring.

**wtf:** Handles terminal commands. Great for "how do I even...?"

Different tools, different problems. Use both.

## vs. ChatGPT/Claude in browser

**Browser AI:** General knowledge. Context-free.

**wtf:** Terminal-specific. Has your history, git status, project type. Contextual.

Browser AI: "Here's how authentication generally works."
wtf: "You're in a Node project with JWT tokens in auth.js line 23. Want me to add refresh token logic?"

## vs. tAI (Terminal AI)

**tAI:** Inspired this project. Simpler, more experimental.

**wtf:** Production-ready. Permissions system. Memory. Hooks.

tAI proved the concept. wtf made it usable.

Credit where it's due: https://github.com/AbanteAI/tAI

## vs. Shell aliases

**Aliases:** Static shortcuts. `alias gs='git status'`

**wtf:** Dynamic reasoning. Understands intent.

Aliases: You remember the shortcut.
wtf: You say what you want.

Example:
- Alias: `deploy-prod`
- wtf: "deploy to production but check if tests passed first"

Different complexity levels.

## vs. Shell completion

**Completion:** Completes commands you already know.

**wtf:** Figures out commands you don't know.

Completion: "Tab to finish this git comm..."
wtf: "I have no idea how to do this, figure it out."

## The Real Question

**"Should I use this instead of X?"**

Probably use it *with* X.

- Use aliases for common commands
- Use Aider for code changes
- Use Copilot for suggestions
- Use wtf when you're confused

They're complementary, not competitive.

## What wtf Actually Solves

1. **Context loss** - AI knows your terminal state
2. **Command syntax** - Don't memorize flags
3. **Error recovery** - Hit error, type wtf
4. **Undo** - Reverse mistakes easily
5. **Memory** - Learns your preferences

If these aren't your problems, you don't need wtf.

If they are, welcome aboard.

## Acknowledgments

Standing on shoulders of:

- **tAI** - Original inspiration
- **Aider** - Showed AI + version control works
- **llm** (Simon Willison) - Model abstraction layer
- **Rich** - Terminal UI that doesn't suck

