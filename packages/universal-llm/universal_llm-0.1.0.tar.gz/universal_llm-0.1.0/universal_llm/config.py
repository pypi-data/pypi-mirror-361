from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, Dict
import json
import os
from enum import Enum


class Provider(str, Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class ProviderConfig(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


class UniversalLLMConfig(BaseModel):
    # Current active provider
    current_provider: Optional[Provider] = None
    
    # Default settings
    default_temperature: float = 0.2
    default_timeout: int = 60
    
    # Provider-specific configurations
    providers: Dict[Provider, ProviderConfig] = {
        Provider.OPENAI: ProviderConfig(model="gpt-4o-mini"),
        Provider.GOOGLE: ProviderConfig(model="gemini-2.0-flash"),
        Provider.ANTHROPIC: ProviderConfig(model="claude-3-5-sonnet-20241022"),
        Provider.OLLAMA: ProviderConfig(model="llama3.2", base_url="http://localhost:11434/v1"),
    }


def get_config_path() -> Path:
    """Get the configuration file path."""
    return Path.home() / ".config" / "universal-llm" / "config.json"


def load_config() -> UniversalLLMConfig:
    """Load configuration with automatic creation of missing files."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = json.load(f)
        return UniversalLLMConfig(**data)
    else:
        config = UniversalLLMConfig()
        save_config(config)
        return config


def save_config(config: UniversalLLMConfig):
    """Save configuration with proper file permissions."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config.model_dump(), f, indent=2)
    
    # Set secure permissions (readable only by owner)
    os.chmod(config_path, 0o600)