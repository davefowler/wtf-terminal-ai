# Feature Proposal: Provider Metadata for LLM

## Summary

Add optional provider metadata to the `llm` package, allowing plugins to expose helpful information like API key signup URLs, documentation links, and pricing pages. This would improve the user experience during setup and make it easier for users to get started with new providers.

## Motivation

Currently, when users need to set up an API key for a new provider, they have to:

1. Search for "[provider name] API key"
2. Find the right page
3. Sign up or navigate to their API settings
4. Copy the key
5. Return to terminal and paste it

**We can make this easier** by providing direct links in the CLI output.

## Proposed API

### For Plugin Developers

Add an optional `ProviderMetadata` class that plugins can return:

```python
from llm import Model, KeyModel, ProviderMetadata

class ClaudeModel(KeyModel):
    model_id = "claude-3-5-sonnet-20241022"

    @classmethod
    def get_provider_metadata(cls):
        return ProviderMetadata(
            name="Anthropic",
            api_key_url="https://console.anthropic.com/settings/keys",
            docs_url="https://docs.anthropic.com/",
            pricing_url="https://www.anthropic.com/pricing"
        )
```

### ProviderMetadata Class

```python
@dataclass
class ProviderMetadata:
    """Optional metadata about an LLM provider."""

    name: str  # Human-readable provider name
    api_key_url: Optional[str] = None  # Where to get an API key
    docs_url: Optional[str] = None  # Documentation homepage
    pricing_url: Optional[str] = None  # Pricing information
    homepage_url: Optional[str] = None  # Provider homepage
```

### CLI Integration

When running `llm keys set anthropic`, if the provider has metadata:

**Current behavior:**
```bash
$ llm keys set anthropic
Enter key: _
```

**Proposed behavior:**
```bash
$ llm keys set anthropic
Enter your Anthropic API key.
Get one at: https://console.anthropic.com/settings/keys

API key: _
```

### Python API

Expose metadata programmatically:

```python
import llm

# Get metadata for a specific model
model = llm.get_model("claude-3-5-sonnet-20241022")
if hasattr(model, 'get_provider_metadata'):
    metadata = model.get_provider_metadata()
    print(f"Get an API key at: {metadata.api_key_url}")

# List all providers with metadata
for model in llm.get_models():
    if hasattr(model, 'get_provider_metadata'):
        meta = model.get_provider_metadata()
        print(f"{meta.name}: {meta.api_key_url}")
```

### New CLI Command: `llm providers`

Show available providers and their metadata:

```bash
$ llm providers

Available LLM Providers:

Anthropic
  API Keys: https://console.anthropic.com/settings/keys
  Documentation: https://docs.anthropic.com/
  Pricing: https://www.anthropic.com/pricing

OpenAI
  API Keys: https://platform.openai.com/api-keys
  Documentation: https://platform.openai.com/docs
  Pricing: https://openai.com/pricing

Google Gemini
  API Keys: https://aistudio.google.com/app/apikey
  Documentation: https://ai.google.dev/docs
```

## Implementation Details

### 1. Add ProviderMetadata class to `llm/__init__.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProviderMetadata:
    """Metadata about an LLM provider."""
    name: str
    api_key_url: Optional[str] = None
    docs_url: Optional[str] = None
    pricing_url: Optional[str] = None
    homepage_url: Optional[str] = None
```

### 2. Update KeyModel base class

Add optional classmethod:

```python
class KeyModel(Model):
    # ... existing code ...

    @classmethod
    def get_provider_metadata(cls) -> Optional[ProviderMetadata]:
        """Override to provide provider metadata."""
        return None
```

### 3. Update `llm keys set` command

In the CLI code that handles `llm keys set`:

```python
def keys_set(key_name):
    # Find the model/provider
    provider_metadata = get_provider_metadata_for_key(key_name)

    if provider_metadata and provider_metadata.api_key_url:
        click.echo(f"Enter your {provider_metadata.name} API key.")
        click.echo(f"Get one at: {provider_metadata.api_key_url}")
        click.echo()

    key = click.prompt("API key", hide_input=True)
    # ... rest of existing logic
```

### 4. Add `llm providers` command

New CLI command to list all providers:

```python
@cli.command()
def providers():
    """List available LLM providers and their metadata."""
    providers = {}

    for model in get_models():
        if hasattr(model, 'get_provider_metadata'):
            meta = model.get_provider_metadata()
            if meta and meta.name not in providers:
                providers[meta.name] = meta

    if not providers:
        click.echo("No provider metadata available.")
        return

    click.echo("\nAvailable LLM Providers:\n")

    for name, meta in sorted(providers.items()):
        click.echo(f"{name}")
        if meta.api_key_url:
            click.echo(f"  API Keys: {meta.api_key_url}")
        if meta.docs_url:
            click.echo(f"  Documentation: {meta.docs_url}")
        if meta.pricing_url:
            click.echo(f"  Pricing: {meta.pricing_url}")
        click.echo()
```

## Example Plugin Implementation

Update existing plugins (like `llm-claude`, `llm-gemini`, etc.) to include metadata:

### llm-claude (Anthropic plugin)

```python
from llm import KeyModel, ProviderMetadata

class ClaudeModel(KeyModel):
    model_id = "claude-3-5-sonnet-20241022"

    @classmethod
    def get_provider_metadata(cls):
        return ProviderMetadata(
            name="Anthropic",
            api_key_url="https://console.anthropic.com/settings/keys",
            docs_url="https://docs.anthropic.com/",
            pricing_url="https://www.anthropic.com/pricing",
            homepage_url="https://www.anthropic.com/"
        )
```

### Built-in OpenAI models

```python
class OpenAIModel(KeyModel):
    # ... existing code ...

    @classmethod
    def get_provider_metadata(cls):
        return ProviderMetadata(
            name="OpenAI",
            api_key_url="https://platform.openai.com/api-keys",
            docs_url="https://platform.openai.com/docs",
            pricing_url="https://openai.com/pricing",
            homepage_url="https://openai.com/"
        )
```

## Benefits

1. **Better UX**: Users can get API keys without leaving the terminal
2. **Discoverability**: `llm providers` shows what's available
3. **Programmatic access**: Other tools (like `wtf`) can use this metadata
4. **Optional**: Plugins don't have to provide metadata - it's opt-in
5. **Extensible**: Easy to add more metadata fields in the future
6. **Backwards compatible**: Doesn't break existing plugins

## Use Cases

### For end users:
- Quick access to API key signup pages
- Discover what providers are available
- Find documentation when needed

### For tool developers:
- Build better onboarding flows (like `wtf`)
- Show provider information in TUIs
- Auto-generate setup documentation

### For plugin developers:
- Promote their provider/service
- Reduce support questions about "where do I get an API key?"
- Provide helpful resources to users

## Migration Path

1. **Phase 1**: Add `ProviderMetadata` class and base implementation
2. **Phase 2**: Update built-in OpenAI models to use it
3. **Phase 3**: Update official plugins (claude, gemini, etc.)
4. **Phase 4**: Document for third-party plugin developers

All phases are backwards compatible - existing plugins continue to work.

## Alternative Approaches Considered

### 1. Hardcode URLs in llm core
**Rejected**: Would require llm updates for every new provider

### 2. External registry/config file
**Rejected**: Adds complexity, hard to keep in sync with plugins

### 3. Plugin returns dict instead of class
**Rejected**: Less type-safe, harder to extend

## Open Questions

1. Should we cache provider metadata or call `get_provider_metadata()` each time?
2. Should `llm providers` also show which models are available from each provider?
3. Should we add a `support_url` field for provider support/help?
4. Should metadata be per-provider or per-model? (Current proposal: per-provider)

## Prior Art

- **Homebrew**: Shows homepage URLs when installing packages
- **npm**: Shows repository and homepage URLs in package info
- **pip**: Shows project URLs in package metadata
- **VS Code extensions**: Metadata includes documentation and support URLs

## Conclusion

This feature would make `llm` more user-friendly and easier to integrate into other tools. It's a small addition with minimal maintenance burden but significant UX benefits.

The implementation is straightforward, backwards compatible, and follows patterns already established in the plugin system.

---

## For Discussion

Would love feedback on:
- The API design (especially `ProviderMetadata` fields)
- CLI output format for `llm providers`
- Whether to include this in core or as a separate package
- Additional metadata fields that would be useful

Happy to implement this if there's interest!
