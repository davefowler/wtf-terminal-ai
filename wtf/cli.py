"""CLI interface for wtf."""

import sys
import argparse
from typing import Optional
from rich.console import Console

from wtf import __version__

console = Console()

HELP_TEXT = """[bold]wtf[/bold] - Because working in the terminal often gets you asking wtf

[bold]USAGE:[/bold]
  wtf [LITERALLY ANYTHING YOU WANT]

That's right. Put whatever you want there. We'll figure it out.

The whole point of wtf is that you're not good at remembering stuff. Why would
this tool make you remember MORE stuff? That would be stupid, right?

Well, the creators aren't that stupid. We know you. We ARE you. So just type
whatever crosses your mind and we'll do our best to make it happen.

[bold]EXAMPLES OF THINGS THAT WORK:[/bold]
  wtf                              [dim]# No args? We'll look at recent context[/dim]
  wtf undo                         [dim]# Made a mistake? We'll reverse it[/dim]
  wtf install express              [dim]# Need something? We'll install it[/dim]
  wtf "what does this error mean?" [dim]# Confused? We'll explain[/dim]
  wtf how do I exit vim            [dim]# Trapped? We'll free you[/dim]
  wtf remember I use emacs         [dim]# Preferences? We'll learn them[/dim]
  wtf show me what you remember    [dim]# Forgot what we know? We'll remind you[/dim]

All of these work exactly as you'd expect. No flags. No manual pages. No
existential dread about whether it's -v or --verbose or -V or --version.

[bold]THAT SAID...[/bold]

Since you're here reading the help (congratulations on your thoroughness),
here's some context about what wtf can do:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[bold]MEMORIES (Teaching wtf Your Preferences)[/bold]

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

[bold]UNDO (The Universal Rewind Button)[/bold]

Made a mistake? Committed to wrong branch? Deleted the wrong file? Just say:

  wtf undo
  wtf undo that commit
  wtf undo the last 3 commands

wtf looks at your history, figures out what you did, and proposes how to
reverse it. It's not magic. It's AI looking at your shell history and
actually being useful for once.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[bold]HOOKS (Automatic wtf on Errors)[/bold]

Want wtf to automatically trigger when commands fail? Set up hooks:

  wtf --setup-error-hook       [dim]# Auto-trigger on command failures[/dim]
  wtf --setup-not-found-hook   [dim]# Auto-trigger on "command not found"[/dim]

Or just ask naturally:
  wtf set up error hooks for me
  wtf enable automatic error detection

To remove them later:
  wtf --remove-hooks

  Or: wtf remove those hooks you set up

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[bold]ACTUAL FLAGS (For the 1% of Times You Might Need Them)[/bold]

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

[bold]THE PHILOSOPHY[/bold]

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

[bold]MORE INFO[/bold]

Documentation: https://wtf-ai.dev
Issues: https://github.com/username/wtf-terminal-ai/issues

Report bugs. Request features. Complain about our jokes. We'll read it.
Probably.
"""


def print_help() -> None:
    """Print the help message using rich formatting."""
    console.print(HELP_TEXT)


def print_version() -> None:
    """Print the version number."""
    console.print(f"wtf {__version__}")


def main() -> None:
    """Main entry point for wtf CLI."""
    # Custom argument parser that doesn't exit on unknown args
    parser = argparse.ArgumentParser(
        add_help=False,  # We'll handle --help ourselves
        description="wtf - Because working in the terminal often gets you asking wtf"
    )

    # Add known flags
    parser.add_argument('--help', '-h', action='store_true', help='Show help message')
    parser.add_argument('--version', '-v', action='store_true', help='Show version')
    parser.add_argument('--config', action='store_true', help='Open config file')
    parser.add_argument('--model', type=str, help='Override AI model')
    parser.add_argument('--verbose', action='store_true', help='Show diagnostic info')
    parser.add_argument('--reset', action='store_true', help='Reset config to defaults')
    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    parser.add_argument('--setup-error-hook', action='store_true', help='Setup error hook')
    parser.add_argument('--setup-not-found-hook', action='store_true', help='Setup not-found hook')
    parser.add_argument('--remove-hooks', action='store_true', help='Remove shell hooks')

    # Collect the rest as the user query
    parser.add_argument('query', nargs='*', help='Your query for wtf')

    args = parser.parse_args()

    # Handle flags
    if args.help:
        print_help()
        sys.exit(0)

    if args.version:
        print_version()
        sys.exit(0)

    # Handle other flags (not implemented yet)
    if args.config:
        console.print("[yellow]Not implemented yet[/yellow]")
        sys.exit(0)

    if args.reset:
        console.print("[yellow]Not implemented yet[/yellow]")
        sys.exit(0)

    if args.setup:
        console.print("[yellow]Not implemented yet[/yellow]")
        sys.exit(0)

    if args.setup_error_hook:
        console.print("[yellow]Not implemented yet[/yellow]")
        sys.exit(0)

    if args.setup_not_found_hook:
        console.print("[yellow]Not implemented yet[/yellow]")
        sys.exit(0)

    if args.remove_hooks:
        console.print("[yellow]Not implemented yet[/yellow]")
        sys.exit(0)

    # Handle query
    if args.query:
        query = ' '.join(args.query)
        console.print(f"[yellow]Not implemented yet[/yellow]: {query}")
    else:
        # No query provided
        console.print("[yellow]Not implemented yet[/yellow]")

    sys.exit(0)


if __name__ == "__main__":
    main()
