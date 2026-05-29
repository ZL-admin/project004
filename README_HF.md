---
title: 二次元 AI 角色扮演后端
emoji: 🗡️
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# 二次元 AI 角色扮演 · 后端 API

FastAPI + SSE 流式聊天后端。这是 [project004](https://github.com/ZL-admin/project004) 的后端服务，
部署在 Hugging Face Spaces（Docker SDK）。

## 配置（在 Space 的 Settings → Variables and secrets 里填）

| 变量 | 值 | 类型 |
|---|---|---|
| `LLM_BACKEND` | `openai` | Variable |
| `OPENAI_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai` | Variable |
| `OPENAI_MODEL` | `gemini-2.5-flash-lite` | Variable |
| `OPENAI_API_KEY` | 你的 Gemini key | **Secret** |

> ⚠️ `OPENAI_API_KEY` 必须存为 **Secret**（不是 Variable），否则会暴露在构建日志/前端。

## 端点

- `GET /api/health` — 健康检查
- `GET /api/characters` — 角色列表
- `POST /api/conversations/{id}/messages` — SSE 流式聊天

详见仓库内 `backend/README.md`。
