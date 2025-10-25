# Web Search

By default, `wtf` has limited web search capabilities using DuckDuckGo's Instant Answer API - it only works for encyclopedic facts like "What is Python" or "Who is Ada Lovelace".

For real web search (weather, news, documentation, current events), you'll need to add a search API key. It's a quick 5-minute setup that dramatically improves `wtf`'s ability to help.

!!! note "Search Requires an API Key"
    Unlike other features, web search (except basic DuckDuckGo facts) requires an external API key. Don't worry - the recommended options have generous free tiers and don't require a credit card.

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

## ✅ All Search Providers Implemented

`wtf` will automatically use whichever search API key you have configured. Priority order:
1. **Serper** (if configured) - Best quality, Google results
2. **Brave** (if configured) - Privacy-focused
3. **Bing** (if configured) - Microsoft Azure
4. **DuckDuckGo** (always available) - Limited to encyclopedic facts only

All three major search APIs are now fully implemented and ready to use!

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

**Which one should I use?**

**Serper** for most people (when implemented). **Brave Search** for now. Both have generous free tiers.

**Is this secure?**

Your API key is stored in your system keychain (macOS/Linux) or securely in `~/.config/wtf/config.yaml`. Keys are only used to make search requests on your behalf.

## Next Steps

- [Setup](../setup.md) - Configure wtf for first use
- [API Keys](api-keys.md) - Manage all your AI and search keys
- [Configuration](files.md) - Learn about other configurable features
