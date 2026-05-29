"""会话/消息的内存存储。

⚠️ 骨架用：进程重启即丢失，无并发隔离。
Phase 1 后期替换为 Postgres（见 TECH_DESIGN §3 的 conversations / messages 表）。
当前以 character_id 作为单用户会话 key（骨架无鉴权）。
"""
from collections import defaultdict

from app.schemas import ChatMessage

_history: dict[str, list[ChatMessage]] = defaultdict(list)


def get_history(conv_id: str) -> list[ChatMessage]:
    return list(_history[conv_id])


def add_message(conv_id: str, role: str, content: str) -> None:
    _history[conv_id].append(ChatMessage(role=role, content=content))


def reset(conv_id: str) -> None:
    _history.pop(conv_id, None)
