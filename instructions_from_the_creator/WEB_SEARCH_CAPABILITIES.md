# Web Search Capabilities in wtf

## The User Examples

```bash
# Weather check
wtf is it nice outside?

# Documentation fetching  
wtf can you get me the docs on connecting react to supabase
```

Both need web access. Here are the solutions:

---

## ✅ Option 1: Safe curl Commands (v0.1 - Easiest)

**Already works!** The agent can use `curl` for safe read-only web requests.

### Weather Example

```bash
$ wtf is it nice outside?

Let me check the weather for you.

╭─────────────────────────────────────────────╮
│ $ curl wttr.in/san-francisco?format=3      │
╰─────────────────────────────────────────────╯

☀️  San Francisco: +18°C, Sunny

It's nice outside! 18°C and sunny. Good time for a walk.
```

**How it works:**
- `curl` is in `SAFE_READONLY_COMMANDS` (auto-allowed)
- `wttr.in` is a public weather service (no API key needed)
- Agent can call it without permission prompt

### Documentation Example

```bash
$ wtf can you get me the docs on connecting react to supabase

Let me fetch the Supabase React documentation.

╭─────────────────────────────────────────────╮
│ $ curl -s https://supabase.com/docs/guides/getting-started/quickstarts/reactjs │
╰─────────────────────────────────────────────╯

[AI reads the HTML/markdown and summarizes]

Here's how to connect React to Supabase:

1. Install the client library:
   npm install @supabase/supabase-js

2. Initialize the client:
   [shows code example]

3. Use in your components:
   [shows code example]

Full docs: https://supabase.com/docs/guides/getting-started/quickstarts/reactjs
```

**Limitations:**
- Only works for sites that return plain text/markdown
- HTML sites need parsing (could be messy)
- No search ranking (agent needs to know the URL)

---

## ✅ Option 2: Gemini with Search Grounding (v0.1 - Works Today)

**Use Google Gemini models with built-in web search** (via `llm` library).

### Installation

```bash
# Install Gemini plugin for llm
llm install llm-gemini

# Set API key
llm keys set gemini
# Paste your Google API key from https://aistudio.google.com/app/apikey

# Use Gemini with wtf
wtf --model gemini-1.5-pro "is it nice outside in San Francisco?"
```

### How It Works

Gemini models have **search grounding** built-in:
- Model can search the web automatically
- No code changes needed in wtf
- Just use a Gemini model via `llm`

### Weather Example

```bash
$ wtf --model gemini-1.5-pro "is it nice outside in San Francisco?"

[Gemini searches web for SF weather]

The current weather in San Francisco is 64°F (18°C) and sunny. It's a nice 
day outside!
```

### Documentation Example

```bash
$ wtf --model gemini-1.5-pro "get me the docs on connecting react to supabase"

[Gemini searches for Supabase React docs]

Here's how to connect React to Supabase:
[Provides summary from official docs with links]
```

**Pros:**
- Works today with zero code changes
- Real web search with ranking
- Handles complex queries
- No URL needed, Gemini finds relevant pages

**Cons:**
- Requires Gemini API key
- User must explicitly use Gemini model
- Costs money (though Gemini has generous free tier)

---

## ✅ Option 3: Web Search MCP Server (v0.2 - Best Long-Term)

**Add a web search MCP server** for structured web access.

### Installation (future)

```bash
# Install web search MCP server
npm install -g @modelcontextprotocol/server-brave-search
# or
npm install -g @modelcontextprotocol/server-exa

# Configure in wtf
wtf --mcp add brave-search
```

### Configuration

```json
// ~/.config/wtf/mcp_servers.json
{
  "brave-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
      "BRAVE_API_KEY": "${BRAVE_API_KEY}"
    }
  }
}
```

### How It Works

```bash
$ wtf is it nice outside?

[wtf detects weather query]
[Calls Brave Search MCP: "weather san francisco"]
[Gets structured weather data]

It's 64°F and sunny in San Francisco. Nice day outside!
```

**Pros:**
- Structured search results
- Multiple search providers (Brave, Exa, Google, etc.)
- Can combine multiple sources
- Standardized protocol

**Cons:**
- Requires MCP server setup
- Not in v0.1
- More complexity

---

## 🎯 Recommendation: Start with Options 1 & 2

### For v0.1:

**Enable both approaches:**

1. **Update SAFE_READONLY_COMMANDS** to explicitly include curl for web:
   ```python
   SAFE_READONLY_COMMANDS = {
       "curl wttr.in",       # Weather
       "curl httpie.io",     # HTTP testing
       "curl ifconfig.me",   # IP check
       # etc.
   }
   ```

2. **Document Gemini usage** in README:
   ```bash
   # For web search capabilities
   llm install llm-gemini
   wtf --model gemini-1.5-pro "search-based query"
   ```

3. **Update system prompt** to mention web capabilities:
   ```
   WEB ACCESS:
   You can access the web using curl for read-only requests:
   - Weather: curl wttr.in/location
   - IP info: curl ifconfig.me
   - HTTP testing: curl httpie.io
   
   If user has Gemini model, you have full web search via search grounding.
   Check if model supports search before trying to use it.
   ```

### For v0.2+:

Add MCP web search server support for structured search.

---

## Implementation for v0.1

### 1. Update Safe Commands

```python
# wtf/core/permissions.py

SAFE_READONLY_COMMANDS = {
    # ... existing commands ...
    
    # Web access (read-only, safe domains)
    "curl wttr.in",           # Weather
    "curl ifconfig.me",       # IP info  
    "curl icanhazip.com",     # IP info
    "curl httpie.io",         # HTTP testing
    "curl api.github.com",    # GitHub API (read-only)
}

# Also allow curl with specific safe patterns
def is_safe_curl(cmd: str) -> bool:
    """Check if curl command is safe."""
    if not cmd.startswith("curl"):
        return False
    
    # Safe domains
    safe_domains = [
        "wttr.in",           # Weather
        "ifconfig.me",       # IP
        "icanhazip.com",     # IP
        "httpie.io",         # HTTP test
        "api.github.com",    # GitHub read-only
        # Add more as needed
    ]
    
    # Check domain is in safe list
    for domain in safe_domains:
        if domain in cmd:
            # Ensure no dangerous flags
            if not any(flag in cmd for flag in ["--upload-file", "-T", "-d", "--data"]):
                return True
    
    return False
```

### 2. Update System Prompt

```python
# wtf/ai/prompts.py

SYSTEM_PROMPT_ADDITION = """
WEB ACCESS:

You can access the web for read-only information using curl:

WEATHER:
  curl wttr.in/location          # Get weather (ASCII art format)
  curl wttr.in/location?format=3 # Get weather (one-line format)
  
Examples:
  curl wttr.in/san-francisco
  curl wttr.in?format="%l:+%c+%t"  # Location, condition, temp

IP INFO:
  curl ifconfig.me               # Get user's IP
  curl icanhazip.com             # Alternative IP service

These commands are auto-allowed (no permission prompt needed).

WEB SEARCH:
If the user is using a Gemini model, you have full web search via search grounding.
Use your normal capabilities - Gemini will automatically search when needed.

For other models, you can fetch specific URLs if you know them:
  curl -s https://example.com/docs/page

Only curl is allowed, not wget or other tools.
"""
```

### 3. Update README

```markdown
## Web Access

wtf can access the web for information like weather and documentation.

### Weather

```bash
wtf is it nice outside?
wtf what's the weather in Tokyo?
```

### Documentation

```bash
wtf get me the docs on React hooks
wtf show me the Supabase quickstart
```

### With Gemini (Full Web Search)

For best web search results, use Gemini:

```bash
# Install Gemini plugin
llm install llm-gemini
llm keys set gemini

# Use with wtf
wtf --model gemini-1.5-pro "search for best React patterns 2024"

# Or set as default
wtf remember to use gemini-1.5-pro as my default model
```

Gemini models have built-in web search, so they can answer any query that needs 
current information.
```

---

## Summary

**For your examples:**

1. **"wtf is it nice outside?"**
   - ✅ Works today with `curl wttr.in` (auto-allowed)
   - ✅ Works with Gemini models (web search)

2. **"wtf can you get me the docs on connecting react to supabase"**
   - ⚠️  Partial with `curl` (needs exact URL)
   - ✅ Full support with Gemini models (searches and finds docs)

**Recommended approach:**
- Ship v0.1 with both `curl` support and Gemini docs
- Users choose: free (`curl` for known sites) or Gemini (full search)
- Add MCP web search in v0.2 for best of both worlds

**Implementation priority:**
1. ✅ Safe curl commands (easy, add to spec)
2. ✅ Document Gemini usage (zero code, just docs)
3. ⏭️  MCP web search (v0.2, when we add MCP support)

