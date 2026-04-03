"""Base agent class with streaming support."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator
from services.llm import chat_completion, chat_completion_stream


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str, description: str, model: str | None = None):
        self.name = name
        self.description = description
        self.model = model

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt defining this agent's role and behavior."""
        ...

    def _build_messages(self, user_message: str, context: list[dict] | None = None) -> list[dict]:
        """Build the message list for the LLM call."""
        messages = [{"role": "system", "content": self.system_prompt}]

        if context:
            # Add recent conversation context (last 10 messages max for speed)
            for msg in context[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": user_message})
        return messages

    async def run(self, user_message: str, context: list[dict] | None = None) -> str:
        """Run the agent and return the full response (non-streaming)."""
        messages = self._build_messages(user_message, context)
        return await chat_completion(messages, model=self.model)

    async def run_stream(
        self, user_message: str, context: list[dict] | None = None
    ) -> AsyncGenerator[str, None]:
        """Run the agent and yield tokens as they arrive (streaming)."""
        messages = self._build_messages(user_message, context)
        async for token in chat_completion_stream(messages, model=self.model):
            yield token
