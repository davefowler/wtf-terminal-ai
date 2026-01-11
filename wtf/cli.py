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
from wtf.ai.tools import UserCancelledError
from wtf.conversation.memory import (
    load_memories,
    save_memory,
    delete_memory,
    clear_memories,
    search_memories,
)
from wtf.conversation.history import append_to_history, get_recent_conversations
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
  --upgrade          Upgrade wtf and all AI model plugins
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


def _save_llm_key(key_name: str, api_key: str) -> None:
    """Save an API key to llm's keys.json file.
    
    Args:
        key_name: The key name (e.g., 'anthropic', 'openai', 'gemini')
        api_key: The API key value
    """
    import json
    
    # Get llm's key storage location
    keys_path = llm.user_dir() / "keys.json"
    
    # Load existing keys
    if keys_path.exists():
        with open(keys_path, 'r') as f:
            keys = json.load(f)
    else:
        keys = {}
    
    # Add/update the key
    keys[key_name] = api_key
    
    # Save back
    keys_path.parent.mkdir(parents=True, exist_ok=True)
    with open(keys_path, 'w') as f:
        json.dump(keys, f, indent=2)


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

    # 1. Choose provider first
    console.print("[bold]Step 1:[/bold] Choose your AI provider")
    console.print()
    console.print("[dim]Discovering available models...[/dim]")
    console.print()

    # Get all models from llm library
    available_models = list(llm.get_models())

    if not available_models:
        console.print("[red]No models found![/red]")
        console.print()
        console.print("This is unexpected. Try reinstalling wtf:")
        console.print("  [cyan]pip install --upgrade wtf-ai[/cyan]")
        console.print()
        console.print("Or install the llm library manually:")
        console.print("  [cyan]pip install llm llm-anthropic llm-gemini[/cyan]")
        sys.exit(1)

    # Group by provider (parse from model class name or model_id)
    grouped = {}
    for model in available_models:
        # Get provider from model class name (e.g., "OpenAIChat" -> "OpenAI")
        provider_name = model.__class__.__name__.replace("Chat", "").replace("Model", "")
        if provider_name not in grouped:
            grouped[provider_name] = []
        grouped[provider_name].append(model.model_id)

    # Detect which API keys are available
    detected_keys = {
        "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "google": bool(os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")),
    }

    # Check if local models are available (Ollama)
    all_available_ids = [m for models in grouped.values() for m in models]
    has_local_models = any(
        "llama" in m.lower() or "mistral" in m.lower() or "qwen" in m.lower() 
        or "deepseek" in m.lower() or "codellama" in m.lower() or "phi" in m.lower()
        for m in all_available_ids
    )

    # Define providers with their display info
    providers = [
        ("anthropic", "Anthropic (Claude)", "claude"),
        ("openai", "OpenAI (GPT, o1, o3)", "gpt"),
        ("google", "Google (Gemini)", "gemini"),
        ("local", "Local (Ollama)", None),
    ]

    # Show provider choices
    provider_choices = []
    for provider_key, provider_name, _ in providers:
        status = ""
        if provider_key == "local":
            if has_local_models:
                status = " [green](models detected)[/green]"
                provider_choices.append((provider_key, provider_name))
        elif detected_keys.get(provider_key):
            status = " [green](key detected)[/green]"
            provider_choices.append((provider_key, provider_name))
        else:
            provider_choices.append((provider_key, provider_name))
        
        console.print(f"  [cyan]{len(provider_choices)}.[/cyan] {provider_name}{status}")

    console.print()
    provider_choice = Prompt.ask(
        "Select provider",
        choices=[str(i) for i in range(1, len(provider_choices) + 1)],
        default="1"
    )
    selected_provider = provider_choices[int(provider_choice) - 1][0]

    console.print()
    console.print(f"[green]✓[/green] Selected provider: [cyan]{provider_choices[int(provider_choice) - 1][1]}[/cyan]")

    # 2. Choose model from selected provider
    console.print()
    console.print("[bold]Step 2:[/bold] Choose a model")
    console.print()

    # Model metadata by provider
    # Descriptions and priority are for display only - actual models come from llm.get_models()
    # Priority: higher = shown first (flagship models should have highest priority)
    model_metadata = {
        "anthropic": {
            # Opus is flagship (most capable), Sonnet is balanced, Haiku is fast/cheap
            "descriptions": {
                "opus": "Most capable, best for complex tasks",
                "sonnet": "Balanced performance and speed",
                "haiku": "Fast & cheap",
            },
            "priority": {
                "opus": 100,
                "sonnet": 80, 
                "haiku": 60,
            },
        },
        "openai": {
            "descriptions": {
                "gpt-5": "Latest generation",
                "gpt-4o": "Great all-around",
                "gpt-4o-search": "Built-in web search!",
                "gpt-4.1": "Enhanced GPT-4",
                "o3": "Advanced reasoning",
                "o1": "Reasoning model",
                "mini": "Fast & cheap",
            },
            "priority": {
                "gpt-5": 100,
                "o3": 95,
                "gpt-4o": 90,
                "o1": 85,
                "gpt-4.1": 85,
                "gpt-4": 80,
                "mini": 50,
            },
        },
        "google": {
            "descriptions": {
                "2.5-pro": "Most capable",
                "2.5-flash": "Fast & efficient",
                "2.0": "Previous generation",
                "pro": "Most capable",
                "flash": "Fast & efficient",
            },
            "priority": {
                "2.5": 90,
                "2.0": 80,
                "pro": 85,
                "flash": 70,
            },
        },
        "local": {
            "descriptions": {
                "llama": "Meta's open model",
                "deepseek": "Reasoning model", 
                "mistral": "Fast open model",
                "codellama": "Optimized for code",
                "qwen": "Alibaba's model",
                "phi": "Microsoft's small model",
            },
            "priority": {
                "llama3": 90,
                "deepseek": 85,
                "mistral": 80,
                "codellama": 75,
                "qwen": 70,
                "phi": 60,
            },
        },
    }

    # Version number priority boost (higher versions = better)
    version_priority = {
        "4.5": 95, "4.1": 92, "4": 90,
        "3.7": 85, "3.5": 80, "3": 75,
        "2.5": 85, "2.0": 80, "2": 75,
    }

    def get_model_priority(model_id: str, provider: str) -> int:
        """Get sort priority for a model (higher = better/first)."""
        model_lower = model_id.lower()
        priority = 0
        
        # Check provider-specific priority
        if provider in model_metadata:
            for key, val in model_metadata[provider].get("priority", {}).items():
                if key in model_lower:
                    priority = max(priority, val)
        
        # Check version number boost
        for ver, val in version_priority.items():
            if ver in model_lower:
                priority = max(priority, val)
        
        return priority

    def get_model_description(model_id: str, provider: str) -> str:
        """Get description for a model if known."""
        model_lower = model_id.lower()
        
        # Check provider-specific descriptions
        if provider in model_metadata:
            for key, desc in model_metadata[provider].get("descriptions", {}).items():
                if key in model_lower:
                    return desc
        return ""

    # Map selected_provider to provider class name patterns for filtering
    provider_patterns = {
        "anthropic": ["claude", "anthropic"],
        "openai": ["gpt", "chatgpt", "o1", "o3", "openai"],
        "google": ["gemini", "google"],
        "local": ["ollama", "llama", "mistral", "phi", "qwen", "deepseek", "codellama"],
    }
    patterns = provider_patterns.get(selected_provider, [])

    # Get all models for this provider from llm.get_models()
    provider_models = []
    for provider_name, model_ids in grouped.items():
        provider_lower = provider_name.lower()
        # Check if this group matches our selected provider
        matches_provider = any(p in provider_lower for p in patterns)
        if not matches_provider:
            # Also check if any model ID contains our patterns
            matches_provider = any(
                any(p in m.lower() for p in patterns) 
                for m in model_ids
            )
        if matches_provider:
            provider_models.extend(model_ids)

    # Deduplicate and filter models - remove dated versions that are likely deprecated
    # e.g., remove "claude-3-5-sonnet-20240620" in favor of "claude-sonnet-4-5"
    import re
    
    def get_base_model_name(model_id: str) -> str:
        """Extract base model name without dates or 'latest' suffix."""
        # Remove date suffixes like -20240229, -20241022
        base = re.sub(r'-\d{8}$', '', model_id)
        # Remove 'latest' suffix
        base = re.sub(r'-latest$', '', base)
        return base
    
    def has_date_suffix(model_id: str) -> bool:
        """Check if model ID has a date suffix (likely deprecated)."""
        return bool(re.search(r'-\d{8}$', model_id))
    
    # First pass: filter out dated models if a non-dated equivalent exists
    # This helps remove deprecated models like claude-3-5-sonnet-20240620
    model_groups = {}
    for model_id in provider_models:
        base = get_base_model_name(model_id)
        if base not in model_groups:
            model_groups[base] = []
        model_groups[base].append(model_id)
    
    # For each group, prefer: non-dated > latest > most recent date
    deduplicated_models = []
    for base, variants in model_groups.items():
        if len(variants) == 1:
            # Only one variant - keep it unless it's a dated version and looks old
            model = variants[0]
            # Skip very old dated models (pre-2025) - they're likely deprecated
            date_match = re.search(r'-(\d{8})$', model)
            if date_match and int(date_match.group(1)) < 20250101:
                continue  # Skip old dated models
            deduplicated_models.append(model)
        else:
            # Multiple variants - pick the best one
            def variant_priority(v):
                # Prefer: non-dated clean names > latest > newer dates
                if 'latest' in v:
                    return (1, 0, v)  # Latest is good but not as clean
                elif re.search(r'-\d{8}$', v):
                    # Has date - lower priority, but newer is better
                    date_match = re.search(r'-(\d{8})$', v)
                    date = date_match.group(1) if date_match else "00000000"
                    return (2, -int(date), v)
                else:
                    # No date, no latest - these are the cleanest names
                    return (0, 0, v)
            
            variants.sort(key=variant_priority)
            deduplicated_models.append(variants[0])
    
    provider_models = deduplicated_models

    # Sort models by priority (flagship first) then alphabetically
    provider_models.sort(key=lambda m: (-get_model_priority(m, selected_provider), m))

    # Build model choices from the actual available models
    model_choices = []
    for model_id in provider_models:
        desc = get_model_description(model_id, selected_provider)
        model_choices.append((model_id, desc))

    # Show model choices
    if model_choices:
        # Limit display to top 10 models (sorted by priority)
        display_choices = model_choices[:10]
        
        # First option is always "Recommended" which auto-selects the best (flagship)
        best_model, best_desc = model_choices[0]
        console.print(f"  [cyan]1.[/cyan] [green]Recommended[/green]: {best_model} [dim]({best_desc or 'flagship'})[/dim]")
        
        for i, (model_id, description) in enumerate(display_choices[1:], 2):
            if description:
                console.print(f"  [cyan]{i}.[/cyan] {model_id} [dim]({description})[/dim]")
            else:
                console.print(f"  [cyan]{i}.[/cyan] {model_id}")
        
        # Add option to see all models if there are more
        extra_options = 1  # Start with "Enter custom model name"
        if len(model_choices) > 10:
            console.print(f"  [cyan]{len(display_choices) + 1}.[/cyan] See all {len(model_choices)} models")
            extra_options += 1
        console.print(f"  [cyan]{len(display_choices) + extra_options}.[/cyan] Enter custom model name")
        console.print()

        max_choice = len(display_choices) + extra_options
        choice = Prompt.ask(
            "Select model",
            choices=[str(i) for i in range(1, max_choice + 1)],
            default="1"
        )
        choice_idx = int(choice) - 1

        if choice_idx == 0:
            # Recommended - pick the first available model (flagship for this provider)
            selected_model = model_choices[0][0]
        elif choice_idx == len(display_choices) + extra_options - 1:
            # Custom model name (always last option)
            console.print()
            console.print("[dim]Enter the exact model name (e.g., claude-opus-4, gpt-4o)[/dim]")
            selected_model = Prompt.ask("Model name")
        elif len(model_choices) > 10 and choice_idx == len(display_choices):
            # Show all models for this provider
            console.print()
            console.print(f"[bold]All {len(model_choices)} models for this provider:[/bold]")
            console.print()

            for i, (model_id, desc) in enumerate(model_choices, 1):
                if desc:
                    console.print(f"  [cyan]{i}.[/cyan] {model_id} [dim]({desc})[/dim]")
                else:
                    console.print(f"  [cyan]{i}.[/cyan] {model_id}")

            console.print()
            choice = Prompt.ask(
                "Select model number",
                choices=[str(i) for i in range(1, len(model_choices) + 1)],
                default="1"
            )
            selected_model = model_choices[int(choice) - 1][0]
        else:
            # Specific model chosen (offset by 1 for the "Recommended" option)
            selected_model = display_choices[choice_idx][0]
    else:
        # No models found for this provider - likely missing plugin
        console.print(f"[yellow]No models found for {provider_choices[int(provider_choice) - 1][1]}[/yellow]")
        console.print()
        console.print("This usually means the llm plugin isn't installed.")
        console.print("Install the required plugin:")
        if selected_provider == "anthropic":
            console.print("  [cyan]pip install llm-anthropic[/cyan]")
        elif selected_provider == "google":
            console.print("  [cyan]pip install llm-gemini[/cyan]")
        elif selected_provider == "local":
            console.print("  [cyan]pip install llm-ollama[/cyan]")
        console.print()
        console.print("Or enter a custom model name:")
        selected_model = Prompt.ask("Model name")

    console.print()
    console.print(f"[green]✓[/green] Selected: [cyan]{selected_model}[/cyan]")

    # Check if API key is already available for this provider
    key_source = "llm"  # Always use llm's key management
    
    key_urls = {
        "anthropic": "https://console.anthropic.com/settings/keys",
        "openai": "https://platform.openai.com/api-keys",
        "google": "https://makersuite.google.com/app/apikey",
    }
    
    # Map our provider names to llm key names
    llm_key_names = {
        "anthropic": "anthropic",
        "openai": "openai", 
        "google": "gemini",
    }
    
    # For local models, no key needed
    if selected_provider == "local":
        console.print()
        console.print("[green]✓[/green] Local models don't require an API key")
    elif detected_keys.get(selected_provider):
        # Key detected - let user choose to use it or enter a different one
        console.print()
        console.print(f"[green]✓[/green] API key detected in environment")
        console.print()
        console.print("  [cyan]1.[/cyan] Use detected key")
        console.print("  [cyan]2.[/cyan] Enter a different key")
        console.print()
        
        key_choice = Prompt.ask("Select", choices=["1", "2"], default="1")
        
        if key_choice == "2":
            console.print()
            key_url = key_urls.get(selected_provider, "")
            if key_url:
                console.print(f"Get a new key: [cyan]{key_url}[/cyan]")
                console.print()
            api_key = Prompt.ask("Paste your API key", password=True)
            
            # Save to llm's keys.json
            _save_llm_key(llm_key_names.get(selected_provider, selected_provider), api_key)
    else:
        # No key detected - prompt user to enter one
        console.print()
        
        key_url = key_urls.get(selected_provider, "")
        
        console.print(f"[bold]Step 3:[/bold] Enter your API key")
        console.print()
        if key_url:
            console.print(f"Get one here: [cyan]{key_url}[/cyan]")
            console.print()
        
        api_key = Prompt.ask("Paste your API key", password=True)
        
        # Save to llm's keys.json
        _save_llm_key(llm_key_names.get(selected_provider, selected_provider), api_key)
        console.print(f"[green]✓[/green] Key saved")

    # Create config (API keys are stored by llm, not in our config)
    config = {
        "version": "0.1.0",
        "api": {
            "model": selected_model,
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


def run_search_setup_wizard() -> None:
    """
    Run the interactive search setup wizard to configure web search providers.
    """
    console.print()
    console.print(Panel.fit(
        "[bold]Web Search Setup[/bold]\n\n"
        "Configure a search provider for weather, news, docs, and current events.",
        border_style="cyan"
    ))
    console.print()

    # Define search providers with their info
    # Note: "key" must match what tools.py expects in config["api_keys"]
    search_providers = [
        {
            "key": "tavily",
            "name": "Tavily",
            "description": "AI-optimized search, clean results",
            "free_tier": "1,000 searches/month",
            "url": "https://tavily.com",
            "env_var": "TAVILY_API_KEY",
        },
        {
            "key": "serper",
            "name": "Serper",
            "description": "Google search results",
            "free_tier": "2,500 searches/month",
            "url": "https://serper.dev",
            "env_var": "SERPER_API_KEY",
        },
        {
            "key": "brave_search",
            "name": "Brave Search",
            "description": "Privacy-focused search",
            "free_tier": "2,000 searches/month",
            "url": "https://brave.com/search/api",
            "env_var": "BRAVE_SEARCH_API_KEY",
        },
        {
            "key": "bing_search",
            "name": "Bing Search",
            "description": "Microsoft Bing results",
            "free_tier": "1,000 searches/month",
            "url": "https://portal.azure.com",
            "env_var": "BING_SEARCH_KEY",
        },
    ]

    # Check for existing keys
    console.print("[bold]Available providers:[/bold]")
    console.print()
    
    # Load existing config to check for saved keys
    try:
        config = load_config()
    except:
        config = {}
    
    saved_keys = config.get("api_keys", {})
    
    for i, provider in enumerate(search_providers, 1):
        status = ""
        env_key = os.environ.get(provider["env_var"])
        saved_key = saved_keys.get(provider["key"])
        
        if env_key:
            status = " [green](key in env)[/green]"
        elif saved_key:
            status = " [green](key saved)[/green]"
        
        console.print(f"  [cyan]{i}.[/cyan] {provider['name']}{status}")
        console.print(f"      [dim]{provider['description']} - {provider['free_tier']}[/dim]")
        console.print()

    console.print(f"  [cyan]{len(search_providers) + 1}.[/cyan] Skip for now")
    console.print()

    choice = Prompt.ask(
        "Select a provider to configure",
        choices=[str(i) for i in range(1, len(search_providers) + 2)],
        default="1"
    )

    if int(choice) > len(search_providers):
        console.print()
        console.print("[yellow]Skipped search setup.[/yellow]")
        console.print("You can run [cyan]wtf --setup-search[/cyan] later to configure.")
        console.print()
        return

    selected = search_providers[int(choice) - 1]
    
    console.print()
    console.print(f"[bold]Setting up {selected['name']}[/bold]")
    console.print()
    console.print(f"1. Go to: [cyan]{selected['url']}[/cyan]")
    console.print("2. Sign up for a free account")
    console.print("3. Copy your API key")
    console.print()

    # Check if key already exists
    existing_env = os.environ.get(selected["env_var"])
    existing_saved = saved_keys.get(selected["key"])
    
    if existing_env:
        console.print(f"[green]✓[/green] Key already set in environment ({selected['env_var']})")
        console.print()
        use_existing = Prompt.ask(
            "Use existing key?",
            choices=["y", "n"],
            default="y"
        )
        if use_existing.lower() == "y":
            console.print()
            console.print(f"[green]✓[/green] Using existing {selected['name']} key from environment")
            console.print()
            return
    elif existing_saved:
        console.print(f"[green]✓[/green] Key already saved in config")
        console.print()
        use_existing = Prompt.ask(
            "Use existing key?",
            choices=["y", "n"],
            default="y"
        )
        if use_existing.lower() == "y":
            console.print()
            console.print(f"[green]✓[/green] Using existing {selected['name']} key")
            console.print()
            return

    # Get new key
    api_key = Prompt.ask("Paste your API key", password=True)
    
    if not api_key.strip():
        console.print("[yellow]No key entered. Skipping.[/yellow]")
        console.print()
        return

    # Save to config
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][selected["key"]] = api_key.strip()
    save_config(config)

    console.print()
    console.print(f"[green]✓[/green] {selected['name']} API key saved!")
    console.print()
    console.print("Try it out:")
    console.print("  [cyan]wtf what's the weather in SF?[/cyan]")
    console.print()


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


def _forget_memory_by_key(key: str) -> None:
    """Forget a specific memory by exact key."""
    memories = load_memories()
    if not memories:
        console.print("[yellow]No memories to forget[/yellow]")
        console.print()
        return

    if key not in memories:
        console.print(f"[yellow]Memory '{key}' not found[/yellow]")
        console.print()
        console.print("Current memories:")
        for mem_key in memories.keys():
            console.print(f"  - {mem_key}")
        console.print()
        return

    delete_memory(key)
    console.print(f"[green]✓[/green] Forgot about: [cyan]{key}[/cyan]")
    console.print()


def _forget_memory(query: str) -> None:
    """DEPRECATED: Old natural language forget function. Use _forget_memory_by_key instead."""
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


# Memory commands removed - all memory operations now handled by AI tools
# This keeps the interface simple: only CLI flags for system operations,
# natural language for everything else


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
    recent_convos = get_recent_conversations(count=3)  # Include last 3 conversations
    context_prompt = build_context_prompt(commands, git_status, env_context, memories, shell_type, recent_convos)
    full_prompt = f"{context_prompt}\n\nUSER QUERY:\n{query}"

    try:
        # Query AI with tools
        # Note: We don't use a spinner here because it conflicts with permission prompts
        console.print()
        console.print("[dim]🤖 Thinking...[/dim]")
        result = query_ai_with_tools(
            prompt=full_prompt,
            config=config,
            system_prompt=system_prompt,
            max_iterations=20,
            env_context=tool_env_context
        )

        # Process tool calls and print outputs
        console.print()

        # Print user-facing tool outputs
        for tool_call in result["tool_calls"]:
            tool_name = tool_call["name"]
            tool_result = tool_call["result"]

            # run_command outputs
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

            # write_file outputs
            elif tool_name == "write_file" and tool_result.get("should_print", False):
                file_path = tool_call["arguments"].get("file_path", "")
                action = tool_result.get("action", "wrote")
                if tool_result.get("success"):
                    console.print(f"[green]✓[/green] {action.capitalize()} [cyan]{file_path}[/cyan]")
                else:
                    error = tool_result.get("error", "Unknown error")
                    console.print(f"[red]✗[/red] Failed to write {file_path}: {error}")
                console.print()

            # edit_file outputs
            elif tool_name == "edit_file" and tool_result.get("should_print", False):
                file_path = tool_call["arguments"].get("file_path", "")
                if tool_result.get("success"):
                    console.print(f"[green]✓[/green] Edited [cyan]{file_path}[/cyan]")
                else:
                    error = tool_result.get("error", "Unknown error")
                    console.print(f"[red]✗[/red] Failed to edit {file_path}: {error}")
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

    except UserCancelledError as e:
        # User said "no" to a command - exit gracefully with their message
        console.print()
        console.print(f"[yellow]{e}[/yellow]")
        console.print()
        return  # Don't log as error

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
    parser.add_argument('--model', type=str, help='Override AI model (e.g., gpt-4, claude-3-5-sonnet)')
    parser.add_argument('--provider', type=str, help='Override AI provider (anthropic, openai, google)')
    parser.add_argument('--verbose', action='store_true', help='Show diagnostic info')
    parser.add_argument('--reset', action='store_true', help='Reset config to defaults')
    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    parser.add_argument('--setup-search', action='store_true', help='Setup web search provider')
    parser.add_argument('--setup-error-hook', action='store_true', help='Setup error hook')
    parser.add_argument('--setup-not-found-hook', action='store_true', help='Setup not-found hook')
    parser.add_argument('--remove-hooks', action='store_true', help='Remove shell hooks')
    parser.add_argument('--upgrade', action='store_true', help='Upgrade wtf and all AI model plugins')

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


def _handle_upgrade_flag() -> None:
    """Handle --upgrade flag to upgrade wtf and all AI model plugins."""
    import subprocess
    
    console.print()
    console.print("[bold]Upgrading wtf and AI model plugins...[/bold]")
    console.print()
    
    # Packages to upgrade: wtf-ai and all llm plugins
    packages = [
        "wtf-ai",
        "llm",
        "llm-anthropic",
        "llm-gemini", 
        "llm-ollama",
    ]
    
    for package in packages:
        console.print(f"[dim]Upgrading {package}...[/dim]")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", package],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Extract version from output if possible
                console.print(f"  [green]✓[/green] {package} upgraded")
            else:
                console.print(f"  [yellow]⚠[/yellow] {package} - {result.stderr.strip() or 'failed'}")
        except Exception as e:
            console.print(f"  [red]✗[/red] {package} - {e}")
    
    console.print()
    console.print("[green]✓[/green] Upgrade complete!")
    console.print()
    
    # Show new version
    from wtf import __version__
    # Reload to get new version (won't work in same process, but show current)
    console.print(f"[dim]Current version: {__version__}[/dim]")
    console.print("[dim]Restart your terminal to use the new version.[/dim]")
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

        # Override config with CLI flags if provided
        if args.model:
            config['api'] = config.get('api', {})
            config['api']['model'] = args.model
        if args.provider:
            config['api'] = config.get('api', {})
            config['api']['provider'] = args.provider

        # Use tool-based approach (simpler than state machine)
        handle_query_with_tools(query, config)
    elif args.model:
        # --model without query = change default model permanently
        old_model = config.get('api', {}).get('model', 'unknown')
        config['api'] = config.get('api', {})
        config['api']['model'] = args.model
        save_config(config)
        console.print()
        console.print(f"[green]✓[/green] Default model changed from [dim]{old_model}[/dim] to [cyan]{args.model}[/cyan]")
        console.print()
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

    if args.setup_search:
        run_search_setup_wizard()
        sys.exit(0)

    _handle_hooks_flags(args)

    if args.upgrade:
        _handle_upgrade_flag()

    # Load or setup config
    config = _load_or_setup_config()

    # Handle query
    _handle_query(args, config)

    sys.exit(0)


if __name__ == "__main__":
    main()
