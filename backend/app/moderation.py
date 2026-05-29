"""内容审核占位（过审/合规的生命线，见 PRD §6 / TECH_DESIGN §5、§7）。

骨架阶段直接放行，保证零成本即可跑通。
上线前接 OpenAI Moderation API（免费、不占额度）：输入 + 输出双层审核，
命中即拦截并返回安全兜底回复，同时记 messages.flagged 做审计。
"""


async def moderate(text: str) -> bool:
    """返回 True 表示内容安全放行。

    TODO(上线前): 调 OpenAI Moderation API (omni-moderation-latest)，
    命中 categories 时返回 False。
    """
    return True
