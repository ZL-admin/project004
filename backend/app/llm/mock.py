"""MockProvider：无需任何 key/网络，返回假数据并模拟流式。

用于零成本调通整条管线和前端。LLM_BACKEND=mock
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
        # 暴露收到的上下文规模，方便验证「记忆/历史」确实拼进了 prompt
        history_turns = max(len(messages) - 2, 0)  # 扣掉 system 和本次 user
        reply = (
            f"（mock·上下文{len(messages)}条/历史{history_turns}条）"
            f"我听到你说「{user}」啦~ "
            f"把 LLM_BACKEND 改成 ollama 或 openai 就能真聊咯。"
        )
        for ch in reply:
            await asyncio.sleep(0.02)  # 模拟逐字流式
            yield ch
