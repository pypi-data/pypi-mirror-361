import json
from typing import AsyncIterator, List, Dict, Union, Any
from ..base import BaseLLMClient, LLMError
from ..settings import Settings
import httpx


class OllamaClient(BaseLLMClient):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.base_url or "http://localhost:11434"
        if not self.base_url.endswith("/api"):
            self.base_url = f"{self.base_url}/api"
    
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
            if "connection" in str(e).lower():
                raise LLMError(f"Connection error: {str(e)}. Is Ollama running?", code="connection_error", provider="ollama")
            elif "model" in str(e).lower() and "not found" in str(e).lower():
                raise LLMError(f"Model not found: {str(e)}", code="model_not_found", provider="ollama")
            else:
                raise LLMError(f"API error: {str(e)}", code="api_error", provider="ollama")
    
    async def _generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        payload = self._build_payload(messages, stream=False, **kwargs)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.settings.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data["message"]["content"]
    
    async def _stream_response(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[Any]:
        payload = self._build_payload(messages, stream=True, **kwargs)
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.settings.timeout
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
                            
                            if chunk_data.get("done"):
                                break
                            
                            message = chunk_data.get("message", {})
                            content = message.get("content")
                            
                            if content:
                                yield content
                            
                            if "tool_calls" in message and message["tool_calls"]:
                                yield chunk_data
                                
                        except json.JSONDecodeError:
                            continue
    
    def _build_payload(self, messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> Dict[str, Any]:
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "stream": stream
        }
        
        if self.settings.temperature is not None:
            payload["options"] = payload.get("options", {})
            payload["options"]["temperature"] = self.settings.temperature
        
        if "options" in kwargs:
            payload["options"] = {**payload.get("options", {}), **kwargs["options"]}
        
        if "format" in kwargs:
            payload["format"] = kwargs["format"]
        
        return payload