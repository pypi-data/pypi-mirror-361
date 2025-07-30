# Universal LLM Client

Swap LLM providers with one env var. No code changes.

```python
from universal_llm import Settings, get_client

settings = Settings(provider="anthropic", model="claude-3-haiku")
client = get_client(settings)

resp = client.chat_sync([
    {"role": "user", "content": "Explain the CAP theorem in 2 sentences."}
])
print(resp)
```

## Installation

```bash
pip install universal-llm[all]
```

Or install only what you need:
- `pip install universal-llm[openai]`
- `pip install universal-llm[anthropic]`
- `pip install universal-llm[google]`
- `pip install universal-llm[ollama]`

## Configuration

Set via environment variables:
- `LLM_PROVIDER` - openai, anthropic, google, or ollama
- `LLM_MODEL` - model name
- `LLM_API_KEY` - API key (not required for Ollama)
- `LLM_BASE_URL` - base URL (Ollama defaults to http://localhost:11434/v1)
- `LLM_TEMPERATURE` - temperature (default: 0.2)
- `LLM_TIMEOUT` - timeout in seconds (default: 60)