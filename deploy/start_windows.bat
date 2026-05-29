@echo off
chcp 65001 >nul
REM ============================================================
REM  二次元 AI 角色扮演 - Windows 本地一键启动 (DeepSeek 直连)
REM  双击本文件即可。手机连同一 WiFi 用打印出的地址访问。
REM ============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0\..\backend"

echo.
echo === [1/4] 检查 Python ===
where python >nul 2>nul
if errorlevel 1 (
  echo [错误] 没找到 Python。请先安装：https://www.python.org/downloads/
  echo        安装时务必勾选 "Add Python to PATH"
  pause & exit /b 1
)
python --version

echo.
echo === [2/4] 安装依赖 (首次较慢) ===
python -m pip install -q -r requirements.txt
if errorlevel 1 ( echo [错误] 依赖安装失败 & pause & exit /b 1 )

echo.
echo === [3/4] 检查配置 ===
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo [提示] 已创建 .env，但还没填 DeepSeek key。
  echo        请用记事本打开 backend\.env，填好这 4 行后重新运行：
  echo            LLM_BACKEND=openai
  echo            OPENAI_BASE_URL=https://api.deepseek.com/v1
  echo            OPENAI_MODEL=deepseek-chat
  echo            OPENAI_API_KEY=你的key（在 platform.deepseek.com 注册领取）
  echo.
  echo        现在先用 mock 模式启动（假数据，能看界面）。
)

REM 取局域网 IP（取第一个 192/10/172 段）
set LANIP=
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
  set ip=%%a
  set ip=!ip: =!
  echo !ip! | findstr /r "^192\.168\. ^10\. ^172\." >nul && if not defined LANIP set LANIP=!ip!
)
if not defined LANIP set LANIP=你的电脑IP

echo.
echo === [4/4] 启动后端 ===
echo.
echo   电脑本机访问：   http://localhost:8000
echo   手机访问(同WiFi)： http://!LANIP!:8000
echo.
echo   [重要] 首次启动若弹出 Windows 防火墙提示，请勾选"专用网络"并允许，
echo          否则手机连不上。
echo   [停止] 在本窗口按 Ctrl+C。
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
