# Initial Project Prompt

## Overview
I want to make a CLI tool for getting AI assistance in the terminal. The command will be "wtf" and then whatever follows it should be instructions to an AI.

## Setup

- It should automatically look for OpenAI, Gemini, or Anthropic API key variables available already and ask the user if one of those should be used. Otherwise have some other way (see how tAI does it) to get a key from them.
- It should be really easy to install, just with pip or brew or a URL to curl from GitHub.

## Config

- There should be global config created on install or first use.
- The config folder should have a `wtf.md` where the user can add custom instructions.
- There should be an allowlist of commands the agent is always allowed to run.

## Usage

A user will write something like:

```bash
> wtf I'm locked into some git merge how do i get out?
```

or sometimes just:

```bash
> wtf
```

And there will be an agent that responds. The agent should also be fed the last 5 commands of the `zsh_history` as context. If needed for more context, the agent can ask to rerun one or more of the most recently run commands to get the output for its context in order to help the user debug the issue they're seeing. Alternatively we could have a log of the terminal output but for now we're just getting context this way. If bash has an equivalent to the `zsh_history` incorporate that but otherwise just focus on making it work for zsh first.

### Command Execution

When running commands the agent should first check if it's allowed to in the config's allow list. Then it should have an interface asking the user if it's okay to run a command. Put it inside a kind of box like tAI does and ask the user for permission to run it. Explain above the command what you're doing and why very briefly. The user can respond with 3 options similar to how claude-code does it:

1. [Y]es
2. Yes and [a]lways allow {cmd}
3. [n]o

Yes is the default. If they choose Y or a then run the command and continue your work. If the work is done give an appropriate explanation (brief if it's a simple thing like helping them remember the right git command, longer if they're asking for an explanation and next steps on an error).

### Conversation History

After the explanation the agent and the wtf command is done. The discussion should be kept in a log file (probably JSON) that also gives each message an ID that is the input that was given to the wtf command.

In this way the user can keep chatting - if after the command they have more follow up they can say:

```bash
> wtf "can you explain that more"
```

or

```bash
> wtf don't do it that way, instead do ...
```

And when the agent starts and sees that some recent commands were "wtf" it can lookup as much history as it wants. A useful thing for this would be that the agent logs should also somewhere have the agent write a "context_summary" about what's going on - what's the user doing and been working on (maybe with you) and where are we at - what's the problem been and where have we currently been. This doesn't go directly to the user but captures the reasoning (and helps with it) and should be part of the log. So that the next wtf that might look at it will be able to have the context.

## Technical Considerations

Maybe use Simon Willison's LLM package so that we can be agent agnostic?

## Task

First make a spec of the features and functionality and then also make another doc with a review of the spec and project - as if you were an expert programmer giving an opinion on what is great and bad about the wtf spec and what you would change or add if you had built it.

After that we'll iterate on the spec and then start building.
