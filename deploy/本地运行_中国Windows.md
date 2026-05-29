# 本地真聊起来（中国 + Windows + DeepSeek 直连）

**目标**：在你的 Windows 电脑上跑后端，手机连同一 WiFi 就能真聊。
**全程不碰墙**：DeepSeek 在国内有直连节点，不需要 VPN。

---

## 为什么走本地（而不是 Hugging Face）

- Hugging Face 在墙外，你手机访问会卡/打不开 —— 部署上去也用不了。
- 本地后端在你自己电脑上，手机走局域网直连，**又快又稳**。
- DeepSeek 国内直连，延迟低、便宜。

---

## 准备（约 5 分钟）

1. **装 Python**：https://www.python.org/downloads/
   —— 安装时**务必勾选 “Add Python to PATH”**（否则脚本找不到 python）。
2. **领 DeepSeek key**：https://platform.deepseek.com
   —— 注册 → 充值（几块钱就够测很久）→ API keys → 新建 → 复制 `sk-...`
3. **下载本项目代码**：
   - 进 https://github.com/ZL-admin/project004 （分支 `claude/busy-clarke-TFGgs`）
   - **Code → Download ZIP**，解压到比如 `D:\project004`

---

## 启动（一步）

1. 打开解压出的文件夹，进 `deploy\`，**双击 `start_windows.bat`**
2. 第一次会自动建 `backend\.env` 并提示填 key。用**记事本**打开 `backend\.env`，改成：

   ```
   LLM_BACKEND=openai
   OPENAI_BASE_URL=https://api.deepseek.com/v1
   OPENAI_MODEL=deepseek-chat
   OPENAI_API_KEY=sk-你刚复制的key
   ```

   保存后，**再次双击 `start_windows.bat`**。
3. 启动时若弹出 **Windows 防火墙提示**，勾选「专用网络」并「允许访问」
   —— 不允许的话手机连不上。

脚本会打印两个地址：
```
电脑本机访问：   http://localhost:8000
手机访问(同WiFi)： http://192.168.x.x:8000   ← 手机浏览器打开这个
```

---

## 手机上真聊

- 确保**手机和电脑连同一个 WiFi**。
- 手机浏览器打开上面那个 `http://192.168.x.x:8000`。
- 选角色 → 开聊。这次是 **DeepSeek 真 AI**，不是假数据。

> 注意：这里要用**后端自带的页面**（`http://192.168.x.x:8000`），
> 不要用 GitHub Pages 那个 demo —— 那个是 https，会拦截连本地 http 后端（浏览器安全限制），
> 而且 Pages 本身也在墙外。本地自带页面是 http 同源，没有这个问题。

---

## 常见问题

| 现象 | 原因 / 解决 |
|---|---|
| 双击闪退 | 没装 Python 或没勾 PATH。重装 Python 勾选 “Add to PATH”。|
| 手机打不开 | ①没连同一 WiFi ②防火墙没放行（重跑脚本看防火墙弹窗）③有的 WiFi 开了"AP隔离"，换个热点试 |
| 回复仍是"mock·假数据" | `.env` 没填好，或 `LLM_BACKEND` 不是 `openai`。检查 4 行配置 |
| 报错 401 / Unauthorized | DeepSeek key 错或没充值。去 platform.deepseek.com 查 |
| 报错连接超时 | 检查网络；DeepSeek 国内直连，一般**关掉 VPN 反而更稳** |

---

## 换其它国产模型（都是改 `.env`，代码不动）

| 模型 | OPENAI_BASE_URL | OPENAI_MODEL |
|---|---|---|
| DeepSeek（推荐） | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 通义千问 Qwen | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen3.6-flash` |
| Kimi（月之暗面） | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |

> 全都国内直连、OpenAI 兼容。这正是当初做"可插拔 provider"的价值：换供应商零改代码。
