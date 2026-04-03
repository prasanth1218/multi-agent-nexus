"""OpenAI LLM client wrapper with streaming and retry support."""
import asyncio
from typing import AsyncGenerator
from openai import AsyncOpenAI
from config import get_settings

_client: AsyncOpenAI | None = None

def get_client() -> AsyncOpenAI:
    """Get or create the OpenAI async client (connection reuse)."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
    return _client

async def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Non-streaming chat completion for quick tasks (e.g., planning)."""
    settings = get_settings()
    client = get_client()
    response = await client.chat.completions.create(
        model=model or settings.agent_model,
        messages=messages,
        temperature=temperature if temperature is not None else settings.temperature,
        max_tokens=max_tokens or settings.max_tokens,
    )
    return response.choices[0].message.content or ""

async def chat_completion_stream(
    messages: list[dict],
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> AsyncGenerator[str, None]:
    """Streaming chat completion — yields tokens as they arrive."""
    settings = get_settings()
    client = get_client()
    stream = await client.chat.completions.create(
        model=model or settings.agent_model,
        messages=messages,
        temperature=temperature if temperature is not None else settings.temperature,
        max_tokens=max_tokens or settings.max_tokens,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content

async def chat_completion_with_retry(
    messages: list[dict],
    model: str | None = None,
    max_retries: int = 2,
    **kwargs
) -> str:
    """Chat completion with exponential backoff retry."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return await chat_completion(messages, model=model, **kwargs)
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt * 0.5)
    raise last_error