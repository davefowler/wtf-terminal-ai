"""CLI interface for wtf."""

import sys
import argparse
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from wtf import __version__
from wtf.core.config import (
    config_exists,
    create_default_config,
    load_config,
    save_config,
    get_config_dir,
)
from wtf.context.shell import get_shell_history, build_history_context, detect_shell
from wtf.context.git import get_git_status
from wtf.context.env import get_environment_context
from wtf.ai.prompts import build_system_prompt, build_context_prompt
from wtf.ai.client import query_ai
from wtf.ai.response_parser import extract_commands
from wtf.core.permissions import (
    load_allowlist,
    load_denylist,
    should_auto_execute,
    prompt_for_permission,
    add_to_allowlist
)
from wtf.core.executor import execute_command
from wtf.conversation.state import (
    ConversationState,
    ConversationContext,
    ConversationStateMachine,
)

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


def run_setup_wizard() -> Dict[str, Any]:
    """
    Run the interactive setup wizard.

    Returns:
        Configuration dictionary with user's choices.
    """
    console.print()
    console.print(Panel.fit(
        "[bold]Welcome to wtf setup![/bold]\n\n"
        "Let's get you configured. This will only take a moment.",
        border_style="cyan"
    ))
    console.print()

    # 1. Choose AI provider
    console.print("[bold]Step 1:[/bold] Choose your AI provider")
    console.print()
    console.print("  [cyan]1.[/cyan] Anthropic (Claude)")
    console.print("  [cyan]2.[/cyan] OpenAI (GPT)")
    console.print("  [cyan]3.[/cyan] Google (Gemini)")
    console.print()

    provider_choice = Prompt.ask(
        "Select provider",
        choices=["1", "2", "3"],
        default="1"
    )

    provider_map = {
        "1": ("anthropic", "claude-3.5-sonnet"),
        "2": ("openai", "gpt-4o"),
        "3": ("google", "gemini-1.5-pro")
    }

    provider, default_model = provider_map[provider_choice]

    # 2. Ask for API key
    console.print()
    console.print(f"[bold]Step 2:[/bold] Enter your {provider.capitalize()} API key")
    console.print()

    # Show where to get the key
    key_urls = {
        "anthropic": "https://console.anthropic.com/settings/keys",
        "openai": "https://platform.openai.com/api-keys",
        "google": "https://makersuite.google.com/app/apikey"
    }

    console.print(f"  [dim]Get your API key at: {key_urls[provider]}[/dim]")
    console.print()

    use_env = Confirm.ask(
        "Do you want to use an environment variable for the API key? (recommended)",
        default=True
    )

    api_key = None
    key_source = "env"

    if use_env:
        env_var_map = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY"
        }
        env_var = env_var_map[provider]
        console.print()
        console.print(f"[green]✓[/green] Set the [cyan]{env_var}[/cyan] environment variable with your API key")
        console.print(f"  [dim]Example: export {env_var}='your-api-key-here'[/dim]")
    else:
        console.print()
        api_key = Prompt.ask(
            "Enter your API key",
            password=True
        )
        key_source = "config"
        console.print("[yellow]⚠[/yellow]  API key will be stored in [cyan]~/.config/wtf/config.json[/cyan]")

    # 3. Choose model
    console.print()
    console.print(f"[bold]Step 3:[/bold] Choose your default model")
    console.print()

    # Model IDs for llm library
    models_by_provider = {
        "anthropic": [
            "claude-3.5-sonnet",
            "claude-3-opus",
            "claude-3-haiku"
        ],
        "openai": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo"
        ],
        "google": [
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
    }

    models = models_by_provider[provider]
    for i, model in enumerate(models, 1):
        is_default = model == default_model
        marker = " [cyan](recommended)[/cyan]" if is_default else ""
        console.print(f"  [cyan]{i}.[/cyan] {model}{marker}")

    console.print()
    model_choice = Prompt.ask(
        "Select model",
        choices=[str(i) for i in range(1, len(models) + 1)],
        default="1"
    )

    selected_model = models[int(model_choice) - 1]

    # Create config
    config = {
        "version": "0.1.0",
        "api": {
            "provider": provider,
            "key_source": key_source,
            "key": api_key,
            "model": selected_model
        },
        "behavior": {
            "auto_execute_allowlist": True,
            "auto_allow_readonly": True,
            "context_history_size": 5,
            "verbose": False,
            "default_permission": "ask"
        },
        "shell": {
            "type": "zsh",  # Will be detected later
            "history_file": "~/.zsh_history"
        }
    }

    # Save config
    console.print()
    create_default_config()
    save_config(config)

    console.print()
    console.print(Panel.fit(
        "[bold green]✓ Setup complete![/bold green]\n\n"
        f"Configuration saved to [cyan]{get_config_dir()}[/cyan]\n\n"
        "You're ready to use wtf!",
        border_style="green"
    ))
    console.print()

    return config


def handle_query(query: str, config: Dict[str, Any]) -> None:
    """
    Handle a user query using the conversation state machine.

    Args:
        query: User's query string
        config: Configuration dictionary
    """
    # Gather context with visual feedback
    with console.status("🔍 Gathering context...", spinner="dots"):
        # Gather shell history
        commands, failure_reason = get_shell_history(
            count=config.get('behavior', {}).get('context_history_size', 5)
        )
        shell_type = detect_shell()

        # Build history context (handles failures gracefully)
        if not commands:
            history_context = build_history_context(commands, failure_reason, shell_type)
            # For now, just use empty list - in full implementation we'd include the error context
            commands = []

        # Gather git status
        git_status = get_git_status()

        # Gather environment context
        env_context = get_environment_context()

        # TODO: Load memories
        memories = {}

    # Load permission lists
    allowlist = load_allowlist()
    denylist = load_denylist()

    # Create conversation context
    context = ConversationContext(
        user_query=query,
        cwd=".",  # Current working directory
        shell_history=commands,
        git_status=git_status,
        env_context=env_context,
        config=config,
        allowlist=allowlist,
        denylist=denylist,
    )

    # Create and run state machine
    state_machine = ConversationStateMachine(context)

    try:
        # Execute state machine with CLI integration
        _run_state_machine_with_cli(state_machine, config)
    except Exception as e:
        console.print()
        console.print(f"[red]Error:[/red] {e}")
        console.print()
        if "API" in str(e) or "key" in str(e).lower():
            console.print("[yellow]Tip:[/yellow] Make sure your API key is set correctly.")
            console.print("  Run [cyan]wtf --setup[/cyan] to reconfigure.")


def _run_state_machine_with_cli(
    state_machine: ConversationStateMachine,
    config: Dict[str, Any]
) -> None:
    """
    Run the state machine with CLI integration for user interaction.

    Args:
        state_machine: The conversation state machine to run
        config: Configuration dictionary
    """
    context = state_machine.context

    while not state_machine.is_complete():
        current_state = state_machine.state

        if current_state == ConversationState.INITIALIZING:
            # Context already gathered, just transition
            state_machine._execute_current_state()

        elif current_state == ConversationState.QUERYING_AI:
            # Build prompt and query AI
            system_prompt = build_system_prompt()
            context_prompt = build_context_prompt(
                context.shell_history,
                context.git_status,
                context.env_context,
                {}  # memories - TODO: implement
            )

            # Include previous command outputs if this is a follow-up query
            output_context = ""
            if context.command_outputs:
                output_context = "\n\nPREVIOUS COMMAND OUTPUTS:\n"
                for i, output in enumerate(context.command_outputs):
                    output_context += f"\nCommand {i+1} output:\n{output}\n"

            full_prompt = f"""{system_prompt}

CONTEXT:
{context_prompt}{output_context}

USER QUERY:
{context.user_query}

Please help the user with their query. If you need to run commands, propose them clearly."""

            # Query AI with status indicator
            console.print()
            with console.status("🤖 Thinking...", spinner="dots"):
                try:
                    response = query_ai(full_prompt, config, stream=False)
                    context.ai_response = response
                except Exception as e:
                    state_machine.error = e
                    state_machine.state = ConversationState.ERROR
                    raise

            console.print()

            # Transition to next state
            state_machine._execute_current_state()

        elif current_state == ConversationState.STREAMING_RESPONSE:
            # Parse commands from response
            commands_to_run = extract_commands(context.ai_response)
            context.commands_to_run = commands_to_run

            # Show AI response
            console.print(context.ai_response)
            console.print()

            # Transition to next state
            state_machine._execute_current_state()

        elif current_state == ConversationState.AWAITING_PERMISSION:
            # Get current command to execute
            cmd_dict = context.commands_to_run[context.current_command_index]
            cmd = cmd_dict['command']
            explanation = cmd_dict.get('explanation', '')
            allowlist_pattern = cmd_dict.get('allowlist_pattern', cmd.split()[0] if cmd else '')

            # Check if command should auto-execute, ask, or deny
            decision = should_auto_execute(cmd, context.allowlist, context.denylist, config)

            if decision == "deny":
                console.print(f"[red]✗[/red] Command denied (in denylist): [cyan]{cmd}[/cyan]")
                console.print()
                # Skip this command
                context.current_command_index += 1
                # Check if more commands
                if context.current_command_index < len(context.commands_to_run):
                    # Stay in AWAITING_PERMISSION for next command
                    continue
                else:
                    # No more commands
                    state_machine.state = ConversationState.RESPONDING
                    continue

            elif decision == "ask":
                # Prompt for permission
                permission = prompt_for_permission(cmd, explanation, allowlist_pattern)

                if permission == "no":
                    console.print("[yellow]Skipped[/yellow]")
                    console.print()
                    # Skip this command
                    context.current_command_index += 1
                    # Check if more commands
                    if context.current_command_index < len(context.commands_to_run):
                        # Stay in AWAITING_PERMISSION for next command
                        continue
                    else:
                        # No more commands
                        state_machine.state = ConversationState.RESPONDING
                        continue

                elif permission == "yes_always":
                    # Add to allowlist
                    add_to_allowlist(allowlist_pattern)
                    console.print()

            # Transition to executing (either auto or approved)
            state_machine._execute_current_state()

        elif current_state == ConversationState.EXECUTING_COMMAND:
            # Execute the current command
            cmd_dict = context.commands_to_run[context.current_command_index]
            cmd = cmd_dict['command']

            # Check decision again for display purposes
            decision = should_auto_execute(cmd, context.allowlist, context.denylist, config)

            if decision == "auto":
                console.print(f"[dim]Running:[/dim] [cyan]{cmd}[/cyan]")
                output, exit_code = execute_command(cmd, show_spinner=False)
            else:
                # User approved it
                output, exit_code = execute_command(cmd)

            # Store output
            context.command_outputs.append(output)

            console.print()
            if output.strip():
                console.print(output)

            if exit_code != 0:
                console.print(f"[yellow]Command exited with code {exit_code}[/yellow]")

            console.print()

            # Transition to next state (state machine handles incrementing index)
            state_machine._execute_current_state()

        elif current_state == ConversationState.RESPONDING:
            # Final response already shown, just transition to complete
            state_machine._execute_current_state()

        elif current_state == ConversationState.ERROR:
            # Error already handled in outer try/catch
            break

        else:
            # Unknown state, just transition
            state_machine._execute_current_state()


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
        run_setup_wizard()
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

    # Check if setup is needed (first run)
    if not config_exists():
        console.print()
        console.print("[yellow]⚠[/yellow]  No configuration found. Running setup wizard...")
        console.print()
        run_setup_wizard()

    # Load config
    try:
        config = load_config()
    except Exception as e:
        console.print(f"[red]Error loading config:[/red] {e}")
        console.print("Run [cyan]wtf --setup[/cyan] to reconfigure.")
        sys.exit(1)

    # Handle query
    if args.query:
        query = ' '.join(args.query)
        handle_query(query, config)
    else:
        # No query provided - analyze recent context
        console.print("[yellow]Analyzing recent commands...[/yellow]")
        # For now, show a helpful message
        console.print()
        console.print("No query provided. Try:")
        console.print("  [cyan]wtf \"your question here\"[/cyan]")
        console.print("  [cyan]wtf undo[/cyan]")
        console.print("  [cyan]wtf --help[/cyan]")

    sys.exit(0)


if __name__ == "__main__":
    main()
