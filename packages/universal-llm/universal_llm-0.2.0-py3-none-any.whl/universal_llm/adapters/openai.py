import json
from typing import AsyncIterator, List, Dict, Union, Any
from ..base import BaseLLMClient, LLMError
from ..settings import Settings
import httpx


class OpenAIClient(BaseLLMClient):
    def __init__(self, settings: Settings):
        self.settings = settings
        
        # Handle Google compatibility
        if settings.provider == "google":
            self.api_key = settings.api_key
            self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
        else:
            self.api_key = settings.api_key
            self.base_url = settings.base_url or "https://api.openai.com/v1"
        
        if not self.api_key:
            raise LLMError(f"{settings.provider.title()} API key is required", provider=settings.provider)
        
        # Google uses the same Bearer auth format as OpenAI
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
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
            if "rate_limit" in str(e).lower() or "429" in str(e):
                raise LLMError(f"Rate limit exceeded: {str(e)}", code="rate_limit", provider=self.settings.provider)
            elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower() or "401" in str(e):
                raise LLMError(f"Authentication error: {str(e)}", code="auth_error", provider=self.settings.provider)
            elif "invalid_request" in str(e).lower() or "400" in str(e):
                raise LLMError(f"Invalid request: {str(e)}", code="invalid_request", provider=self.settings.provider)
            else:
                raise LLMError(f"API error: {str(e)}", code="api_error", provider=self.settings.provider)
    
    async def _generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        payload = self._build_payload(messages, stream=False, **kwargs)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.settings.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _stream_response(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[Any]:
        payload = self._build_payload(messages, stream=True, **kwargs)
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
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
                            chunk_data = json.loads(data_str)
                            
                            if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                                choice = chunk_data["choices"][0]
                                delta = choice.get("delta", {})
                                
                                if "content" in delta and delta["content"]:
                                    yield delta["content"]
                                elif "tool_calls" in delta and delta["tool_calls"]:
                                    yield {"type": "tool_call", "data": chunk_data}
                                elif "function_call" in delta and delta["function_call"]:
                                    yield {"type": "function_call", "data": chunk_data}
                        except json.JSONDecodeError:
                            continue
    
    def _build_payload(self, messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> Dict[str, Any]:
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "stream": stream
        }
        
        if self.settings.temperature is not None:
            payload["temperature"] = self.settings.temperature
        
        # Add provider-specific kwargs
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]
        if "stop" in kwargs:
            payload["stop"] = kwargs["stop"]
        if "response_format" in kwargs:
            payload["response_format"] = kwargs["response_format"]
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]
        if "tool_choice" in kwargs:
            payload["tool_choice"] = kwargs["tool_choice"]
        if "function_call" in kwargs:
            payload["function_call"] = kwargs["function_call"]
        if "functions" in kwargs:
            payload["functions"] = kwargs["functions"]
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "frequency_penalty" in kwargs:
            payload["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            payload["presence_penalty"] = kwargs["presence_penalty"]
        if "logit_bias" in kwargs:
            payload["logit_bias"] = kwargs["logit_bias"]
        if "user" in kwargs:
            payload["user"] = kwargs["user"]
        
        return payload