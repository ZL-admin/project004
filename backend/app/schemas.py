"""数据结构（pydantic）。骨架阶段够用，Phase 1 后期对齐 TECH_DESIGN 的 DB schema。"""
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # system / user / assistant
    content: str


class Character(BaseModel):
    id: str
    name: str
    tagline: str          # 一句话简介
    persona: str          # 人设（进系统提示词）
    greeting: str         # 开场白
    tags: list[str] = []
    avatar: str = "🙂"     # 先用 emoji 占位，Phase 2 接图库/生图


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
