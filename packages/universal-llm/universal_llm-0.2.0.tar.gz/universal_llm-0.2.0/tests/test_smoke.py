import pytest
import sys
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from universal_llm import Settings, get_client
from universal_llm.base import LLMError


class TestSmokeTests:
    """Basic smoke tests to verify all providers can be imported and initialized"""
    
    def test_package_imports(self):
        """Test that the main package imports work"""
        from universal_llm import Settings, get_client
        assert Settings is not None
        assert get_client is not None
    
    def test_openai_client_initialization(self):
        """Test OpenAI client can be initialized"""
        settings = Settings(
            provider="openai",
            model="gpt-4o-mini",
            api_key="test-key"
        )
        
        # Mock the OpenAI module import
        mock_openai = MagicMock()
        with patch.dict('sys.modules', {'openai': mock_openai}):
            with patch('universal_llm.adapters.openai.OpenAI', mock_openai.OpenAI):
                client = get_client(settings)
                assert client is not None
    
    def test_google_client_initialization(self):
        """Test Google client can be initialized (uses OpenAI adapter)"""
        settings = Settings(
            provider="google",
            model="gemini-2.0-flash",
            api_key="test-key"
        )
        
        # Mock the OpenAI module import
        mock_openai = MagicMock()
        with patch.dict('sys.modules', {'openai': mock_openai}):
            with patch('universal_llm.adapters.openai.OpenAI', mock_openai.OpenAI):
                client = get_client(settings)
                assert client is not None
    
    def test_anthropic_client_initialization(self):
        """Test Anthropic client can be initialized"""
        settings = Settings(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            api_key="test-key"
        )
        
        # Mock the httpx module import
        mock_httpx = MagicMock()
        with patch.dict('sys.modules', {'httpx': mock_httpx}):
            with patch('universal_llm.adapters.anthropic.httpx', mock_httpx):
                client = get_client(settings)
                assert client is not None
    
    def test_ollama_client_initialization(self):
        """Test Ollama client can be initialized"""
        settings = Settings(
            provider="ollama",
            model="llama3.2",
            base_url="http://localhost:11434"
        )
        
        # Mock the httpx module import
        mock_httpx = MagicMock()
        with patch.dict('sys.modules', {'httpx': mock_httpx}):
            with patch('universal_llm.adapters.ollama.httpx', mock_httpx):
                client = get_client(settings)
                assert client is not None
    
    def test_invalid_provider_raises_error(self):
        """Test that invalid provider raises appropriate error"""
        settings = Settings(
            provider="invalid_provider",
            model="some-model"
        )
        
        with pytest.raises(LLMError) as exc_info:
            get_client(settings)
        
        assert "Unknown provider" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_openai_chat_mock(self):
        """Test OpenAI chat with mocked response"""
        settings = Settings(
            provider="openai",
            model="gpt-4o-mini",
            api_key="test-key"
        )
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello, world!"
        
        with patch('universal_llm.adapters.openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response
            
            client = get_client(settings)
            result = await client.chat([{"role": "user", "content": "Hello"}])
            
            assert result == "Hello, world!"
    
    @pytest.mark.asyncio
    async def test_anthropic_chat_mock(self):
        """Test Anthropic chat with mocked response"""
        settings = Settings(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            api_key="test-key"
        )
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [{"text": "Hello from Claude!"}]
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('universal_llm.adapters.anthropic.httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            client = get_client(settings)
            result = await client.chat([{"role": "user", "content": "Hello"}])
            
            assert result == "Hello from Claude!"
    
    @pytest.mark.asyncio
    async def test_ollama_chat_mock(self):
        """Test Ollama chat with mocked response"""
        settings = Settings(
            provider="ollama",
            model="llama3.2",
            base_url="http://localhost:11434"
        )
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": {"content": "Hello from Ollama!"}
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('universal_llm.adapters.ollama.httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            client = get_client(settings)
            result = await client.chat([{"role": "user", "content": "Hello"}])
            
            assert result == "Hello from Ollama!"
    
    def test_sync_chat_methods(self):
        """Test that sync methods work without errors"""
        settings = Settings(
            provider="openai",
            model="gpt-4o-mini",
            api_key="test-key"
        )
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Sync response!"
        
        with patch('universal_llm.adapters.openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response
            
            client = get_client(settings)
            result = client.chat_sync([{"role": "user", "content": "Hello"}])
            
            assert result == "Sync response!"
    
    def test_ask_convenience_method(self):
        """Test the ask convenience method"""
        settings = Settings(
            provider="openai",
            model="gpt-4o-mini",
            api_key="test-key"
        )
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Answer!"
        
        with patch('universal_llm.adapters.openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response
            
            client = get_client(settings)
            result = client.ask("What is 2+2?")
            
            assert result == "Answer!"
    
    def test_error_handling(self):
        """Test that errors are properly normalized"""
        settings = Settings(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022"
        )
        
        with pytest.raises(LLMError) as exc_info:
            client = get_client(settings)
        
        assert exc_info.value.provider == "anthropic"
        assert "API key is required" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])