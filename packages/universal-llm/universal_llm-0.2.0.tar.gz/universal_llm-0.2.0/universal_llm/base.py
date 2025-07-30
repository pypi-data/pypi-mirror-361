from typing import AsyncIterator, Iterator, List, Dict, Union, Any
import asyncio


class LLMError(RuntimeError):
    def __init__(self, message: str, code: str = None, provider: str = None):
        super().__init__(message)
        self.code = code
        self.provider = provider


class BaseLLMClient:
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Union[str, AsyncIterator[Any]]:
        raise NotImplementedError("Subclasses must implement chat method")
    
    def chat_sync(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[Any]]:
        if stream:
            return self._sync_stream_wrapper(messages, **kwargs)
        else:
            try:
                loop = asyncio.get_running_loop()
                return loop.run_until_complete(self.chat(messages, stream=False, **kwargs))
            except RuntimeError:
                return asyncio.run(self.chat(messages, stream=False, **kwargs))
    
    def ask(self, question: str) -> str:
        """Simple one-off question/answer"""
        return self.chat_sync([{"role": "user", "content": question}])
    
    async def ask_async(self, question: str) -> str:
        """Simple one-off question/answer (async)"""
        return await self.chat([{"role": "user", "content": question}])
    
    def _sync_stream_wrapper(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[Any]:
        async def _collect():
            async for chunk in self.chat(messages, stream=True, **kwargs):
                yield chunk
        
        try:
            loop = asyncio.get_running_loop()
            import asyncio
            import concurrent.futures
            
            async def run_generator():
                async for chunk in self.chat(messages, stream=True, **kwargs):
                    yield chunk
            
            gen = run_generator()
            while True:
                try:
                    future = asyncio.ensure_future(gen.__anext__())
                    yield loop.run_until_complete(future)
                except StopAsyncIteration:
                    break
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async_gen = _collect()
                while True:
                    try:
                        yield loop.run_until_complete(async_gen.__anext__())
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()