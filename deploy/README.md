# 后端部署指南（Hugging Face Spaces）

把后端跑到公网,让手机 demo 能真聊。**全程约 10 分钟**,大部分是点网页。

> 镜像在本仓库沙箱里无法 build（网络拦截 Docker Hub），但容器内的启动命令与所有
> API/SSE 已用等价命令实测通过。到了 HF（能正常访问 Docker Hub）即可正常构建。

---

## 你需要先准备（我替不了的 3 样）

1. **Hugging Face 账号** → https://huggingface.co/join （免费）
2. **HF write token** → https://huggingface.co/settings/tokens → New token，权限选 **Write**
3. **Gemini API key** → https://aistudio.google.com/apikey （免费层即可）

---

## 方式 A：一键脚本（推荐）

```bash
# 1) 先在网页建一个空 Space：https://huggingface.co/new-space
#    - Owner: 你；Space name: anime-rp-backend
#    - SDK 选 【Docker】→ 【Blank】；可见性 Public
# 2) 回到本仓库根目录，跑：
HF_USER=你的用户名 HF_SPACE=anime-rp-backend HF_TOKEN=hf_xxx ./deploy/deploy_hf.sh
```

脚本会把 `Dockerfile + backend/ + README_HF.md` 推到 Space，HF 自动构建。

## 方式 B：纯网页拖拽（不想用命令行）

1. 建 Space（同上，SDK 选 Docker）
2. 在 Space 的 **Files → Add file → Upload** 里上传：
   - `Dockerfile`
   - `README_HF.md` → **改名为 `README.md`** 上传（HF 靠它的 YAML 配置 Space）
   - 整个 `backend/` 文件夹（不含 `.env`）

---

## 关键一步：配置环境变量（**别跳过**）

Space → **Settings → Variables and secrets**：

| 名称 | 值 | 类型 |
|---|---|---|
| `LLM_BACKEND` | `openai` | Variable |
| `OPENAI_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai` | Variable |
| `OPENAI_MODEL` | `gemini-2.5-flash-lite` | Variable |
| `OPENAI_API_KEY` | 你的 Gemini key | **Secret** ⚠️ |

> `OPENAI_API_KEY` 一定要存成 **Secret**,不是 Variable——否则会暴露。
> 改完变量后 Space 会自动重启生效。

---

## 部署完怎么用

1. 后端地址：`https://你的用户名-anime-rp-backend.hf.space`
2. 浏览器开 `https://你的用户名-anime-rp-backend.hf.space/api/health`
   看到 `{"status":"ok","llm_backend":"openai"}` 就成了。
3. 打开手机上的 Pages demo → 右上角徽标 → 填入上面这个后端地址 → **变真聊天**。

---

## 注意事项

- **冷启动**：免费 Space 闲置会休眠，下次访问等十几秒唤醒。内测无所谓；
  Apple 审核期间和正式上线要换不休眠的托管（见 `../UNIT_ECONOMICS.md` 思路）。
- **CORS**：后端已设 `allow_origins=["*"]`，方便联调；上线前应收紧到你的前端域名。
- **审核**：当前 `moderation.py` 是放行占位，上线前务必接 OpenAI Moderation（见 `../TECH_DESIGN.md §7`）。
- **key 安全**：key 只存在后端 Secret 里，永不进前端/App——这正是"App 只是遥控器"的意义。
