# Using Universal LLM in Your Project

## Installation in a New Project

```bash
mkdir my-llm-project
cd my-llm-project
pip install universal-llm
```

## Simple Example

Create `main.py`:

```python
from universal_llm import Settings, get_client
import os

# Method 1: Use environment variables
os.environ['LLM_PROVIDER'] = 'openai'
os.environ['LLM_API_KEY'] = 'your-openai-api-key'
os.environ['LLM_MODEL'] = 'gpt-4o-mini'

settings = Settings()  # Loads from environment
client = get_client(settings)

response = client.ask("What is the meaning of life?")
print(response)
```

## Or Configure Programmatically

```python
from universal_llm import Settings, get_client

# Method 2: Direct configuration
settings = Settings(
    provider="anthropic",
    model="claude-3-5-haiku",
    api_key="your-anthropic-api-key"
)

client = get_client(settings)
response = client.ask("Explain quantum computing in simple terms")
print(response)
```

## Switching Providers

```python
from universal_llm import Settings, get_client

# Easy to switch between providers
providers = [
    Settings(provider="openai", model="gpt-4o-mini", api_key="openai-key"),
    Settings(provider="anthropic", model="claude-3-5-haiku", api_key="anthropic-key"),
    Settings(provider="google", model="gemini-2.0-flash", api_key="google-key"),
    Settings(provider="ollama", model="llama3.2")  # No API key needed
]

question = "What is machine learning?"

for setting in providers:
    try:
        client = get_client(setting)
        response = client.ask(question)
        print(f"\n{setting.provider.upper()}: {response[:100]}...")
    except Exception as e:
        print(f"{setting.provider} failed: {e}")
```

## Async Example

```python
import asyncio
from universal_llm import Settings, get_client

async def async_example():
    settings = Settings(provider="anthropic", api_key="your-key")
    client = get_client(settings)
    
    # Async chat
    response = await client.chat([
        {"role": "user", "content": "Tell me a joke"}
    ])
    print(response)
    
    # Async streaming
    print("\nStreaming response:")
    async for chunk in await client.chat([
        {"role": "user", "content": "Count from 1 to 5"}
    ], stream=True):
        if isinstance(chunk, str):
            print(chunk, end="")
    print()

asyncio.run(async_example())
```

## Production Example with Error Handling

```python
from universal_llm import Settings, get_client, LLMError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_llm_call(prompt: str, fallback_providers=None):
    """Call LLM with fallback providers if primary fails"""
    
    if fallback_providers is None:
        fallback_providers = [
            Settings(provider="openai", model="gpt-4o-mini"),
            Settings(provider="anthropic", model="claude-3-5-haiku"),
            Settings(provider="ollama", model="llama3.2")
        ]
    
    for setting in fallback_providers:
        try:
            client = get_client(setting)
            response = client.ask(prompt)
            logger.info(f"Success with {setting.provider}")
            return response
            
        except LLMError as e:
            if e.code == "auth_error":
                logger.warning(f"{setting.provider}: Invalid API key")
            elif e.code == "rate_limit":
                logger.warning(f"{setting.provider}: Rate limited")
            else:
                logger.warning(f"{setting.provider}: {e}")
            continue
        except Exception as e:
            logger.error(f"{setting.provider}: Unexpected error: {e}")
            continue
    
    raise Exception("All LLM providers failed")

# Usage
try:
    result = safe_llm_call("What is Python programming?")
    print(result)
except Exception as e:
    print(f"All providers failed: {e}")
```

## Django/Flask Integration

```python
# django views.py or flask app.py
from universal_llm import Settings, get_client
from django.conf import settings as django_settings

def get_llm_client():
    """Get configured LLM client from Django settings"""
    return get_client(Settings(
        provider=django_settings.LLM_PROVIDER,
        model=django_settings.LLM_MODEL,
        api_key=django_settings.LLM_API_KEY,
    ))

def chat_view(request):
    client = get_llm_client()
    user_message = request.POST.get('message')
    
    response = client.ask(user_message)
    return JsonResponse({'response': response})
```

## FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from universal_llm import Settings, get_client, LLMError
from pydantic import BaseModel

app = FastAPI()

# Initialize client once
client = get_client(Settings())  # Uses environment variables

class ChatRequest(BaseModel):
    message: str
    provider: str = "openai"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Override provider if specified
        if request.provider != "openai":
            temp_client = get_client(Settings(provider=request.provider))
        else:
            temp_client = client
            
        response = await temp_client.chat([
            {"role": "user", "content": request.message}
        ])
        return {"response": response}
        
    except LLMError as e:
        raise HTTPException(status_code=400, detail=f"LLM Error: {e}")
```

## Environment Setup (.env file)

Create `.env` file in your project:

```bash
# .env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your-openai-api-key-here
LLM_TEMPERATURE=0.7
LLM_TIMEOUT=30
```

Then in your code:
```python
from universal_llm import Settings, get_client

# Automatically loads from .env file
settings = Settings()
client = get_client(settings)
```

## Testing with Mock

```python
# test_my_app.py
import pytest
from unittest.mock import patch, MagicMock
from universal_llm import get_client, Settings

def test_my_llm_function():
    with patch('universal_llm.get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_client.ask.return_value = "Mocked response"
        mock_get_client.return_value = mock_client
        
        # Your function that uses universal_llm
        result = my_function_that_uses_llm("test input")
        
        assert result == "Mocked response"
        mock_client.ask.assert_called_once_with("test input")
```

That's it! Universal LLM makes it easy to add LLM capabilities to any Python project with minimal setup and maximum flexibility.