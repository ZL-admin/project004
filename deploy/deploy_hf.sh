#!/usr/bin/env bash
# 一键把后端部署到 Hugging Face Spaces。
# 你需要先有：①HF 账号 ②一个 Docker 类型的 Space ③HF write token ④Gemini key
# 用法：
#   HF_USER=你的用户名 HF_SPACE=anime-rp-backend HF_TOKEN=hf_xxx ./deploy/deploy_hf.sh
set -euo pipefail

: "${HF_USER:?需要 HF_USER（你的 Hugging Face 用户名）}"
: "${HF_SPACE:?需要 HF_SPACE（Space 名，如 anime-rp-backend）}"
: "${HF_TOKEN:?需要 HF_TOKEN（HF write token，从 hf.co/settings/tokens 生成）}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
SPACE_URL="https://${HF_USER}:${HF_TOKEN}@huggingface.co/spaces/${HF_USER}/${HF_SPACE}"

echo "==> 克隆 Space 仓库"
git clone "https://huggingface.co/spaces/${HF_USER}/${HF_SPACE}" "$TMP" 2>/dev/null \
  || { echo "克隆失败：请先在 hf.co/new-space 建一个 Docker 类型的 Space（名为 ${HF_SPACE}）"; exit 1; }

echo "==> 拷贝部署文件"
cp "$REPO_ROOT/Dockerfile"      "$TMP/Dockerfile"
cp "$REPO_ROOT/.dockerignore"   "$TMP/.dockerignore"
cp "$REPO_ROOT/README_HF.md"    "$TMP/README.md"     # HF 用 README 的 YAML frontmatter 配置 Space
rm -rf "$TMP/backend"
cp -r "$REPO_ROOT/backend"      "$TMP/backend"
rm -f "$TMP/backend/.env"                            # 绝不上传本地密钥

echo "==> 提交并推送"
cd "$TMP"
git add -A
git -c user.email="deploy@local" -c user.name="deploy" commit -m "Deploy backend $(date -u +%FT%TZ)" || echo "(无改动)"
git push "$SPACE_URL" HEAD:main

echo ""
echo "✅ 已推送。HF 会自动构建镜像（首次 2-4 分钟）。"
echo "   构建日志：https://huggingface.co/spaces/${HF_USER}/${HF_SPACE}?logs=build"
echo "   ⚠️ 别忘了在 Space 的 Settings → Variables and secrets 里配置："
echo "      LLM_BACKEND=openai  (Variable)"
echo "      OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai  (Variable)"
echo "      OPENAI_MODEL=gemini-2.5-flash-lite  (Variable)"
echo "      OPENAI_API_KEY=你的Gemini key  (Secret!)"
echo "   后端地址：https://${HF_USER}-${HF_SPACE}.hf.space"
rm -rf "$TMP"
