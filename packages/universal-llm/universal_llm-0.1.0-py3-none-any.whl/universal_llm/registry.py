from .base import BaseLLMClient, LLMError
from .settings import Settings


def get_client(settings: Settings) -> BaseLLMClient:
    if settings.provider in ["openai", "google"]:
        from .adapters.openai import OpenAIClient
        return OpenAIClient(settings)
    elif settings.provider == "anthropic":
        from .adapters.anthropic import AnthropicClient
        return AnthropicClient(settings)
    elif settings.provider == "ollama":
        from .adapters.ollama import OllamaClient
        return OllamaClient(settings)
    else:
        raise LLMError(f"Unknown provider: {settings.provider}")