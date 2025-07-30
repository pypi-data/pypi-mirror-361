import json
from typing import AsyncIterator, List, Dict, Union, Any
from ..base import BaseLLMClient, LLMError
from ..settings import Settings
import httpx


class AnthropicClient(BaseLLMClient):
    def __init__(self, settings: Settings):
        self.settings = settings
        if not settings.api_key:
            raise LLMError("Anthropic API key is required", provider="anthropic")
        
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": settings.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Union[str, AsyncIterator[Any]]:
        try:
            if stream:
                return self._stream_response(messages, **kwargs)
            else:
                return await self._generate_response(messages, **kwargs)
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise LLMError(f"Rate limit exceeded: {str(e)}", code="rate_limit", provider="anthropic")
            elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                raise LLMError(f"Authentication error: {str(e)}", code="auth_error", provider="anthropic")
            else:
                raise LLMError(f"API error: {str(e)}", code="api_error", provider="anthropic")
    
    async def _generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        payload = self._build_payload(messages, stream=False, **kwargs)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=self.settings.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data["content"][0]["text"]
    
    async def _stream_response(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[Any]:
        payload = self._build_payload(messages, stream=True, **kwargs)
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=self.settings.timeout
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            event_data = json.loads(data_str)
                            event_type = event_data.get("type")
                            
                            if event_type == "content_block_delta":
                                delta = event_data.get("delta", {})
                                if "text" in delta:
                                    yield delta["text"]
                            elif event_type in ["tool_use", "thinking_delta"]:
                                yield event_data
                        except json.JSONDecodeError:
                            continue
    
    def _build_payload(self, messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> Dict[str, Any]:
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "stream": stream
        }
        
        if self.settings.temperature is not None:
            payload["temperature"] = self.settings.temperature
        
        if "stop_sequences" in kwargs:
            payload["stop_sequences"] = kwargs["stop_sequences"]
        
        if "system" in kwargs:
            payload["system"] = kwargs["system"]
        
        return payload