"""Prompt 组装。

按 TECH_DESIGN §5 的结构：稳定内容放前面（利于将来命中前缀缓存降本），
动态内容（历史、本次输入）放后面。
"""
from app.config import settings
from app.schemas import Character, ChatMessage

GLOBAL_SYSTEM = (
    "你是一个二次元角色扮演 AI。请始终保持角色设定，用第一人称沉浸式扮演，"
    "语气和性格要贴合人设。\n"
    "内容须保持健康(SFW)：不输出色情、露骨暴力、违法或自我/他人伤害相关内容；"
    "若用户引向此类话题，请温和地把话题带回安全、轻松的方向，不要生硬拒答而出戏。\n"
    "回复简洁自然、有代入感，避免大段说教，避免暴露自己是 AI。"
)


def build_messages(
    character: Character, history: list[ChatMessage], user_msg: str
) -> list[ChatMessage]:
    # —— 稳定前缀（尽量不变，利于缓存）：全局指令 + 角色卡 ——
    system = (
        f"{GLOBAL_SYSTEM}\n\n"
        f"# 你扮演的角色\n"
        f"姓名：{character.name}\n"
        f"简介：{character.tagline}\n"
        f"人设：{character.persona}\n"
        f"开场白风格示例：{character.greeting}"
    )
    messages = [ChatMessage(role="system", content=system)]

    # —— 动态：滑动窗口历史 + 本次输入 ——
    window = history[-settings.history_window :]
    messages.extend(window)
    messages.append(ChatMessage(role="user", content=user_msg))
    return messages
