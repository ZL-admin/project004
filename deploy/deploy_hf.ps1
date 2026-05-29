#Requires -Version 5.1
<#
.SYNOPSIS
  一键把后端部署到 Hugging Face Spaces（Windows PowerShell 版）。
.DESCRIPTION
  与 deploy_hf.sh 等价的 Windows 原生版本。需先：
    1) 装 Git for Windows  2) 有 HF 账号 + 一个 Docker 类型的 Space
    3) HF write token      4) Gemini key（部署后在 Space 网页里配）
.EXAMPLE
  .\deploy\deploy_hf.ps1 -HfUser 你的用户名 -HfSpace anime-rp-backend -HfToken hf_xxx
#>
param(
  [Parameter(Mandatory = $true)][string]$HfUser,
  [Parameter(Mandatory = $true)][string]$HfSpace,
  [Parameter(Mandatory = $true)][string]$HfToken
)

$ErrorActionPreference = "Stop"

# 仓库根目录 = 本脚本所在目录(deploy/)的上一级
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("hf-deploy-" + [System.Guid]::NewGuid().ToString("N"))

Write-Host "==> 克隆 Space 仓库"
git clone "https://huggingface.co/spaces/$HfUser/$HfSpace" $Tmp
if ($LASTEXITCODE -ne 0) {
  Write-Error "克隆失败：请先在 https://huggingface.co/new-space 建一个 Docker 类型的 Space（名为 $HfSpace）"
  exit 1
}

Write-Host "==> 拷贝部署文件"
Copy-Item (Join-Path $RepoRoot "Dockerfile")    (Join-Path $Tmp "Dockerfile")    -Force
Copy-Item (Join-Path $RepoRoot ".dockerignore") (Join-Path $Tmp ".dockerignore") -Force
Copy-Item (Join-Path $RepoRoot "README_HF.md")  (Join-Path $Tmp "README.md")     -Force  # HF 靠 README 的 YAML 配置 Space
$dstBackend = Join-Path $Tmp "backend"
if (Test-Path $dstBackend) { Remove-Item $dstBackend -Recurse -Force }
Copy-Item (Join-Path $RepoRoot "backend") $dstBackend -Recurse -Force
$envFile = Join-Path $dstBackend ".env"
if (Test-Path $envFile) { Remove-Item $envFile -Force }   # 绝不上传本地密钥

Write-Host "==> 提交并推送"
Push-Location $Tmp
git add -A
# 若本次无改动，commit 会返回非零——这不是错误，照常推送即可
git -c user.email="deploy@local" -c user.name="deploy" commit -m "Deploy backend $(Get-Date -Format o)"
if ($LASTEXITCODE -ne 0) { Write-Host "   (无文件改动，跳过 commit)" }
$SpaceUrl = "https://$($HfUser):$($HfToken)@huggingface.co/spaces/$HfUser/$HfSpace"
git push $SpaceUrl HEAD:main
if ($LASTEXITCODE -ne 0) { Pop-Location; Write-Error "推送失败：检查 HfToken 是否为 Write 权限、Space 名是否正确"; exit 1 }
Pop-Location

Write-Host ""
Write-Host "[OK] 已推送。HF 会自动构建镜像（首次 2-4 分钟）。"
Write-Host "    构建日志: https://huggingface.co/spaces/$HfUser/$HfSpace?logs=build"
Write-Host "    别忘了在 Space 的 Settings -> Variables and secrets 里配置:"
Write-Host "       LLM_BACKEND=openai  (Variable)"
Write-Host "       OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai  (Variable)"
Write-Host "       OPENAI_MODEL=gemini-2.5-flash-lite  (Variable)"
Write-Host "       OPENAI_API_KEY=你的Gemini key  (Secret!)"
Write-Host "    后端地址: https://$HfUser-$HfSpace.hf.space"

Remove-Item $Tmp -Recurse -Force
