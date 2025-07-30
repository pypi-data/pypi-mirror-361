from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        populate_by_name=True
    )
    
    provider: str = Field(default="openai", alias="LLM_PROVIDER")
    model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    api_key: Optional[str] = Field(default=None, alias="LLM_API_KEY")
    base_url: Optional[str] = Field(default=None, alias="LLM_BASE_URL")
    temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")
    timeout: int = Field(default=60, alias="LLM_TIMEOUT")