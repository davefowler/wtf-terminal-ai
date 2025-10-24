# Web Search Options for wtf

Currently wtf only has `web_instant_answers` which uses DuckDuckGo's Instant Answer API - very limited, only encyclopedic facts.

## Options for Real Web Search

### 1. **Brave Search API** (Recommended)
**Pros:**
- Free tier: 2,000 queries/month
- No credit card required for free tier
- Good quality results
- Simple REST API
- Privacy-focused

**Cons:**
- Requires API key signup

**Implementation:**
```python
def brave_search(query: str, api_key: str) -> Dict[str, Any]:
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"X-Subscription-Token": api_key}
    response = requests.get(url, headers=headers, params={"q": query})
    return response.json()
```

**Setup for users:**
```bash
# Get API key from https://brave.com/search/api/
export BRAVE_SEARCH_API_KEY="your-key"
```

### 2. **Serper.dev**
**Pros:**
- Free tier: 2,500 searches/month
- Google search results
- Very easy API
- No credit card for free tier

**Cons:**
- Requires API key signup

**Implementation:**
```python
def serper_search(query: str, api_key: str) -> Dict[str, Any]:
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    data = {"q": query}
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

**Setup for users:**
```bash
# Get API key from https://serper.dev
export SERPER_API_KEY="your-key"
```

### 3. **Tavily Search API**
**Pros:**
- Free tier: 1,000 searches/month
- Designed for AI/LLM use cases
- Returns cleaned, structured data
- Good for research queries

**Cons:**
- Requires credit card even for free tier
- Smaller free tier

**Implementation:**
```python
def tavily_search(query: str, api_key: str) -> Dict[str, Any]:
    url = "https://api.tavily.com/search"
    data = {"api_key": api_key, "query": query}
    response = requests.post(url, json=data)
    return response.json()
```

### 4. **MCP Server (Model Context Protocol)**
**Pros:**
- User can choose their own search provider
- Flexible, extensible
- Can add other MCP tools too

**Cons:**
- More complex setup
- Requires MCP server running
- Users need to understand MCP

**Implementation:**
Would need to add MCP client support to wtf, then users can configure any MCP server including:
- @modelcontextprotocol/server-brave-search
- @modelcontextprotocol/server-fetch
- Custom MCP servers

### 5. **SearXNG (Self-hosted)**
**Pros:**
- No API key needed
- Privacy-focused
- Meta-search (queries multiple engines)
- Free

**Cons:**
- User must self-host or use public instance
- Public instances can be unreliable
- Requires more setup

**Implementation:**
```python
def searxng_search(query: str, instance_url: str = "https://searx.be") -> Dict[str, Any]:
    url = f"{instance_url}/search"
    params = {"q": query, "format": "json"}
    response = requests.get(url, params=params)
    return response.json()
```

## Recommendation

**Start with Brave Search API:**
1. Best balance of ease-of-use and quality
2. Generous free tier
3. No credit card required
4. Simple implementation

**Implementation Plan:**
1. Add `brave_search` tool that checks for `BRAVE_SEARCH_API_KEY` env var
2. Only register tool if API key is present
3. Update docs with signup link
4. Keep `web_instant_answers` as fallback for users without key

This way:
- Users without API key: get limited instant answers (current behavior)
- Users with API key: get full web search (5-10 min setup)
- Clean, optional upgrade path
