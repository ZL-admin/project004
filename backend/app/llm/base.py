"""LLM Provider 抽象层。

统一接口，三个实现（mock / ollama / openai 兼容）由 LLM_BACKEND 切换。
这就是 TECH_DESIGN §2「模型路由/降级」的落地：今天插免费的，
上线改个环境变量切付费，调用方代码不动。
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator

from app.schemas import ChatMessage


class LLMProvider(ABC):
    @abstractmethod
    def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        """逐 token 流式产出回复文本（async generator）。"""
        raise NotImplementedError
