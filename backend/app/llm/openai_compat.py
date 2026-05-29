"""OpenAICompatProvider：任何 OpenAI 兼容端点。LLM_BACKEND=openai

同一份代码即可指向：
  - Gemini 免费层 / 付费   (https://generativelanguage.googleapis.com/v1beta/openai)
  - Groq                    (https://api.groq.com/openai/v1)
  - OpenRouter              (https://openrouter.ai/api/v1)
靠 OPENAI_BASE_URL / OPENAI_API_KEY / OPENAI_MODEL 三个环境变量切换。
"""
import json
from typing import AsyncIterator

import httpx

from app.config import settings
from app.llm.base import LLMProvider
from app.schemas import ChatMessage


class OpenAICompatProvider(LLMProvider):
    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        payload = {
            "model": settings.openai_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
        }
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST", url, json=payload, headers=headers
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    line = line.strip()
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[len("data:") :].strip()
                    if data == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    choices = obj.get("choices") or [{}]
                    chunk = choices[0].get("delta", {}).get("content")
                    if chunk:
                        yield chunk
