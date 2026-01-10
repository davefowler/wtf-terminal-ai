# Web Search

`wtf` can search the web to answer questions about current events, documentation, weather, and more.

## Free Search Options

### Option 1: DuckDuckGo (Easiest - FREE & Unlimited)

Install the `duckduckgo-search` library for **free, unlimited** web search with no API key:

```bash
pip install duckduckgo-search
```

**That's it!** `wtf` will automatically use DuckDuckGo for web searches.

!!! tip "Recommended for Most Users"
    DuckDuckGo search is completely free, requires no API key, and works great for most queries.
    Just install the package and you're done!

---

### Option 2: OpenAI Native Search

If you're using **OpenAI**, you can use a model with **built-in web search**:

```bash
# Configure wtf to use OpenAI's search model
$ wtf --setup
# Select: gpt-4o-search-preview or gpt-4o-mini-search-preview
```

**No additional API keys needed.** The model will automatically search the web when relevant.

!!! note "OpenAI Search Models"
    - `gpt-4o-search-preview` - Best quality, ~$25/1000 searches
    - `gpt-4o-mini-search-preview` - Faster & cheaper
    
    These models search automatically - you don't need to configure anything else.

---

## API-Based Search (Optional)

If you prefer API-based search or DuckDuckGo is rate-limited, you can configure one of these:

### Tavily (Recommended API)

**Best for:** AI-optimized results with summaries

- ✅ **1,000 free searches/month**
- ✅ **No credit card required**
- ✅ Returns AI-friendly summaries
- ✅ Very popular for AI agents

**Get your key:** [tavily.com](https://tavily.com)

**Add it to wtf:**
```bash
$ wtf here is my tavily api key tvly-YOUR_KEY_HERE
```

Or set manually:
```bash
export TAVILY_API_KEY="tvly-YOUR_KEY"
```

---

## Recommended Search APIs

### 1. Serper.dev (Recommended)

**Best for:** Most users - simple, reliable, Google results

- ✅ **2,500 free searches/month**
- ✅ **Google search results** (high quality)
- ✅ **No credit card required** for free tier
- ✅ Very easy API

**Get your key:** [serper.dev](https://serper.dev) (sign up takes 2 minutes)

**Add it to wtf:**
```bash
$ wtf here is my serper api key sk_YOUR_KEY_HERE
```

Or set manually:
```bash
export SERPER_API_KEY="sk_YOUR_KEY"
```

---

### 2. Bing Search API

**Best for:** Microsoft Azure users or those who need more searches

- ✅ **1,000 free searches/month** (Free tier on Azure)
- ✅ **Bing search results**
- ⚠️ Requires Azure account
- ⚠️ Slightly more complex setup

**Get your key:** [Microsoft Azure Portal](https://portal.azure.com) → Create Bing Search resource

**Add it to wtf:**
```bash
$ wtf here is my bing search api key YOUR_KEY
```

Or set manually:
```bash
export BING_SEARCH_API_KEY="YOUR_KEY"
```

---

### 3. Brave Search

**Best for:** Privacy-conscious users

- ✅ **2,000 free searches/month**
- ✅ **Privacy-focused** search engine
- ✅ **No credit card required**
- ✅ Independent search index

**Get your key:** [brave.com/search/api](https://brave.com/search/api)

**Add it to wtf:**
```bash
$ wtf here is my brave search api key YOUR_KEY
```

Or set manually:
```bash
export BRAVE_SEARCH_API_KEY="YOUR_KEY"
```

---

## Search Priority

`wtf` automatically uses the best available search method:

1. **Native OpenAI Search** (if using `gpt-4o-search-preview` or `gpt-4o-mini-search-preview`)
   - Built into the model, no extra config needed
2. **DuckDuckGo** (if `duckduckgo-search` installed) - FREE & unlimited!
3. **Tavily** (if API key configured) - AI-optimized results
4. **Serper** (if API key configured) - Google results
5. **Brave** (if API key configured) - Privacy-focused
6. **Bing** (if API key configured) - Microsoft Azure
7. **DuckDuckGo Instant Answers** (always available) - Limited to encyclopedic facts only

When using native search models, custom search tools are automatically disabled to avoid redundancy.

## Testing Your Search

Once you've added a key, try it:

```bash
$ wtf "what's the weather in San Francisco?"
$ wtf "find documentation for React hooks"
$ wtf "latest news about AI"
```

With a search key, `wtf` can:
- ✅ Check weather anywhere
- ✅ Find documentation and guides
- ✅ Look up current news and events
- ✅ Research technical questions
- ✅ Find specific information across the web

## Troubleshooting

### "Search API key not configured"

You haven't added a search key yet. Run:

```bash
$ wtf here is my brave search api key YOUR_KEY
```

### "API key is invalid"

Double-check you copied the entire key correctly. Visit the provider's website to verify your key is active.

### "Rate limit exceeded"

You've used up your free monthly searches. Either:
- Wait until next month for the free tier to reset
- Upgrade your plan with the provider
- Switch to a different search provider

## FAQ

**Do I need this?**

Only if you want `wtf` to:
- Check weather
- Find documentation
- Look up news and current events
- Research questions that require web search

Basic terminal help works fine without it.

**Which option should I use?**

- **Easiest:** Install `duckduckgo-search` - free, unlimited, no API key!
- **OpenAI users:** Use `gpt-4o-search-preview` - no extra setup needed
- **Want API-based:** Get a **Tavily** key (1,000 free/month) or **Serper** key (2,500 free/month)

**Is this secure?**

Your API key is stored in your system keychain (macOS/Linux) or securely in `~/.config/wtf/config.yaml`. Keys are only used to make search requests on your behalf.

**Will Anthropic Claude get native search?**

Anthropic Claude has a native web search tool, but it's not yet supported through the llm library we use. This may be added in a future update.

**What if DuckDuckGo is rate-limited?**

DuckDuckGo may occasionally rate-limit requests. If this happens, consider:
- Waiting a few minutes and trying again
- Installing Tavily (1,000 free searches/month, no credit card)
- Using an OpenAI search model

## Next Steps

- [Setup](../setup.md) - Configure wtf for first use
- [API Keys](api-keys.md) - Manage all your AI and search keys
- [Configuration](files.md) - Learn about other configurable features
