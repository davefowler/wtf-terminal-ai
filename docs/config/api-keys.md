# API Key Management in wtf

## Overview

wtf now has a unified `wtf_config` tool for managing all API keys and settings. Users can configure keys conversationally.

## Usage

### Save API Keys

Users can save API keys naturally:

```bash
# Save Brave Search key
wtf here is my brave search api key sk-1234567890

# Save other keys
wtf save my anthropic key sk-ant-xxxxx
wtf here is my openai api key sk-xxxxx
```

The AI will use the `wtf_config` tool to save these to `~/.config/wtf/config.json` under `api_keys` section.

### Check API Keys

```bash
wtf do I have a brave search key configured?
wtf show me my api keys
```

## Config Storage

API keys are stored in `~/.config/wtf/config.json`:

```json
{
  "version": "0.1.0",
  "api": {
    "provider": "anthropic",
    "model": "claude-3.5-sonnet"
  },
  "api_keys": {
    "brave_search": "your-key-here",
    "custom_service": "another-key"
  }
}
```

## Tool Implementation

The `wtf_config` tool handles:

- **set_api_key**: Save API key to config
- **get_api_key**: Retrieve stored API key
- **set_setting**: Update general settings (behavior, shell, etc.)
- **get_setting**: Read config values

## Web Search Integration

All three web search providers (Serper, Bing, Brave) are now fully implemented.

Each search tool checks for API key in two places:
1. Config file: `config.api_keys.serper`, `config.api_keys.bing_search`, `config.api_keys.brave_search`
2. Environment variables: `SERPER_API_KEY`, `BING_SEARCH_API_KEY`, `BRAVE_SEARCH_API_KEY`

### Setting Search API Keys

```bash
# Serper (Recommended - Google results)
wtf here is my serper api key sk-YOUR_KEY

# Brave Search (Privacy-focused)
wtf here is my brave search api key YOUR_KEY

# Bing Search (Microsoft Azure)
wtf here is my bing search api key YOUR_KEY
```

If no key found, tools return helpful errors with links to get free API keys.

### Search Provider Priority

wtf automatically uses whichever search API you have configured:
1. **Serper** (preferred) - Best quality, Google results
2. **Brave** - Privacy-focused
3. **Bing** - Microsoft Azure
4. **DuckDuckGo** - Always available, limited to encyclopedic facts

See [Web Search](web-search.md) for more details.

## Security Note

API keys are stored in plain text in `~/.config/wtf/config.json`.

File permissions are managed by the OS. On Unix systems, config directory should be readable only by user (0700).

For sensitive production environments, use environment variables instead.
