# wtf - Because working in the terminal often gets you asking wtf

A command-line AI assistant that actually understands your terminal context.

## What is this?

`wtf` is there for you when you mess up. Hit an error? Just type `wtf`. Made a mistake? Say `wtf undo`. Need to install something? `wtf install [thing]`. Forgot a command? Ask `wtf can you back me out of this failed merge attempt?`

No flags to remember. No manual pages written in ancient Sumerian. Just describe what you want in plain English (or whatever language you prefer, we're not picky).

## Why does this exist?

Because developers spend half their time Googling error messages and the other half copy-pasting commands from Stack Overflow without reading them.

We figured: what if your terminal just... helped you?

Novel concept, we know.

## Quick Example

```bash
$ git rebase -i HEAD~5
# Oh no, you messed up the rebase
$ wtf

I see you're in the middle of a rebase. Let me guess - you picked
the wrong commit? Happens to the best of us. Actually, it happens
to everyone. Rebasing is just UI/UX for masochists.

Here's how to get out:

$ git rebase --abort
```

## Key Features

- **Context Aware**: Knows your shell history, git status, and project type
- **Permission System**: Won't run dangerous commands without asking
- **Undo Feature**: Analyzes history and suggests safe reversals
- **Memories**: Learns your preferences ("I use npm, not yarn")
- **Multi-Provider AI**: Works with Anthropic, OpenAI, or Google
- **Personality**: Dry, sardonic wit inspired by Gilfoyle and Marvin

## Installation

Three ways to install, because choice is the illusion of control:

=== "curl (Recommended)"

    ```bash
    curl -sSL https://raw.githubusercontent.com/davefowler/wtf-terminal-ai/main/install.sh | bash
    ```

=== "pip"

    ```bash
    pip install wtf-ai
    ```

=== "From Source"

    ```bash
    git clone https://github.com/davefowler/wtf-terminal-ai.git
    cd wtf-terminal-ai
    pip install -e .
    ```

## First Use

Just run `wtf` with any query. Setup happens automatically:

```bash
wtf "what's in my git status?"
```

The setup wizard will ask you to:

1. Choose your AI provider (Anthropic, OpenAI, or Google)
2. Enter your API key
3. Select your default model

That's it. You're ready to make mistakes and let AI fix them.

## What's Next?

- [Getting Started](getting-started.md) - Detailed installation and setup
- [Quick Tour](quick-tour.md) - See what wtf can do
- [FAQ](faq.md) - Questions we've asked ourselves

## Philosophy

CLI tools have 47 flags and you need to consult the manual every time. And then the manual is written like a legal document from 1987.

We hate that too.

`wtf` has a different philosophy: you shouldn't need to remember anything. Just describe what you want. The AI figures out the rest.

It's not complicated. Which is the point.

## Requirements

- Python 3.10 or higher
- An API key from Anthropic, OpenAI, or Google
- A terminal (we assume you have this already)
- Problems (we assume you have these too)

## License

MIT License - Use it, abuse it, just don't blame us when Skynet takes over.

## Contributing

Issues and PRs welcome. Complain about our jokes. We'll probably read it.

[GitHub Repository](https://github.com/davefowler/wtf-terminal-ai)
