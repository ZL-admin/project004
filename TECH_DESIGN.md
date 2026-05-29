# 技术方案 —— 二次元 AI 角色扮演 App（MVP）

> 配套：`PRD.md`（需求）、`UNIT_ECONOMICS.md`（成本）、`ROADMAP.md`（任务）
> 原则：用现成 API、最小可上瘾循环优先、成本与过审从第一天就纳入设计。

## 1. 架构总览

```
┌─────────────┐     HTTPS / SSE      ┌──────────────────────┐
│  App 客户端  │ ───────────────────▶ │   API 服务 (FastAPI)  │
│ Expo/RN     │ ◀───────────────────  │                      │
│ iOS+Android │   流式 token          │  ┌────────────────┐  │
└─────────────┘                       │  │ Chat Orchestr. │  │
                                      │  │ - 组 prompt     │  │
   RevenueCat (IAP 订阅)               │  │ - 记忆检索      │  │
                                      │  │ - 审核(in/out)  │  │
                                      │  │ - 模型路由/降级 │  │
                                      │  └───────┬────────┘  │
                                      └──────────┼───────────┘
                            ┌────────────────────┼────────────────────┐
                            ▼                     ▼                     ▼
                     ┌────────────┐       ┌─────────────┐       ┌──────────────┐
                     │ Postgres   │       │ Redis       │       │ LLM 供应商    │
                     │ +pgvector  │       │ 缓存/限速    │       │ Gemini/OpenAI │
                     │ 用户/角色/  │       │ 会话热数据   │       │ /DeepSeek     │
                     │ 消息/记忆   │       └─────────────┘       │ +Moderation  │
                     └────────────┘                             └──────────────┘
```

## 2. 技术选型（理由见括号）

| 层 | 选型 | 理由 |
|---|---|---|
| 客户端 | **Expo (React Native)** | 一套码双端、上架生态成熟、迭代快 |
| 后端 | **FastAPI (Python)** | SSE/异步好写、AI 生态最全 |
| 主数据库 | **Postgres + pgvector** | 关系数据 + 向量记忆一库搞定，少运维 |
| 缓存/限速 | **Redis** | 会话热数据、限流、幂等 |
| LLM 主力 | **gemini-2.5-flash-lite** | 最便宜、SFW 友好、自带安全过滤 |
| LLM 升级/备份 | gpt-4o-mini / deepseek-v3 | 付费层质量、容灾分流 |
| 审核 | **OpenAI Moderation API** | 免费、不占额度 |
| 订阅 | **RevenueCat** | 统一管 iOS/Android IAP |
| 托管 | Fly.io / Railway → 起步 | 简单、便宜、易扩 |
| 鉴权 | JWT (access+refresh) | 无状态、客户端友好 |

## 3. 数据模型（Postgres）

```sql
-- 用户
users (
  id            uuid pk,
  email         text unique,
  auth_provider text,              -- apple/google/email
  age_confirmed bool default false,
  is_premium    bool default false,
  created_at    timestamptz,
  deleted_at    timestamptz        -- 软删除，支持账号删除合规
)

-- 角色（含官方预置 + 用户自建 UGC）
characters (
  id            uuid pk,
  creator_id    uuid fk users null,  -- null=官方预置
  name          text,
  avatar_url    text,
  tagline       text,                -- 一句话简介
  persona       text,                -- 人设（进系统提示词）
  greeting      text,                -- 开场白
  example_dialogs jsonb,             -- few-shot 范例（稳住语气）
  tags          text[],              -- 题材/属性，发现页用
  visibility    text,                -- public/private
  is_featured   bool default false,
  status        text default 'active', -- active/blocked(被举报下架)
  created_at    timestamptz
)

-- 会话（用户↔某角色）
conversations (
  id            uuid pk,
  user_id       uuid fk,
  character_id  uuid fk,
  summary       text,                -- 长期记忆摘要（滚动更新）
  last_active   timestamptz,
  created_at    timestamptz,
  unique(user_id, character_id)      -- 一个用户对一个角色一条主会话
)

-- 消息
messages (
  id            uuid pk,
  conversation_id uuid fk,
  role          text,                -- user/assistant/system
  content       text,
  tokens        int,                 -- 计费/分析
  flagged       bool default false,  -- 审核命中记录
  created_at    timestamptz
)

-- 长期记忆（向量检索）
memories (
  id            uuid pk,
  conversation_id uuid fk,
  content       text,                -- 一条记忆事实
  embedding     vector(768),         -- pgvector
  created_at    timestamptz
)

-- 举报（过审合规需要）
reports (
  id uuid pk, reporter_id uuid, target_type text, target_id uuid,
  reason text, status text, created_at timestamptz
)

-- 用量计数（限速/计费）
usage_counters (
  user_id uuid, period date, msg_count int, token_in bigint, token_out bigint,
  primary key(user_id, period)
)
```

## 4. API 设计（REST + SSE）

```
# 鉴权
POST /auth/login              # 第三方/邮箱登录，返回 JWT
POST /auth/refresh
DELETE /account              # 账号删除（合规，级联软删 + 排程硬删）

# 角色
GET  /characters             # 发现页：分页/标签筛选/搜索
GET  /characters/{id}
POST /characters             # 自建角色（先过审）
PATCH/DELETE /characters/{id}

# 会话 & 聊天
GET  /conversations          # 我的会话列表
GET  /conversations/{id}/messages
POST /conversations/{id}/messages   # 发消息 → SSE 流式返回 AI 回复
DELETE /conversations/{id}    # 重置/清空

# 安全 & 合规
POST /reports                # 举报角色/消息
POST /blocks                 # 拉黑

# 计费（Phase 2）
POST /billing/webhook        # RevenueCat webhook 同步订阅状态
```

### 聊天主接口（核心，SSE）
`POST /conversations/{id}/messages`，请求体 `{ "content": "..." }`，
返回 `text/event-stream`：
```
event: token   data: {"t":"你"}
event: token   data: {"t":"好"}
...
event: done    data: {"message_id":"...","tokens_out":123}
```
错误/审核拦截：
```
event: blocked data: {"reason":"safety","fallback":"咱们换个话题聊聊吧～"}
```

## 5. 聊天编排管线（Chat Orchestrator —— 系统核心）

每条用户消息按顺序经过：

```
1. 限速检查        Redis：免费用户日配额；超限→提示升级
2. 输入审核        Moderation API：命中→拦截，返回安全兜底，不调 LLM
3. 组装 Prompt     见下方结构；尽量构造可缓存前缀
4. 记忆检索        pgvector：取 top-k 相关记忆拼入
5. 模型路由        免费→flash-lite；付费→flash；失败→降级到备份供应商
6. 流式生成        SSE 逐 token 透传给客户端
7. 输出审核        对完整回复再过一次 Moderation；命中→替换为兜底
8. 落库 & 计数     存消息、更新 usage_counters
9. 记忆更新        异步：每 N 轮触发摘要 + 抽取记忆写入 memories
```

### Prompt 结构（注意缓存友好：稳定内容放前面）
```
[可缓存前缀 —— 尽量不变，命中缓存价=10%]
  - 全局系统指令（SFW 边界、roleplay 规则、安全话术）
  - 角色卡：persona + 说话风格 + example_dialogs
  - 长期记忆摘要 conversations.summary
[半稳定]
  - 检索到的相关记忆 top-k
[动态 —— 每次变化]
  - 最近 N 轮对话历史（滑动窗口）
  - 本次用户消息
```
> 把"系统指令+角色卡+摘要"做成稳定前缀是**最高回报的降本工程**（见 UNIT_ECONOMICS）。

### 记忆策略（防失忆 + 控成本的平衡）
- **短期**：滑动窗口保留最近 N 轮（控制 history_tokens ≈ 3000）。
- **长期**：每 N 轮异步生成/更新 `conversations.summary`；并抽取关键事实写入 `memories`（向量化）。
- **检索**：下次对话用当前上下文向量检索 top-k 记忆拼入，而非把全历史塞进去（否则成本线性爆炸）。

## 6. 成本控制（落到代码的开关）
1. **分层路由**：`is_premium` 决定模型档位。
2. **前缀缓存**：稳定 prompt 前缀复用供应商缓存。
3. **上下文上限**：硬限制 history_tokens + 摘要压缩。
4. **限速**：免费用户日配额（Redis 计数）。
5. **可观测**：每条消息记 token_in/out，按用户/模型出成本报表（对账 UNIT_ECONOMICS 假设）。

## 7. 安全与合规（工程落点）
- 输入+输出双审核，命中即拦截 + 兜底 + 记 `messages.flagged`。
- 系统提示词内置 SFW 边界与拒答话术（自伤/未成年人等敏感话题给求助资源）。
- 账号删除：`DELETE /account` 软删 + 排程硬删（含聊天数据），满足"可删除"合规。
- UGC 举报：`/reports` → 后台审核 → `characters.status=blocked`，承诺 24h 处理（Apple 1.2）。
- 密钥与数据：LLM key 走服务端，绝不下发客户端；聊天数据加密存储。

## 8. 部署与可观测
- 环境：dev / staging / prod；密钥用环境变量/密钥管理。
- 日志/监控：请求延迟、首 token 延迟、审核命中率、各模型 token 成本、错误率。
- 容灾：LLM 供应商多活，超时/限流自动降级到备份。

## 9. MVP 故意不做的简化（技术债，记录在案）
- 头像用预置图库（不接生图）。
- 记忆摘要用规则触发（不做复杂记忆图谱）。
- 单区域部署（不做多区域）。
- 审核用现成 API（不自训分类器）。
> 这些都在 Phase 2+ 视数据再补。
```
