"""
Model constants for all supported LLM providers.

Use these exact strings with client.chat.completions.create(model=...)
Last updated: 2025-07-14
"""

from typing import Dict, List


class OpenAIModels:
    """OpenAI model constants"""
    
    # GPT-4.1 models (latest)
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1_NANO = "gpt-4.1-nano"
    
    # GPT-4o models
    GPT_4O = "gpt-4o"  # alias: chatgpt-4o-latest
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O_NANO = "gpt-4o-nano"
    
    # O-series reasoning models
    O3 = "o3"  # flagship reasoning model
    O4_MINI = "o4-mini"
    
    # GPT-3.5 models
    GPT_3_5_TURBO = "gpt-3.5-turbo"  # current snapshot: gpt-3.5-turbo-0125
    
    ALL = [
        GPT_4_1, GPT_4_1_MINI, GPT_4_1_NANO,
        GPT_4O, GPT_4O_MINI, GPT_4O_NANO,
        O3, O4_MINI,
        GPT_3_5_TURBO
    ]


class AnthropicModels:
    """Anthropic model constants"""
    
    # Claude 4 models (latest)
    CLAUDE_OPUS_4_20250514 = "claude-opus-4-20250514"
    CLAUDE_SONNET_4_20250514 = "claude-sonnet-4-20250514"
    
    # Claude 3.7 models
    CLAUDE_3_7_SONNET_20250219 = "claude-3-7-sonnet-20250219"  # alias: claude-3-7-sonnet-latest
    
    # Claude 3.5 models
    CLAUDE_3_5_SONNET_20241022 = "claude-3-5-sonnet-20241022"  # alias: claude-3-5-sonnet-latest
    CLAUDE_3_5_SONNET_20240620 = "claude-3-5-sonnet-20240620"
    CLAUDE_3_5_HAIKU_20241022 = "claude-3-5-haiku-20241022"    # alias: claude-3-5-haiku-latest
    
    # Claude 3 models
    CLAUDE_3_HAIKU_20240307 = "claude-3-haiku-20240307"
    CLAUDE_3_OPUS_20240229 = "claude-3-opus-20240229"
    
    ALL = [
        CLAUDE_OPUS_4_20250514, CLAUDE_SONNET_4_20250514,
        CLAUDE_3_7_SONNET_20250219,
        CLAUDE_3_5_SONNET_20241022, CLAUDE_3_5_SONNET_20240620, CLAUDE_3_5_HAIKU_20241022,
        CLAUDE_3_HAIKU_20240307, CLAUDE_3_OPUS_20240229
    ]


class GoogleModels:
    """Google Gemini model constants"""
    
    # Gemini 2.5 models (latest)
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_FLASH_LITE_PREVIEW_06_17 = "gemini-2.5-flash-lite-preview-06-17"
    GEMINI_2_5_FLASH_PREVIEW_NATIVE_AUDIO_DIALOG = "gemini-2.5-flash-preview-native-audio-dialog"
    GEMINI_2_5_FLASH_EXP_NATIVE_AUDIO_THINKING_DIALOG = "gemini-2.5-flash-exp-native-audio-thinking-dialog"
    GEMINI_2_5_FLASH_PREVIEW_TTS = "gemini-2.5-flash-preview-tts"
    GEMINI_2_5_PRO_PREVIEW_TTS = "gemini-2.5-pro-preview-tts"
    
    # Gemini 2.0 models
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_PREVIEW_IMAGE_GENERATION = "gemini-2.0-flash-preview-image-generation"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    
    # Gemini 1.5 models
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_FLASH_8B = "gemini-1.5-flash-8b"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    
    # Live/streaming models
    GEMINI_LIVE_2_5_FLASH_PREVIEW = "gemini-live-2.5-flash-preview"
    GEMINI_2_0_FLASH_LIVE_001 = "gemini-2.0-flash-live-001"
    
    # Embedding models
    GEMINI_EMBEDDING_EXP = "gemini-embedding-exp"
    TEXT_EMBEDDING_004 = "models/text-embedding-004"
    
    ALL = [
        GEMINI_2_5_PRO, GEMINI_2_5_FLASH, GEMINI_2_5_FLASH_LITE_PREVIEW_06_17,
        GEMINI_2_5_FLASH_PREVIEW_NATIVE_AUDIO_DIALOG, GEMINI_2_5_FLASH_EXP_NATIVE_AUDIO_THINKING_DIALOG,
        GEMINI_2_5_FLASH_PREVIEW_TTS, GEMINI_2_5_PRO_PREVIEW_TTS,
        GEMINI_2_0_FLASH, GEMINI_2_0_FLASH_PREVIEW_IMAGE_GENERATION, GEMINI_2_0_FLASH_LITE,
        GEMINI_1_5_FLASH, GEMINI_1_5_FLASH_8B, GEMINI_1_5_PRO,
        GEMINI_LIVE_2_5_FLASH_PREVIEW, GEMINI_2_0_FLASH_LIVE_001,
        GEMINI_EMBEDDING_EXP, TEXT_EMBEDDING_004
    ]


class OllamaModels:
    """Common Ollama model constants (from popular models)"""
    
    # Meta Llama models
    LLAMA3 = "llama3"  # 8B / 70B
    
    # Mistral models
    MISTRAL = "mistral"  # Mistral-7B-Instruct
    
    # Multimodal models
    LLAVA_LLAMA3 = "llava-llama3"
    
    # Small efficient models
    SMOLLM2 = "smollm2"  # 135M - 1.7B
    
    ALL = [LLAMA3, MISTRAL, LLAVA_LLAMA3, SMOLLM2]


class Models:
    """Unified model access across all providers"""
    
    openai = OpenAIModels
    anthropic = AnthropicModels
    google = GoogleModels
    ollama = OllamaModels
    
    @classmethod
    def get_all_models(cls, provider: str) -> List[str]:
        """Get all available models for a provider"""
        if provider == "openai":
            return OpenAIModels.ALL
        elif provider == "anthropic":
            return AnthropicModels.ALL
        elif provider == "google":
            return GoogleModels.ALL
        elif provider == "ollama":
            return OllamaModels.ALL
        return []
    
    @classmethod
    def list_all_models(cls) -> Dict[str, List[str]]:
        """List all models for all providers"""
        return {
            "openai": OpenAIModels.ALL,
            "anthropic": AnthropicModels.ALL,
            "google": GoogleModels.ALL,
            "ollama": OllamaModels.ALL
        }


# Convenience exports
__all__ = [
    "Models",
    "OpenAIModels", 
    "AnthropicModels",
    "GoogleModels", 
    "OllamaModels",
    "ModelInfo"
]