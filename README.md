# 二次元 AI 角色扮演 App —— 项目文档

对标 PolyBuzz / Character.AI 的 AI 角色扮演聊天 App。
**路线**：纯 SFW · 双商店上架（iOS + Android）· 现成 LLM API · 二次元垂直切入。

## 文档导航

| 文档 | 内容 | 读它来回答 |
|---|---|---|
| [`PRD.md`](./PRD.md) | 产品需求 | 做什么、给谁、MVP 范围、合规要求 |
| [`TECH_DESIGN.md`](./TECH_DESIGN.md) | 技术方案 | 架构、数据模型、API、聊天管线、成本控制 |
| [`UNIT_ECONOMICS.md`](./UNIT_ECONOMICS.md) | 单位经济结论 | 选哪个模型、能不能赚钱、降本杠杆 |
| [`unit_economics.py`](./unit_economics.py) | 成本测算脚本 | 改假设重跑：`python3 unit_economics.py` |
| [`ROADMAP.md`](./ROADMAP.md) | 路线图/任务拆解 | 分几步、每步做什么（可当 backlog）|

## 当前状态
- ✅ Phase 0：定位 + 单位经济（已确认可行，模型选型是生死线）
- ⏭️ 下一步：Phase 1 MVP（发现→聊天→记忆→自建角色）

## 一分钟结论
1. 单位经济能跑通，**但免费层必须用最便宜的模型档（如 gemini-2.5-flash-lite）**——模型选型差 20 倍。
2. 成本几乎全在 input token，两个降本杠杆：**便宜模型 + 前缀缓存**。
3. 真正的风险不在 token 成本，而在 **获客成本(CAC)** 和 **过审/合规**。
