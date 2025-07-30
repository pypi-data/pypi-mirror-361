# Smoke Tests for Universal LLM

This guide explains how to run real API smoke tests for all four supported providers.

## Setup

1. Install the package with dependencies:
```bash
pip install -e .[all,dev]
```

2. Set environment variables for the providers you want to test:

### OpenAI
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Anthropic
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Google Gemini
```bash
export GOOGLE_API_KEY="your-google-api-key"
```

### Ollama (local)
```bash
# First start Ollama server
ollama serve

# Pull a small model for testing
ollama pull llama3.2:1b

# Enable Ollama tests
export TEST_OLLAMA=1
```

## Running Tests

### Run all available tests
```bash
python -m pytest tests/test_real_smoke.py -v -s
```

### Run specific provider tests
```bash
# Only OpenAI tests
python -m pytest tests/test_real_smoke.py -k "openai" -v -s

# Only Anthropic tests
python -m pytest tests/test_real_smoke.py -k "anthropic" -v -s

# Only Google tests
python -m pytest tests/test_real_smoke.py -k "google" -v -s

# Only Ollama tests
python -m pytest tests/test_real_smoke.py -k "ollama" -v -s
```

### Run the test file directly
```bash
python tests/test_real_smoke.py
```

## What the Tests Cover

1. **Basic functionality**: Simple ask/chat calls for each provider
2. **Streaming**: Real streaming responses from APIs
3. **Provider-specific kwargs**: Testing provider-specific parameters
4. **Error handling**: Proper error handling for missing keys and invalid providers
5. **Async/sync compatibility**: Both async and sync API calls

## Expected Output

Tests will show which providers are available and skip those without API keys:

```
✅ OPENAI_API_KEY found - will test OpenAI
❌ ANTHROPIC_API_KEY not found - skipping Anthropic tests
❌ GOOGLE_API_KEY not found - skipping Google tests
❌ TEST_OLLAMA not found - skipping Ollama tests
```

Each successful test will print the actual API response to verify real communication.

## Troubleshooting

### OpenAI Tests Fail
- Check your API key is valid
- Ensure you have credits in your OpenAI account
- Try with a different model (e.g., "gpt-3.5-turbo")

### Anthropic Tests Fail
- Verify your API key format (should start with "sk-ant-")
- Check you have access to the Claude model being tested
- Try with "claude-3-haiku-20240307" if the default fails

### Google Tests Fail
- Ensure your API key is for Gemini API (not Google Cloud)
- Check the model name is correct
- Try with "gemini-1.5-flash" if the default fails

### Ollama Tests Fail
- Make sure Ollama server is running: `ollama serve`
- Check the model is pulled: `ollama list`
- Try a different model: change "llama3.2:1b" to another available model