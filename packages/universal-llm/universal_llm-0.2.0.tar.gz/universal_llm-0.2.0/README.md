# Universal LLM Client

Swap LLM providers with one command or environment variable. No code changes, no SDK dependencies.

**Pure HTTP implementation** - works with OpenAI, Anthropic, Google Gemini, and Ollama using standard HTTP requests.

```python
from universal_llm import Settings, get_client, Models

# Use any provider with model constants
settings = Settings(
    provider="anthropic", 
    model=Models.anthropic.CLAUDE_3_5_HAIKU_20241022
)
client = get_client(settings)

response = client.ask("Explain the CAP theorem in 2 sentences.")
print(response)
```

## Installation

```bash
pip install universal-llm
```

That's it! All providers work out of the box - no extra dependencies needed.

## Quick Start

### 1. Install from PyPI
```bash
pip install universal-llm
```

### 2. Set your API key
```bash
# For OpenAI
export LLM_API_KEY="your-openai-api-key"
export LLM_PROVIDER="openai"

# For Anthropic
export LLM_API_KEY="your-anthropic-api-key" 
export LLM_PROVIDER="anthropic"

# For Google Gemini
export LLM_API_KEY="your-google-api-key"
export LLM_PROVIDER="google"

# For Ollama (local, no API key needed)
export LLM_PROVIDER="ollama"
```

### 3. Use in your code
```python
from universal_llm import Settings, get_client

# Settings automatically loads from environment variables
settings = Settings()
client = get_client(settings)

# Simple question
response = client.ask("What is the capital of France?")
print(response)

# Full conversation
messages = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "How are you?"}
]
response = client.chat_sync(messages)
print(response)
```

## Supported Providers

| Provider | Models | Setup |
|----------|---------|-------|
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-3.5-turbo | Get API key from [OpenAI](https://platform.openai.com/api-keys) |
| **Anthropic** | claude-3-5-sonnet, claude-3-5-haiku | Get API key from [Anthropic](https://console.anthropic.com/) |
| **Google Gemini** | gemini-2.0-flash, gemini-1.5-pro | Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey) |
| **Ollama** | llama3.2, qwen2.5, etc. | Install [Ollama](https://ollama.com/) locally |

## Configuration Options

### Environment Variables
- `LLM_PROVIDER` - Provider name (openai, anthropic, google, ollama)
- `LLM_MODEL` - Model name
- `LLM_API_KEY` - API key (not needed for Ollama)
- `LLM_BASE_URL` - Custom base URL
- `LLM_TEMPERATURE` - Temperature (default: 0.2)
- `LLM_TIMEOUT` - Timeout in seconds (default: 60)

### Programmatic Configuration
```python
from universal_llm import Settings, get_client, Models

# Override any setting with model constants
settings = Settings(
    provider="openai",
    model=Models.openai.GPT_4O_MINI,
    api_key="your-key-here",
    temperature=0.7
)
client = get_client(settings)
```

## Model Constants

Universal LLM provides constants for all supported models, updated regularly:

```python
from universal_llm import Models, OpenAIModels, AnthropicModels

# Access models by provider
print(f"Latest OpenAI model: {OpenAIModels.GPT_4O}")
print(f"Fast Anthropic model: {AnthropicModels.CLAUDE_3_5_HAIKU_20241022}")

# Get recommended models
fast_model = Models.get_recommended_model("openai", "fast")      # gpt-4o-mini
balanced_model = Models.get_recommended_model("anthropic", "balanced")  # claude-3-5-sonnet

# List all models for a provider
all_openai = Models.get_all_models("openai")
print(f"OpenAI has {len(all_openai)} models available")

# Validate model names
is_valid = Models.is_valid_model("google", "gemini-2.0-flash")  # True
```

### Available Model Categories

**OpenAI**: GPT-4.1, GPT-4o, O3/O4 reasoning models, GPT-3.5 Turbo  
**Anthropic**: Claude 4 (Opus/Sonnet), Claude 3.7 Sonnet, Claude 3.5 Sonnet/Haiku  
**Google**: Gemini 2.5 Pro/Flash, Gemini 2.0 Flash, Gemini 1.5 models, embeddings  
**Ollama**: Llama3, Mistral, LLaVA (multimodal), SmolLM2, and more  

Use `universal-llm list-models` to see all current models. Constants are updated with each release.

## CLI Usage

Universal LLM includes a command-line interface:

```bash
# Interactive setup
universal-llm configure

# Quick question
universal-llm ask "What is Python?"

# Interactive chat
universal-llm chat

# Set provider
universal-llm set-provider openai
universal-llm set-key  # Will prompt for API key

# Show current config
universal-llm show-config

# List available models
universal-llm list-models                    # All providers
universal-llm list-models --provider openai  # Specific provider
```

## Advanced Usage

### Streaming Responses
```python
import asyncio
from universal_llm import Settings, get_client

async def stream_example():
    settings = Settings(provider="openai")
    client = get_client(settings)
    
    async for chunk in await client.chat([
        {"role": "user", "content": "Count from 1 to 10"}
    ], stream=True):
        if isinstance(chunk, str):
            print(chunk, end="")
    print()

asyncio.run(stream_example())
```

### Provider-Specific Options
```python
# OpenAI-specific options
response = client.chat_sync(messages, 
    max_tokens=100,
    response_format={"type": "json_object"},
    tools=[...])

# Anthropic-specific options  
response = await client.chat(messages,
    max_tokens=100,
    stop_sequences=["END"],
    system="You are a helpful assistant")

# Ollama-specific options
response = client.chat_sync(messages,
    options={"temperature": 0.8, "num_ctx": 4096})
```

### Error Handling
```python
from universal_llm import Settings, get_client, LLMError

try:
    client = get_client(Settings(provider="openai", api_key="invalid"))
    response = client.ask("Hello")
except LLMError as e:
    print(f"Error: {e}")
    print(f"Error code: {e.code}")
    print(f"Provider: {e.provider}")
```

## Why Universal LLM?

- **No SDK dependencies** - Pure HTTP implementation, no vendor lock-in
- **Consistent interface** - Same code works with any provider  
- **Provider flexibility** - Switch providers with one environment variable
- **Production ready** - Proper error handling, streaming, timeouts
- **Local development** - Works with Ollama for offline development
- **Simple setup** - Single pip install, no complex configuration

## Contributing

See [CLAUDE.md](CLAUDE.md) for development setup and architecture details.