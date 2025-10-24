"""CLI interface for wtf."""

import os
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
from wtf.ai.client import query_ai_safe, query_ai_with_tools
from wtf.ai.errors import (
    InvalidAPIKeyError,
    NetworkError,
    RateLimitError,
)
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
from wtf.context.shell import detect_shell

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


def handle_memory_command(query: str) -> bool:
    """
    Check if query is a memory command and handle it directly.

    Args:
        query: User's query string

    Returns:
        True if handled as memory command, False otherwise
    """
    query_lower = query.lower().strip()

    # Show memories
    if "show" in query_lower and "remember" in query_lower:
        memories = load_memories()
        if not memories:
            console.print("[yellow]No memories stored yet.[/yellow]")
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
        return True

    # Clear all memories
    if "clear" in query_lower and "memor" in query_lower:
        memories = load_memories()
        if not memories:
            console.print("[yellow]No memories to clear.[/yellow]")
        else:
            clear_memories()
            console.print("[green]✓[/green] Cleared all memories.")
        console.print()
        return True

    # Remember something
    if "remember" in query_lower and not ("show" in query_lower or "what" in query_lower):
        # Extract the fact to remember
        # Remove "remember" and common words (as whole words, not substrings!)
        import re
        fact = query.lower()
        # Use word boundaries to only remove whole words
        for word in ["wtf", "remember", "that", "i", "we", "you"]:
            fact = re.sub(r'\b' + re.escape(word) + r'\b', '', fact)
        fact = fact.strip()

        if not fact:
            console.print("[yellow]What should I remember?[/yellow]")
            console.print()
            console.print("Example:")
            console.print("  [cyan]wtf remember I use emacs[/cyan]")
            console.print()
            return True

        # Try to extract a key-value pair
        # Simple heuristics: "use X", "prefer X", etc.
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
                    # Generic key from first word before "use"
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

        save_memory(key, value)
        console.print(f"[green]✓[/green] I'll remember: [cyan]{key}[/cyan] = {value}")
        console.print()
        return True

    # Forget specific memory
    if "forget" in query_lower:
        # Try to extract what to forget
        memories = load_memories()
        if not memories:
            console.print("[yellow]No memories to forget.[/yellow]")
            console.print()
            return True

        # Find matching memory keys
        matches = []
        for key in memories.keys():
            if key.lower() in query_lower or any(word in key.lower() for word in query_lower.split()):
                matches.append(key)

        if not matches:
            console.print("[yellow]Couldn't find a matching memory to forget.[/yellow]")
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
            console.print("Be more specific, or delete them manually:")
            console.print("  [cyan]wtf forget about <specific thing>[/cyan]")
            console.print()

        return True

    return False


def handle_query_with_tools(query: str, config: Dict[str, Any]) -> None:
    """
    Handle a user query using the tool-based agent approach.

    Simpler than state machine - agent uses tools in a loop.

    Args:
        query: User's query string
        config: Configuration dictionary
    """
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

    # Build prompts
    system_prompt = build_system_prompt()
    context_prompt = build_context_prompt(commands, git_status, env_context, memories)
    full_prompt = f"{context_prompt}\n\nUSER QUERY:\n{query}"

    try:
        # Query AI with tools
        console.print()
        with console.status("🤖 Thinking...", spinner="dots"):
            result = query_ai_with_tools(
                prompt=full_prompt,
                config=config,
                system_prompt=system_prompt,
                max_iterations=10
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


def handle_query(query: str, config: Dict[str, Any]) -> None:
    """
    Handle a user query using the conversation state machine.

    Args:
        query: User's query string
        config: Configuration dictionary
    """
    # Check if this is a direct memory command
    if handle_memory_command(query):
        return

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

        # Load memories
        memories = load_memories()

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
        _run_state_machine_with_cli(state_machine, config, memories)

        # Log conversation to history after successful completion
        if state_machine.state == ConversationState.COMPLETE:
            append_to_history({
                "query": query,
                "response": context.ai_response,
                "commands": [cmd.get("command", "") for cmd in context.commands_to_run],
                "exit_code": 0  # TODO: track actual exit codes
            })

    except Exception as e:
        console.print()
        console.print(f"[red]Error:[/red] {e}")
        console.print()
        if "API" in str(e) or "key" in str(e).lower():
            console.print("[yellow]Tip:[/yellow] Make sure your API key is set correctly.")
            console.print("  Run [cyan]wtf --setup[/cyan] to reconfigure.")

        # Log error conversation
        append_to_history({
            "query": query,
            "response": str(e),
            "commands": [],
            "exit_code": 1
        })


def _run_state_machine_with_cli(
    state_machine: ConversationStateMachine,
    config: Dict[str, Any],
    memories: Dict[str, Any]
) -> None:
    """
    Run the state machine with CLI integration for user interaction.

    Args:
        state_machine: The conversation state machine to run
        config: Configuration dictionary
        memories: User memories/preferences
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
                memories
            )

            # Include previous command outputs if this is a follow-up query
            output_context = ""
            if context.command_outputs:
                output_context = "\n\nCOMMAND OUTPUTS YOU JUST RAN:\n"
                for i, output in enumerate(context.command_outputs):
                    cmd = context.commands_to_run[i]['command'] if i < len(context.commands_to_run) else "unknown"
                    output_context += f"\n$ {cmd}\n{output}\n"

            # Different prompt for iterations vs initial query
            if context.iteration_count > 0:
                full_prompt = f"""{system_prompt}

CONTEXT:
{context_prompt}{output_context}

ORIGINAL USER QUERY:
{context.user_query}

The commands above have been executed. Please analyze their output and provide your response or run additional commands if needed."""
            else:
                full_prompt = f"""{system_prompt}

CONTEXT:
{context_prompt}{output_context}

USER QUERY:
{context.user_query}

Please help the user with their query. If you need to run commands, propose them clearly."""

            # Query AI with status indicator and retry logic
            console.print()
            with console.status("🤖 Thinking...", spinner="dots"):
                try:
                    response = query_ai_safe(full_prompt, config, stream=False, max_retries=3)
                    context.ai_response = response
                except InvalidAPIKeyError as e:
                    state_machine.error = e
                    state_machine.state = ConversationState.ERROR
                    console.print()
                    console.print(f"[red]✗ API Key Error:[/red] {str(e)}")
                    console.print()
                    console.print("To fix this:")
                    if e.provider:
                        key_urls = {
                            "anthropic": "https://console.anthropic.com/settings/keys",
                            "openai": "https://platform.openai.com/api-keys",
                            "google": "https://makersuite.google.com/app/apikey"
                        }
                        url = key_urls.get(e.provider, "")
                        if url:
                            console.print(f"  1. Get a valid API key from: [cyan]{url}[/cyan]")
                    console.print("  2. Run [cyan]wtf --setup[/cyan] to configure")
                    console.print()
                    raise
                except RateLimitError as e:
                    state_machine.error = e
                    state_machine.state = ConversationState.ERROR
                    console.print()
                    console.print(f"[yellow]⚠ Rate Limit:[/yellow] {str(e)}")
                    console.print()
                    if e.retry_after:
                        console.print(f"Please wait {e.retry_after} seconds before trying again.")
                    else:
                        console.print("Please wait a moment before trying again.")
                    console.print()
                    raise
                except NetworkError as e:
                    state_machine.error = e
                    state_machine.state = ConversationState.ERROR
                    console.print()
                    console.print(f"[red]✗ Network Error:[/red] {str(e)}")
                    console.print()
                    console.print("Possible fixes:")
                    console.print("  - Check your internet connection")
                    console.print("  - Try again in a moment")
                    console.print("  - Check if the AI service is experiencing issues")
                    console.print()
                    raise
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

            # Store output for AI to analyze
            context.command_outputs.append(output)

            console.print()
            if output.strip():
                console.print(output)

            if exit_code != 0:
                console.print(f"[yellow]Command exited with code {exit_code}[/yellow]")

            console.print()

            # Check if this is the last command in the current batch
            is_last_command = (context.current_command_index + 1) >= len(context.commands_to_run)

            # If this is the last command and we have command outputs, set flag to requery
            # so the AI can see the results and decide what to do next
            if is_last_command and context.command_outputs and context.iteration_count < context.max_iterations:
                context.needs_requery = True

            # Transition to next state (state machine handles incrementing index)
            state_machine._execute_current_state()

        elif current_state == ConversationState.PROCESSING_OUTPUT:
            # AI will analyze command outputs and generate next response
            # Show status to user
            console.print("[dim]Analyzing command output...[/dim]")
            console.print()

            # Transition to QUERYING_AI (state machine handles this)
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
        shell = detect_shell()
        console.print()
        console.print(f"[cyan]Setting up error hook for {shell}...[/cyan]")
        success, message = setup_error_hook(shell)
        if success:
            console.print(f"[green]✓[/green] {message}")
            console.print()
            console.print("[yellow]Restart your shell or run:[/yellow]")
            from wtf.setup.hooks import get_shell_config_file
            config_file = get_shell_config_file(shell)
            console.print(f"  [cyan]source {config_file}[/cyan]")
        else:
            console.print(f"[red]✗[/red] {message}")
        console.print()
        sys.exit(0)

    if args.setup_not_found_hook:
        shell = detect_shell()
        console.print()
        console.print(f"[cyan]Setting up command-not-found hook for {shell}...[/cyan]")
        success, message = setup_not_found_hook(shell)
        if success:
            console.print(f"[green]✓[/green] {message}")
            console.print()
            console.print("[yellow]Restart your shell or run:[/yellow]")
            from wtf.setup.hooks import get_shell_config_file
            config_file = get_shell_config_file(shell)
            console.print(f"  [cyan]source {config_file}[/cyan]")
        else:
            console.print(f"[red]✗[/red] {message}")
        console.print()
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

    sys.exit(0)


if __name__ == "__main__":
    main()
