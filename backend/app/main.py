"""FastAPI 应用：发现角色 + SSE 流式聊天（MVP 骨架）。

运行：cd backend && uvicorn app.main:app --reload --port 8000
然后浏览器打开 http://localhost:8000
"""
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.characters import CHARACTERS, CHARACTERS_BY_ID
from app.config import settings
from app.llm.factory import get_provider
from app.moderation import moderate
from app.prompt import build_messages
from app.schemas import SendMessageRequest
from app.store import add_message, get_history, reset

app = FastAPI(title="二次元 AI 角色扮演 · MVP 骨架")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = get_provider()


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.get("/api/health")
async def health():
    return {"status": "ok", "llm_backend": settings.llm_backend}


@app.get("/api/characters")
async def list_characters():
    return CHARACTERS


@app.get("/api/characters/{cid}")
async def get_character(cid: str):
    c = CHARACTERS_BY_ID.get(cid)
    if not c:
        raise HTTPException(404, "角色不存在")
    return c


@app.post("/api/conversations/{cid}/messages")
async def send_message(cid: str, req: SendMessageRequest):
    character = CHARACTERS_BY_ID.get(cid)
    if not character:
        raise HTTPException(404, "角色不存在")

    # 1) 输入审核（命中即拦截，不调 LLM）
    if not await moderate(req.content):
        async def blocked():
            yield sse("blocked", {"reason": "safety", "fallback": "咱们换个话题聊聊吧~"})

        return StreamingResponse(blocked(), media_type="text/event-stream")

    # 2) 组装 prompt（稳定前缀 + 滑动窗口历史），再记录用户消息
    messages = build_messages(character, get_history(cid), req.content)
    add_message(cid, "user", req.content)

    async def event_stream():
        parts: list[str] = []
        try:
            async for chunk in provider.stream_chat(messages):
                parts.append(chunk)
                yield sse("token", {"t": chunk})
        except Exception as exc:  # 供应商失败：透传错误（Phase 2 改为降级到备份）
            yield sse("error", {"message": str(exc)})
            return

        reply = "".join(parts)
        # 3) 输出审核（骨架为 stub；生产建议先缓冲再审或分段审，见 moderation.py）
        if not await moderate(reply):
            reply = "（这段我不太方便说，我们聊点别的吧~）"
            yield sse("blocked", {"reason": "safety", "fallback": reply})
        add_message(cid, "assistant", reply)
        yield sse("done", {"len": len(reply)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.delete("/api/conversations/{cid}")
async def reset_conversation(cid: str):
    reset(cid)
    return {"status": "reset"}


# 静态前端（放最后，避免吃掉 /api 路由）
app.mount("/", StaticFiles(directory="static", html=True), name="static")
