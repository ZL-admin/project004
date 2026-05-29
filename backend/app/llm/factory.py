"""根据 LLM_BACKEND 选择 provider 实现。"""
from app.config import settings
from app.llm.base import LLMProvider
from app.llm.mock import MockProvider
from app.llm.ollama import OllamaProvider
from app.llm.openai_compat import OpenAICompatProvider


def get_provider() -> LLMProvider:
    backend = settings.llm_backend.lower()
    if backend == "mock":
        return MockProvider()
    if backend == "ollama":
        return OllamaProvider()
    if backend == "openai":
        return OpenAICompatProvider()
    raise ValueError(
        f"未知 LLM_BACKEND={settings.llm_backend!r}，应为 mock / ollama / openai"
    )
