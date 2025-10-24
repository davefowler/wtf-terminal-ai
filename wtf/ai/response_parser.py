"""Parse AI responses to extract commands."""

import re
from typing import List, Dict, Any


def extract_commands(ai_response: str) -> List[Dict[str, str]]:
    """
    Extract commands from AI response.

    Looks for:
    1. Commands in markdown code blocks (```bash or ```sh)
    2. Commands in fancy boxes (╭─ style)
    3. Commands after $ prompt

    Args:
        ai_response: The AI's response text

    Returns:
        List of dicts with:
        - command: The command to execute
        - explanation: Why the command is needed
        - allowlist_pattern: Suggested pattern for allowlist
    """
    commands = []

    # Pattern 1: Markdown code blocks with bash/sh
    code_block_pattern = r'```(?:bash|sh)\n(.*?)\n```'
    for match in re.finditer(code_block_pattern, ai_response, re.DOTALL):
        code = match.group(1).strip()
        lines = code.split('\n')

        for line in lines:
            # Skip comments and empty lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Remove $ prompt if present
            if line.startswith('$ '):
                line = line[2:]

            if line:
                commands.append({
                    'command': line,
                    'explanation': '',
                    'allowlist_pattern': _suggest_allowlist_pattern(line)
                })

    # Pattern 2: Lines starting with $ (shell prompt)
    prompt_pattern = r'^\$ (.+)$'
    for match in re.finditer(prompt_pattern, ai_response, re.MULTILINE):
        cmd = match.group(1).strip()
        if cmd:
            # Check if not already added from code block
            if not any(c['command'] == cmd for c in commands):
                commands.append({
                    'command': cmd,
                    'explanation': '',
                    'allowlist_pattern': _suggest_allowlist_pattern(cmd)
                })

    # Pattern 3: Look for explanation text before commands
    # Try to find context around each command
    for cmd_dict in commands:
        cmd = cmd_dict['command']
        # Look for text before the command in the response
        cmd_index = ai_response.find(cmd)
        if cmd_index > 0:
            # Get ~200 chars before command
            context_start = max(0, cmd_index - 200)
            context = ai_response[context_start:cmd_index].strip()

            # Extract last sentence or line as explanation
            lines = context.split('\n')
            if lines:
                explanation = lines[-1].strip()
                # Clean up markdown and formatting
                explanation = re.sub(r'[*_`]', '', explanation)
                cmd_dict['explanation'] = explanation[:100]  # Limit length

    return commands


def _suggest_allowlist_pattern(cmd: str) -> str:
    """
    Suggest an appropriate allowlist pattern for a command.

    Args:
        cmd: Command string

    Returns:
        Suggested pattern for allowlist
    """
    cmd = cmd.strip()

    # For multi-command tools, include the subcommand
    parts = cmd.split()
    if not parts:
        return cmd

    base_cmd = parts[0]

    # Commands that should include subcommand in pattern
    subcommand_tools = ['git', 'docker', 'npm', 'pip', 'cargo', 'go']

    if base_cmd in subcommand_tools and len(parts) > 1:
        # Include subcommand
        return f"{base_cmd} {parts[1]}"

    # For simple commands, just use base
    simple_commands = ['ls', 'cat', 'echo', 'pwd', 'cd']

    if base_cmd in simple_commands:
        return base_cmd

    # For dangerous commands with safety flags, include the flags
    if base_cmd == 'rm' and '-i' in cmd:
        return 'rm -i'

    # Default: first two parts or just base command
    if len(parts) > 1:
        return f"{base_cmd} {parts[1]}"

    return base_cmd
