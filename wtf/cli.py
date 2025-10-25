"""CLI interface for wtf."""

import os
import sys
import re
import argparse
import llm
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from wtf import __version__
from wtf.core.config import (
    config_exists,
    create_default_config,
    load_config,
    save_config,
    get_config_dir,
)
from wtf.context.shell import get_shell_history, detect_shell
from wtf.context.git import get_git_status
from wtf.context.env import get_environment_context, build_tool_env_context
from wtf.ai.prompts import build_system_prompt, build_context_prompt
from wtf.ai.client import query_ai_with_tools
from wtf.ai.errors import InvalidAPIKeyError, NetworkError, RateLimitError
from wtf.conversation.memory import (
    load_memories,
    save_memory,
    delete_memory,
    clear_memories,
    search_memories,
)
from wtf.conversation.history import append_to_history
from wtf.setup.hooks import (
    setup_error_hook,
    setup_not_found_hook,
    remove_hooks,
    show_hook_info,
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

Documentation: https://github.com/davefowler/wtf-terminal-ai
Issues: https://github.com/davefowler/wtf-terminal-ai/issues

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

    # 1. List available models from llm
    console.print("[bold]Step 1:[/bold] Choose a model")
    console.print()
    console.print("[dim]Discovering available models...[/dim]")
    console.print()

    # Get all models from llm library
    available_models = list(llm.get_models())

    if not available_models:
        console.print("[red]No models found![/red]")
        console.print("Install model plugins: [cyan]llm install llm-claude-3[/cyan]")
        sys.exit(1)

    # Group by provider (parse from model class name or model_id)
    grouped = {}
    for model in available_models:
        # Get provider from model class name (e.g., "OpenAIChat" -> "OpenAI")
        provider_name = model.__class__.__name__.replace("Chat", "").replace("Model", "")
        if provider_name not in grouped:
            grouped[provider_name] = []
        grouped[provider_name].append(model.model_id)

    # Show popular models first
    popular = [
        ("claude-3.5-sonnet", "Anthropic Claude 3.5 Sonnet (recommended)"),
        ("gpt-4o", "OpenAI GPT-4o"),
        ("gpt-4o-mini", "OpenAI GPT-4o Mini (fast & cheap)"),
        ("claude-3-opus", "Anthropic Claude 3 Opus"),
        ("gemini-1.5-pro", "Google Gemini 1.5 Pro"),
    ]

    # Show popular models that are available
    model_choices = []
    for model_id, description in popular:
        if any(model_id in models for models in grouped.values()):
            model_choices.append((model_id, description))

    # Show them
    for i, (model_id, description) in enumerate(model_choices, 1):
        console.print(f"  [cyan]{i}.[/cyan] {description}")

    # Add option to see all
    console.print(f"  [cyan]{len(model_choices) + 1}.[/cyan] See all available models")
    console.print()

    choice = Prompt.ask(
        "Select model",
        choices=[str(i) for i in range(1, len(model_choices) + 2)],
        default="1"
    )

    choice_idx = int(choice) - 1

    if choice_idx == len(model_choices):
        # Show all models grouped by provider
        console.print()
        console.print("[bold]All Available Models:[/bold]")
        console.print()

        all_models = []
        for provider, models in sorted(grouped.items()):
            console.print(f"[bold]{provider}:[/bold]")
            for model_id in sorted(models)[:5]:  # Show first 5 per provider
                all_models.append(model_id)
                console.print(f"  [cyan]{len(all_models)}.[/cyan] {model_id}")
            if len(models) > 5:
                console.print(f"  [dim]...and {len(models) - 5} more[/dim]")
            console.print()

        console.print()
        choice = Prompt.ask(
            "Select model number",
            choices=[str(i) for i in range(1, len(all_models) + 1)],
            default="1"
        )
        selected_model = all_models[int(choice) - 1]
    else:
        selected_model = model_choices[choice_idx][0]

    console.print()
    console.print(f"[green]✓[/green] Selected: [cyan]{selected_model}[/cyan]")

    # 2. Configure API key
    console.print()
    console.print(f"[bold]Step 2:[/bold] Configure API access")
    console.print()
    console.print("[dim]The llm library handles API keys. You can:[/dim]")
    console.print("  [dim]1. Set environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)[/dim]")
    console.print("  [dim]2. Use: [cyan]llm keys set <provider>[/cyan][/dim]")
    console.print("  [dim]3. Let wtf store it (not recommended)[/dim]")
    console.print()

    use_llm_keys = Confirm.ask(
        "Use llm's key management? (recommended)",
        default=True
    )

    api_key = None
    key_source = "llm"  # New: delegate to llm library

    if not use_llm_keys:
        console.print()
        api_key = Prompt.ask(
            "Enter your API key",
            password=True
        )
        key_source = "config"
        console.print("[yellow]⚠[/yellow]  API key will be stored in [cyan]~/.config/wtf/config.json[/cyan]")

    # Create config
    config = {
        "version": "0.1.0",
        "api": {
            "model": selected_model,
            "key_source": key_source,
            "key": api_key
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


def _show_memories() -> None:
    """Display all stored memories."""
    memories = load_memories()
    if not memories:
        console.print("[yellow]No memories stored yet[/yellow]")
        console.print()
        console.print("You can teach me your preferences:")
        console.print("  [cyan]wtf remember I use emacs[/cyan]")
        console.print("  [cyan]wtf remember I prefer npm over yarn[/cyan]")
    else:
        console.print("[bold]Memories:[/bold]")
        console.print()
        for key, memory_data in memories.items():
            value = memory_data.get("value")
            timestamp = memory_data.get("timestamp", "")
            if timestamp:
                timestamp = timestamp.split("T")[0]  # Just date
            console.print(f"  [cyan]{key}:[/cyan] {value} [dim]({timestamp})[/dim]")
        console.print()


def _clear_memories() -> None:
    """Clear all stored memories."""
    memories = load_memories()
    if not memories:
        console.print("[yellow]No memories to clear[/yellow]")
    else:
        clear_memories()
        console.print("[green]✓[/green] Cleared all memories.")
    console.print()


def _remember_fact(query: str) -> None:
    """Parse and remember a fact from the query."""
    # Remove "remember" and common filler words
    fact = query.lower()
    for word in ["wtf", "remember", "that", "i", "we", "you"]:
        fact = re.sub(r'\b' + re.escape(word) + r'\b', '', fact)
    fact = fact.strip()

    if not fact:
        console.print("[yellow]What should I remember[/yellow]")
        console.print()
        console.print("Example:")
        console.print("  [cyan]wtf remember I use emacs[/cyan]")
        console.print()
        return

    # Try to extract key-value pair from common patterns
    key, value = _parse_memory_fact(fact)

    save_memory(key, value)
    console.print(f"[green]✓[/green] I'll remember: [cyan]{key}[/cyan] = {value}")
    console.print()


def _parse_memory_fact(fact: str) -> tuple[str, str]:
    """Parse a fact string into key and value.

    Args:
        fact: The fact to parse (e.g., "use emacs" or "prefer npm over yarn")

    Returns:
        Tuple of (key, value)
    """
    key = None
    value = None

    if "use" in fact:
        parts = fact.split("use", 1)
        if len(parts) == 2:
            value = parts[1].strip()
            # Guess key from context
            if "editor" in fact or "emacs" in value or "vim" in value:
                key = "editor"
            elif "package" in fact or "npm" in value or "yarn" in value:
                key = "package_manager"
            elif "shell" in fact or "zsh" in value or "bash" in value:
                key = "shell"
            elif "python" in fact:
                key = "python_version"
            else:
                key = parts[0].strip().replace(" ", "_") or "preference"

    elif "prefer" in fact:
        parts = fact.split("prefer", 1)
        if len(parts) == 2:
            value = parts[1].strip()
            # Remove "over X" if present
            if " over " in value:
                value = value.split(" over ")[0].strip()
            key = parts[0].strip().replace(" ", "_") or "preference"

    # If we couldn't parse it, save the whole fact
    if not key or not value:
        key = "general"
        value = fact

    return key, value


def _forget_memory(query: str) -> None:
    """Find and forget a specific memory."""
    memories = load_memories()
    if not memories:
        console.print("[yellow]No memories to forget[/yellow]")
        console.print()
        return

    query_lower = query.lower()

    # Find matching memory keys
    matches = []
    for key in memories.keys():
        if key.lower() in query_lower or any(word in key.lower() for word in query_lower.split()):
            matches.append(key)

    if not matches:
        console.print("[yellow]Couldn't find a matching memory to forget[/yellow]")
        console.print()
        console.print("Current memories:")
        for key in memories.keys():
            console.print(f"  - {key}")
        console.print()
    elif len(matches) == 1:
        delete_memory(matches[0])
        console.print(f"[green]✓[/green] Forgot about: [cyan]{matches[0]}[/cyan]")
        console.print()
    else:
        console.print(f"[yellow]Multiple matches found:[/yellow]")
        for key in matches:
            console.print(f"  - {key}")
        console.print()
        console.print("Be more specific")
        console.print()


def handle_setup_command(query: str) -> bool:
    """Check if query is a setup/configuration command and handle it.

    Args:
        query: User's query string

    Returns:
        True if handled as setup command, False otherwise
    """
    query_lower = query.lower().strip()

    # Patterns that indicate wanting to run setup/reconfigure
    has_model_keywords = ("provider" in query_lower or "ai" in query_lower or "model" in query_lower)
    has_known_models = any(name in query_lower for name in ["claude", "gpt", "gemini", "openai", "anthropic", "google"])

    setup_patterns = [
        "change" in query_lower and (has_model_keywords or has_known_models),
        "switch" in query_lower and (has_model_keywords or has_known_models or "to" in query_lower),
        "use" in query_lower and ("different" in query_lower or "another" in query_lower) and (has_model_keywords or has_known_models),
        "reconfigure" in query_lower,
        "setup" in query_lower and not "--setup" in query,  # Natural language, not flag
        "reset" in query_lower and ("config" in query_lower or "settings" in query_lower or "everything" in query_lower),
    ]

    if any(setup_patterns):
        console.print()
        console.print("[cyan]I'll run the setup wizard to change your configuration.[/cyan]")
        console.print()
        run_setup_wizard()
        return True

    return False


def handle_memory_command(query: str) -> bool:
    """Check if query is a memory command and handle it.

    Args:
        query: User's query string

    Returns:
        True if handled as memory command, False otherwise
    """
    query_lower = query.lower().strip()

    if "show" in query_lower and "remember" in query_lower:
        _show_memories()
        return True

    if "clear" in query_lower and "memor" in query_lower:
        _clear_memories()
        return True

    if "remember" in query_lower and not ("show" in query_lower or "what" in query_lower):
        _remember_fact(query)
        return True

    if "forget" in query_lower:
        _forget_memory(query)
        return True

    return False


def _setup_hook(hook_name: str, setup_func) -> None:
    """Helper to set up a shell hook with consistent messaging.

    Args:
        hook_name: Human-readable hook name (e.g., "error", "command-not-found")
        setup_func: The setup function to call
    """
    from wtf.setup.hooks import get_shell_config_file

    shell = detect_shell()
    console.print()
    console.print(f"[cyan]Setting up {hook_name} hook for {shell}...[/cyan]")
    success, message = setup_func(shell)

    if success:
        console.print(f"[green]✓[/green] {message}")
        console.print()
        console.print("[yellow]Restart your shell or run:[/yellow]")
        config_file = get_shell_config_file(shell)
        console.print(f"  [cyan]source {config_file}[/cyan]")
    else:
        console.print(f"[red]✗[/red] {message}")
    console.print()


def handle_query_with_tools(query: str, config: Dict[str, Any]) -> None:
    """
    Handle a user query using the tool-based agent approach.

    Simpler than state machine - agent uses tools in a loop.

    Args:
        query: User's query string
        config: Configuration dictionary
    """
    # Check if this is a setup/configuration command
    if handle_setup_command(query):
        return

    # Check if this is a direct memory command
    if handle_memory_command(query):
        return

    # Gather context
    with console.status("🔍 Gathering context...", spinner="dots"):
        commands, _ = get_shell_history(
            count=config.get('behavior', {}).get('context_history_size', 5)
        )
        git_status = get_git_status()
        env_context = get_environment_context()
        memories = load_memories()
        tool_env_context = build_tool_env_context(env_context, git_status)
        shell_type = detect_shell()

    # Build prompts
    system_prompt = build_system_prompt()
    context_prompt = build_context_prompt(commands, git_status, env_context, memories, shell_type)
    full_prompt = f"{context_prompt}\n\nUSER QUERY:\n{query}"

    try:
        # Query AI with tools
        console.print()
        with console.status("🤖 Thinking...", spinner="dots"):
            result = query_ai_with_tools(
                prompt=full_prompt,
                config=config,
                system_prompt=system_prompt,
                max_iterations=10,
                env_context=tool_env_context
            )

        # Process tool calls and print outputs
        console.print()

        # Print run_command outputs (user-facing)
        for tool_call in result["tool_calls"]:
            tool_name = tool_call["name"]
            tool_result = tool_call["result"]

            # Only print run_command outputs (internal tools are hidden)
            if tool_name == "run_command" and tool_result.get("should_print", False):
                cmd = tool_call["arguments"].get("command", "")
                output = tool_result.get("output", "")
                exit_code = tool_result.get("exit_code", 0)

                console.print(f"[dim]$[/dim] [cyan]{cmd}[/cyan]")
                if output.strip():
                    # Add "│ " (box-drawing character) prefix, dim the entire output
                    indented_output = '\n'.join(f"[dim]│ {line}[/dim]" for line in output.split('\n'))
                    console.print(indented_output)
                # Only show exit code if it's actually an error AND the output doesn't already explain it
                # (e.g., "nothing to commit" is self-explanatory, no need for "Exit code: 1")
                if exit_code != 0 and exit_code != 1:
                    console.print(f"[yellow]Exit code: {exit_code}[/yellow]")
                console.print()

        # Print final agent response
        response_text = result.get("response", "")
        if response_text:
            console.print(response_text)
        else:
            # Debug: show what we got
            console.print("[dim]No response text. Debug info:[/dim]")
            console.print(f"[dim]Tool calls: {len(result['tool_calls'])}[/dim]")
            console.print(f"[dim]Iterations: {result.get('iterations', 0)}[/dim]")
        console.print()

        # Log to history
        append_to_history({
            "query": query,
            "response": result["response"],
            "commands": [tc["arguments"].get("command", "") for tc in result["tool_calls"] if tc["name"] == "run_command"],
            "exit_code": 0
        })

    except Exception as e:
        console.print()
        console.print(f"[red]Error:[/red] {e}")
        console.print()
        if "API" in str(e) or "key" in str(e).lower():
            console.print("[yellow]Tip:[/yellow] Make sure your API key is set correctly.")
            console.print("  Run [cyan]wtf --setup[/cyan] to reconfigure.")

        append_to_history({
            "query": query,
            "response": str(e),
            "commands": [],
            "exit_code": 1
        })



def _parse_arguments():
    """Parse command line arguments."""
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

    return parser.parse_args()


def _handle_config_flag() -> None:
    """Handle --config flag to show configuration file location."""
    config_dir = get_config_dir()
    config_file = config_dir / "config.json"
    console.print()
    console.print(f"[bold]Configuration:[/bold]")
    console.print()
    console.print(f"  Config directory: [cyan]{config_dir}[/cyan]")
    console.print(f"  Config file: [cyan]{config_file}[/cyan]")
    console.print()
    if config_file.exists():
        console.print("[dim]To edit, open the file in your editor or run:[/dim]")
        console.print(f"  [cyan]$EDITOR {config_file}[/cyan]")
    else:
        console.print("[yellow]No config file found - run 'wtf --setup' to create one[/yellow]")
    console.print()
    sys.exit(0)


def _handle_reset_flag() -> None:
    """Handle --reset flag to delete all configuration."""
    from pathlib import Path
    import shutil

    config_dir = Path(get_config_dir())

    if not config_dir.exists():
        console.print("[yellow]No config found to reset[/yellow]")
        sys.exit(0)

    console.print()
    console.print("[bold red]⚠ Warning:[/bold red] This will delete ALL wtf configuration")
    console.print()
    console.print("This includes:")
    console.print("  • API keys and model settings")
    console.print("  • Memories (learned preferences)")
    console.print("  • Conversation history")
    console.print("  • Allowlist/denylist")
    console.print()

    if not Confirm.ask("[bold]Are you sure?[/bold]", default=False):
        console.print("[yellow]Cancelled[/yellow]")
        sys.exit(0)

    try:
        shutil.rmtree(config_dir)
        console.print()
        console.print(f"[green]✓[/green] Deleted {config_dir}")
        console.print()
        console.print("Run [cyan]wtf --setup[/cyan] to reconfigure.")
        console.print()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
    sys.exit(0)


def _handle_hooks_flags(args) -> None:
    """Handle hook-related flags (--setup-error-hook, --setup-not-found-hook, --remove-hooks)."""
    if args.setup_error_hook:
        _setup_hook("error", setup_error_hook)
        sys.exit(0)

    if args.setup_not_found_hook:
        _setup_hook("command-not-found", setup_not_found_hook)
        sys.exit(0)

    if args.remove_hooks:
        shell = detect_shell()
        console.print()
        console.print(f"[cyan]Removing wtf hooks from {shell}...[/cyan]")
        success, message = remove_hooks(shell)
        if success:
            console.print(f"[green]✓[/green] {message}")
        else:
            console.print(f"[yellow]⚠[/yellow] {message}")
        console.print()
        sys.exit(0)


def _load_or_setup_config():
    """Load configuration, running setup wizard if needed."""
    # Check if setup is needed (first run)
    if not config_exists():
        console.print()
        console.print("[yellow]⚠[/yellow]  No configuration found. Running setup wizard...")
        console.print()
        run_setup_wizard()

    # Load config
    try:
        return load_config()
    except Exception as e:
        console.print(f"[red]Error loading config:[/red] {e}")
        console.print("Run [cyan]wtf --setup[/cyan] to reconfigure.")
        sys.exit(1)


def _handle_query(args, config) -> None:
    """Handle user query or show helpful message."""
    if args.query:
        query = ' '.join(args.query)
        # Set verbose/debug mode via environment variable
        if args.verbose:
            os.environ['WTF_DEBUG'] = '1'
        # Use tool-based approach (simpler than state machine)
        handle_query_with_tools(query, config)
    else:
        # No query provided - analyze recent context
        console.print("[yellow]Analyzing recent commands...[/yellow]")
        # For now, show a helpful message
        console.print()
        console.print("No query provided. Try:")
        console.print("  [cyan]wtf \"your question here\"[/cyan]")
        console.print("  [cyan]wtf undo[/cyan]")
        console.print("  [cyan]wtf --help[/cyan]")


def main() -> None:
    """Main entry point for wtf CLI."""
    args = _parse_arguments()

    # Handle flags
    if args.help:
        print_help()
        sys.exit(0)

    if args.version:
        print_version()
        sys.exit(0)

    if args.config:
        _handle_config_flag()

    if args.reset:
        _handle_reset_flag()

    if args.setup:
        run_setup_wizard()
        sys.exit(0)

    _handle_hooks_flags(args)

    # Load or setup config
    config = _load_or_setup_config()

    # Handle query
    _handle_query(args, config)

    sys.exit(0)


if __name__ == "__main__":
    main()
