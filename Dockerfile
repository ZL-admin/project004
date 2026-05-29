# 二次元 AI 角色扮演 —— 后端镜像（Hugging Face Spaces / 任意支持 Docker 的平台通用）
FROM python:3.11-slim

WORKDIR /app

# 先装依赖（利用 Docker 层缓存，改代码不必重装依赖）
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝后端代码
COPY backend/ ./

# HF Spaces 默认端口 7860；其它平台多用 $PORT，这里兼容两者
ENV PORT=7860
EXPOSE 7860

# 用 sh -c 让 $PORT 在运行时展开（平台注入的端口优先，否则回退 7860）
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
