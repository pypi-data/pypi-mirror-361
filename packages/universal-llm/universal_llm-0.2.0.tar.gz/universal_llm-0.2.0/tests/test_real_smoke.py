import pytest
import os
import asyncio
from universal_llm import Settings, get_client
from universal_llm.base import LLMError


class TestRealSmokeTests:
    """Real smoke tests that call actual APIs - requires API keys in environment"""
    
    def test_package_imports(self):
        """Test that the main package imports work"""
        from universal_llm import Settings, get_client
        assert Settings is not None
        assert get_client is not None
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_openai_real_call(self):
        """Test real OpenAI API call"""
        settings = Settings(
            provider="openai",
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        client = get_client(settings)
        response = client.ask("Say 'Hello from OpenAI' and nothing else")
        
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"OpenAI Response: {response}")
    
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    @pytest.mark.asyncio
    async def test_anthropic_real_call(self):
        """Test real Anthropic API call"""
        settings = Settings(
            provider="anthropic",
            model="claude-3-5-haiku-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        client = get_client(settings)
        response = await client.chat([
            {"role": "user", "content": "Say 'Hello from Anthropic' and nothing else"}
        ])
        
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"Anthropic Response: {response}")
    
    @pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set")
    def test_google_real_call(self):
        """Test real Google API call"""
        settings = Settings(
            provider="google",
            model="gemini-2.0-flash",
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        client = get_client(settings)
        response = client.ask("Say 'Hello from Google' and nothing else")
        
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"Google Response: {response}")
    
    @pytest.mark.skipif(not os.getenv("TEST_OLLAMA"), reason="TEST_OLLAMA not set - ollama server not running")
    def test_ollama_real_call(self):
        """Test real Ollama API call - requires Ollama running locally"""
        settings = Settings(
            provider="ollama",
            model="llama3.2:1b",  # Use small model for testing
            base_url="http://localhost:11434"
        )
        
        client = get_client(settings)
        response = client.ask("Say 'Hello from Ollama' and nothing else")
        
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"Ollama Response: {response}")
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    @pytest.mark.asyncio
    async def test_openai_streaming(self):
        """Test real OpenAI streaming"""
        settings = Settings(
            provider="openai",
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        client = get_client(settings)
        chunks = []
        
        async for chunk in await client.chat([
            {"role": "user", "content": "Count from 1 to 5, one number per response chunk"}
        ], stream=True):
            if isinstance(chunk, str):
                chunks.append(chunk)
                print(f"Chunk: {chunk}")
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0
        print(f"Full streaming response: {full_response}")
    
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    @pytest.mark.asyncio
    async def test_anthropic_streaming(self):
        """Test real Anthropic streaming"""
        settings = Settings(
            provider="anthropic",
            model="claude-3-5-haiku-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        client = get_client(settings)
        chunks = []
        
        async for chunk in await client.chat([
            {"role": "user", "content": "Count from 1 to 3, one number per response chunk"}
        ], stream=True):
            if isinstance(chunk, str):
                chunks.append(chunk)
                print(f"Chunk: {chunk}")
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0
        print(f"Full streaming response: {full_response}")
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_openai_with_kwargs(self):
        """Test OpenAI with provider-specific kwargs"""
        settings = Settings(
            provider="openai",
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        client = get_client(settings)
        response = client.chat_sync([
            {"role": "user", "content": "Respond with exactly 10 words"}
        ], max_tokens=20, temperature=0.1)
        
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"OpenAI with kwargs: {response}")
    
    @pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
    @pytest.mark.asyncio
    async def test_anthropic_with_kwargs(self):
        """Test Anthropic with provider-specific kwargs"""
        settings = Settings(
            provider="anthropic",
            model="claude-3-5-haiku-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        client = get_client(settings)
        response = await client.chat([
            {"role": "user", "content": "Respond with exactly 10 words"}
        ], max_tokens=25, stop_sequences=["END"])
        
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"Anthropic with kwargs: {response}")
    
    def test_error_handling_no_api_key(self):
        """Test error handling when API key is missing"""
        settings = Settings(
            provider="anthropic",
            model="claude-3-5-haiku-20241022"
            # No API key
        )
        
        with pytest.raises(LLMError) as exc_info:
            get_client(settings)
        
        assert exc_info.value.provider == "anthropic"
        assert "API key is required" in str(exc_info.value)
    
    def test_error_handling_invalid_provider(self):
        """Test error handling for invalid provider"""
        settings = Settings(
            provider="nonexistent",
            model="some-model"
        )
        
        with pytest.raises(LLMError) as exc_info:
            get_client(settings)
        
        assert "Unknown provider" in str(exc_info.value)


if __name__ == "__main__":
    # Run specific tests based on available API keys
    test_args = [__file__, "-v", "-s"]  # -s to see print statements
    
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OPENAI_API_KEY found - will test OpenAI")
    else:
        print("❌ OPENAI_API_KEY not found - skipping OpenAI tests")
        
    if os.getenv("ANTHROPIC_API_KEY"):
        print("✅ ANTHROPIC_API_KEY found - will test Anthropic")
    else:
        print("❌ ANTHROPIC_API_KEY not found - skipping Anthropic tests")
        
    if os.getenv("GOOGLE_API_KEY"):
        print("✅ GOOGLE_API_KEY found - will test Google")
    else:
        print("❌ GOOGLE_API_KEY not found - skipping Google tests")
        
    if os.getenv("TEST_OLLAMA"):
        print("✅ TEST_OLLAMA found - will test Ollama")
    else:
        print("❌ TEST_OLLAMA not found - skipping Ollama tests")
    
    pytest.main(test_args)