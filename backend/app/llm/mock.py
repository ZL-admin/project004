"""MockProvider: returns canned data and simulates streaming, no key/network needed.

Used to exercise the whole pipeline and frontend at zero cost. LLM_BACKEND=mock
"""
import asyncio
from typing import AsyncIterator

from app.llm.base import LLMProvider
from app.schemas import ChatMessage


class MockProvider(LLMProvider):
    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        user = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        # Expose the received context size to verify memory/history is in the prompt
        history_turns = max(len(messages) - 2, 0)  # minus system and current user
        reply = (
            f"(mock · context {len(messages)} msgs / history {history_turns}) "
            f"I heard you say \"{user}\"~ "
            f"Set LLM_BACKEND to ollama or openai for real chat."
        )
        for ch in reply:
            await asyncio.sleep(0.02)  # simulate token-by-token streaming
            yield ch
