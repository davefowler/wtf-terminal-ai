# Simple Feature Request: Add api_key_url to KeyModel

## Summary

Add a single optional field `api_key_url` to the `KeyModel` class. When set, display it during `llm keys set` to help users find where to get their API key.

## Current KeyModel

```python
class MyModel(llm.KeyModel):
    needs_key = "myservice"
    key_env_var = "MYSERVICE_API_KEY"
```

## Proposed Addition

```python
class MyModel(llm.KeyModel):
    needs_key = "myservice"
    key_env_var = "MYSERVICE_API_KEY"
    api_key_url = "https://myservice.com/api-keys"  # NEW - optional field
```

## Updated CLI Behavior

**Current:**
```bash
$ llm keys set anthropic
Enter key: _
```

**Proposed:**
```bash
$ llm keys set anthropic
Enter your Anthropic API key.
Get one at: https://console.anthropic.com/settings/keys

API key: _
```

## Implementation

### 1. Add field to KeyModel class (llm/models.py or llm/__init__.py)

```python
class KeyModel(Model):
    needs_key: str
    key_env_var: Optional[str] = None
    api_key_url: Optional[str] = None  # NEW
```

### 2. Update `llm keys set` command (llm/cli.py)

Find where keys are set, add 3-4 lines:

```python
def keys_set(key_name):
    # ... existing code to find model ...

    # NEW: Show API key URL if available
    if hasattr(model, 'api_key_url') and model.api_key_url:
        provider_name = getattr(model, 'needs_key', key_name).title()
        click.echo(f"Enter your {provider_name} API key.")
        click.echo(f"Get one at: {model.api_key_url}")
        click.echo()

    # ... rest of existing key prompt code ...
```

### 3. Update built-in OpenAI models (llm/default_plugins/openai_models.py)

```python
class OpenAIChat(llm.KeyModel):
    needs_key = "openai"
    key_env_var = "OPENAI_API_KEY"
    api_key_url = "https://platform.openai.com/api-keys"  # NEW
```

### 4. Plugin developers can add it (e.g., llm-claude)

```python
class Claude(llm.KeyModel):
    model_id = "claude-3-5-sonnet"
    needs_key = "anthropic"
    key_env_var = "ANTHROPIC_API_KEY"
    api_key_url = "https://console.anthropic.com/settings/keys"  # NEW
```

## That's It!

- One new optional field
- 3-4 lines of code in the CLI
- Backwards compatible (plugins without it still work)
- No new commands, no new objects, no complexity

## Example URLs

For reference, here are the URLs for major providers:

- Anthropic: https://console.anthropic.com/settings/keys
- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://aistudio.google.com/app/apikey
