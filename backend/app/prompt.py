"""Prompt assembly.

Follows the structure in TECH_DESIGN §5: stable content first (so it can hit
prefix caching later to cut cost), dynamic content (history, current input) last.
"""
from app.config import settings
from app.schemas import Character, ChatMessage

GLOBAL_SYSTEM = (
    "You are an anime roleplay AI. "
    "IMPORTANT: always write every reply in natural English, no matter what "
    "language the user writes in.\n"
    "Always stay in character, play the role in the first person in an immersive "
    "way, and match the character's tone and personality.\n"
    "Keep all content safe for work (SFW): no sexual content, graphic violence, "
    "illegal activity, or self-harm / harm to others. If the user steers toward "
    "such topics, gently guide the conversation back to something safe and "
    "lighthearted without breaking character with a blunt refusal.\n"
    "Keep replies concise, natural, and immersive; avoid long lectures and never "
    "reveal that you are an AI."
)


def build_messages(
    character: Character, history: list[ChatMessage], user_msg: str
) -> list[ChatMessage]:
    # —— Stable prefix (kept as constant as possible for caching): global rules + character card ——
    system = (
        f"{GLOBAL_SYSTEM}\n\n"
        f"# The character you are playing\n"
        f"Name: {character.name}\n"
        f"Tagline: {character.tagline}\n"
        f"Persona: {character.persona}\n"
        f"Example of greeting style: {character.greeting}"
    )
    messages = [ChatMessage(role="system", content=system)]

    # —— Dynamic: sliding-window history + current input ——
    window = history[-settings.history_window :]
    messages.extend(window)
    messages.append(ChatMessage(role="user", content=user_msg))
    return messages
