# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Universal LLM is a Python library that provides a unified interface for multiple LLM providers (OpenAI, Anthropic, Google, Ollama). Users can swap providers with environment variables or CLI configuration without changing code.

## Development Commands

### Installation and Dependencies
```bash
# Install with all providers
pip install -e .[all]

# Install for development
pip install -e .[dev]

# Install specific providers only
pip install -e .[openai]  # or anthropic, google, ollama
```

### Testing
```bash
# Run tests (uses pytest)
pytest

# Run async tests
pytest -v
```

### CLI Usage
```bash
# CLI entry point
universal-llm

# Test the CLI installation
python -m universal_llm.cli
```

## Architecture

### Core Components

1. **Settings (`settings.py`)** - Pydantic model for LLM configuration with environment variable support
2. **Base Client (`base.py`)** - Abstract base class `BaseLLMClient` defining the interface for all providers
3. **Registry (`registry.py`)** - Factory function `get_client()` that returns appropriate client based on provider
4. **Adapters (`adapters/`)** - Provider-specific implementations using pure HTTP requests:
   - `openai.py` - OpenAI Chat Completions API with SSE streaming
   - `anthropic.py` - Anthropic Messages API with SSE streaming  
   - `ollama.py` - Ollama local API with newline-delimited JSON streaming
   - `google` - Uses OpenAI adapter with Google's OpenAI-compatible endpoint

### Configuration System

- **CLI Config (`config.py`)** - Typer-based CLI with persistent configuration stored in `~/.config/universal-llm/config.json`
- **Settings (`settings.py`)** - Environment variable configuration with pydantic-settings
- **Provider Enum** - Centralized provider definitions: openai, anthropic, google, ollama

### Key Design Patterns

1. **Adapter Pattern** - Each provider implements `BaseLLMClient` interface
2. **Factory Pattern** - `get_client()` returns appropriate client based on provider string
3. **Unified Interface** - All providers support:
   - `chat()` - Async chat with message history
   - `chat_sync()` - Synchronous wrapper 
   - `ask()` - Simple question/answer interface
4. **Configuration Hierarchy** - CLI overrides > config file > environment variables > defaults

### CLI Architecture

Based on Typer with hierarchical commands:
- `ask` - Single question/answer
- `chat` - Interactive conversation
- `set-provider` - Configure active provider
- `set-key` - Set API keys securely
- `set-model` - Configure default models
- `show-config` - Display current configuration
- `configure` - Interactive setup wizard

Configuration stored securely in `~/.config/universal-llm/config.json` with 0o600 permissions.

### Implementation Status

✅ **All adapters implemented with pure HTTP**:
- `OpenAIClient` - Pure httpx implementation of OpenAI Chat Completions API
- `AnthropicClient` - Pure httpx implementation of Anthropic Messages API  
- `OllamaClient` - Pure httpx implementation of Ollama local API
- `Google` - Uses OpenAI adapter with Google's OpenAI-compatible endpoint

✅ **No SDK dependencies**: All adapters use standard `httpx` for HTTP requests, no provider SDKs required

✅ **Streaming fixed**: Removed incorrect `await` from async iterator, proper chunk handling for all providers

✅ **Error normalization**: All provider exceptions wrapped in `LLMError` with `code` and `provider` attributes

✅ **Provider-specific kwargs**: Each adapter accepts and passes through provider-specific parameters

✅ **Sync/async bridging**: Fixed with `asyncio.get_running_loop()` check to prevent nested event loop errors

✅ **Real smoke tests**: Full test suite in `tests/test_real_smoke.py` with actual API calls for all providers

### Testing

Run real API smoke tests (requires API keys):
```bash
python -m pytest tests/test_real_smoke.py -v -s
```

See `SMOKE_TESTS.md` for detailed testing instructions.