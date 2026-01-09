# wtf

Because working in the command line often leaves you asking `wtf`.

## Quick install

```bash
curl -sSL https://raw.githubusercontent.com/davefowler/wtf-terminal-ai/main/install.sh | bash
```

## What is this?

`wtf` is a sometimes helpful, usually unpleasant AI assistant for your terminal. It is there for you when you mess up. 

Hit an error? Just type `wtf`. Made a mistake? Say `wtf undo`. Need to install something? `wtf install [thing]`. Forgot a command? Ask `wtf can you back me out of this failed merge attempt?`

No flags to remember. No manual pages written in ancient Sumerian. Just describe what you want in plain English (or whatever language you prefer, we're not picky).

## wtf does this exist?

Brain rot is real, as is the excess of information that insists on you remembering it.  Like any good drug `wtf` offers you relief from your brain rot condition while quickening its ascent.  

Why spend time challenging your mind with learning tools, commands, and how things work when its so deliciously easy to just let the ai do the thinking for you?

## wtf is this for?

### Data Analysts & Non-Engineers

More and more people are now able to work with code and command lines: data analysts using git for dbt models, designers and product managers vibe coding prototype features, marketers working with static sites. `wtf` helps with setups, remembering commands, and gets them out of jams when things inevitably break.

### Engineers

There are so many tools and commands to remember. You get stuck, you make mistakes, you get slowed down having to go read docs or switch over to ask your llm of choice. But now you can just stay in your terminal and have it answer or even fix your problems as they come up.

## Quick Example

```bash
$ git rebase -i HEAD~5
# Oh no, you messed up the rebase
$ wtf

I see you are in the middle of a rebase. Let me guess - you picked
the wrong commit? Happens to the best of us. Actually, it happens
to everyone. Rebasing is just UI/UX for masochists.

Here is how to get out:

$ git rebase --abort
```

## Key Features

- **Context Aware**: Knows your shell history, git status, and project type
- **Permission System**: Won't run dangerous commands without asking
- **Undo Feature**: Analyzes history and suggests safe reversals
- **Memories**: Learns your preferences ("I use npm, not yarn")
- **Multi-Provider AI**: Works with Anthropic, OpenAI, Google, or locally via Ollama
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
wtf what is the answer to life the universe and everything?
```

The setup wizard will ask you to:

1. Choose your AI provider (Anthropic, OpenAI, Google, or local via Ollama)
2. Enter your API key (or skip if using local models!)
3. Select your default model

That's it. You're ready to make mistakes and let AI fix them.

## Examples

Stop reading docs like these.  In the future just ask `wtf`:

```bash
wtf what are some examples of what you can do?
```


chat with it and ask questions like any other llm

```bash
wtf what is the oldest city in the world?
```

get yourself out of a jam

```bash
wtf get me out of this githole
```

have it try to undo whatever you just f'd up

```bash
wtf undo
```

install something for you (politeness optional)

```bash
wtf please install x
```

figure out what you should install

```bash
wtf i want to check my internet speed.  can you install something to do that and check?
```

have it remember things about you, your preferences and your projects

```bash
wtf remember that i live in San Francisco and my favorite editor is emacs
```

search for things ([if search key added](config/web-search.md))

```bash
wtf is it nice outside?
```

pick yourself up

```bash
wtf i need some inspiration today.  hit me with a quote
```

replace your therapist (disclaimer: this is not and endorced use case)

```bash
wtf "okay here's a scenerio, tell me AITA? ..."
```

debug errors

```bash
wtf just happend?  fix?
```


## What's Next?

- [Getting Started](getting-started.md) - Detailed installation guide
- [Setup](setup.md) - Configure wtf for first use
- [Quick Tour](quick-tour.md) - See what wtf can do
- [FAQ](faq.md) - Questions we've asked ourselves


## Philosophy

CLI tools have 47 flags and you need to consult the manual every time. And then the manual is written like a legal document from 1987.  This can really harsh your vibe coding.

`wtf` has a different philosophy: you shouldn't need to (read: can't) remember anything. Instead, just describe what you want. The AI figures out the rest.

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
