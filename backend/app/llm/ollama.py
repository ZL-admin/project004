"""OllamaProvider：本地开源模型。LLM_BACKEND=ollama

先 `ollama pull mistral`（或 qwen2.5 / gemma2 等），再启动本服务。
"""
import json
from typing import AsyncIterator

import httpx

from app.config import settings
from app.llm.base import LLMProvider
from app.schemas import ChatMessage


class OllamaProvider(LLMProvider):
    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        payload = {
            "model": settings.ollama_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
        }
        url = f"{settings.ollama_base_url}/api/chat"
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    data = json.loads(line)  # Ollama 每行一个 JSON
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk
                    if data.get("done"):
                        break
