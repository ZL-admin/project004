# 后端 · MVP 骨架

二次元 AI 角色扮演的最小可跑骨架：**Provider 抽象（mock/ollama/openai）+ FastAPI SSE 流式聊天 + 预置角色 + 极简前端**。
对应文档：`../PRD.md` `../TECH_DESIGN.md` `../ROADMAP.md`。

## 快速开始（零成本，30 秒跑通）

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env            # 默认 LLM_BACKEND=mock，无需任何 key
uvicorn app.main:app --reload --port 8000
```

浏览器打开 **http://localhost:8000** → 选个角色 → 开聊。
`mock` 模式返回假数据，但**整条管线和前端都是真的**（流式 SSE、会话记忆、角色卡）。

## 切换到真模型（改 `.env` 即可，代码不动）

**A. 本地 Ollama（免费、离线、隐私最好）**
```bash
ollama pull mistral          # 或 qwen2.5 / gemma2 / llama3.2
# .env:
LLM_BACKEND=ollama
OLLAMA_MODEL=mistral
```

**B. Gemini 免费层（质量接近未来生产模型，1000 次/天）**
```bash
# 到 Google AI Studio 拿免费 key
# .env:
LLM_BACKEND=openai
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
OPENAI_API_KEY=你的key
OPENAI_MODEL=gemini-2.5-flash-lite
```
> ⚠️ 免费层数据会被用于训练，仅用于内测/验证；公开上线请切付费或自托管（见 `../UNIT_ECONOMICS.md`）。

**C. Groq / OpenRouter / 付费**：同 openai 模式，只改 `OPENAI_BASE_URL` / `OPENAI_MODEL`。

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查（含当前 LLM 后端）|
| GET | `/api/characters` | 角色列表（发现页）|
| GET | `/api/characters/{id}` | 角色详情 |
| POST | `/api/conversations/{id}/messages` | 发消息 → **SSE 流式**回复 |
| DELETE | `/api/conversations/{id}` | 重置会话 |

SSE 事件：`token`（逐字）/ `done` / `blocked`（审核兜底）/ `error`。

## 结构

```
backend/app/
  main.py          # FastAPI 路由 + SSE
  config.py        # 环境变量配置
  schemas.py       # 数据结构
  characters.py    # 预置二次元角色（原创，规避版权）
  store.py         # 内存会话存储（⚠️ Phase 1 后期换 Postgres）
  prompt.py        # prompt 组装（稳定前缀在前，利于缓存）
  moderation.py    # 审核占位（⚠️ 上线前接 OpenAI Moderation）
  llm/             # Provider 抽象 + mock/ollama/openai 三实现
```

## 已知简化（技术债，已在代码注释标注）
- 内存存储，无鉴权，无数据库 → Phase 1 后期接 Postgres + pgvector + JWT。
- 审核为 stub，永远放行 → 上线前接 Moderation API。
- 记忆仅滑动窗口，无摘要/向量检索 → Phase 2。
- 供应商失败直接报错，无降级 → Phase 2 加多供应商容灾。
