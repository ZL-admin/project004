"""配置：全部由环境变量驱动，切换 LLM 后端只需改 .env，代码不动。"""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM 后端：mock / ollama / openai
    llm_backend: str = os.getenv("LLM_BACKEND", "mock")

    # ollama
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "mistral")

    # openai 兼容（Gemini 免费层 / Groq / OpenRouter / 付费）
    openai_base_url: str = os.getenv(
        "OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai"
    )
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gemini-2.5-flash-lite")

    # 滑动窗口：最近多少条历史进 prompt
    history_window: int = int(os.getenv("HISTORY_WINDOW", "20"))


settings = Settings()
