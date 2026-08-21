@echo off
chcp 65001 >nul
echo ============================================================
echo   GILOS 获客系统 - GitHub 一键初始化并推送脚本
echo ============================================================
echo.

REM ----- 配置信息（请填入自己的） -----
set GITHUB_USER=YOUR_GITHUB_USERNAME
set GITHUB_TOKEN=YOUR_GITHUB_TOKEN
set REPO_NAME=huoke-system-gilos
set EMAIL=dev@huoke-system.local
set USER_NAME=GILOS Dev

REM 如果有 githubAPI.txt（格式：第1行用户名，第2行Token），自动读取它（优先使用）
if exist "%~dp0githubAPI.txt" (
    for /f "usebackq tokens=* delims=" %%a in ("%~dp0githubAPI.txt") do (
        if not defined __line1 (set "__line1=%%~a") else if not defined __line2 (set "__line2=%%~a")
    )
    if defined __line1 set "GITHUB_USER=%__line1:用户名：=%"
    if defined __line2 set "GITHUB_TOKEN=%__line2%"
    set "__line1=" & set "__line2="
)

cd /d "%~dp0"

echo [1/6] 检查 Git 是否安装...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Git，请先安装 Git：
    echo        下载地址：https://git-scm.com/download/win
    echo        安装完成后重新运行此脚本。
    pause
    exit /b 1
)
echo       Git 已安装：%git_version%
echo.

echo [2/6] 初始化 Git 仓库...
if exist .git (
    echo       已存在 .git 目录，跳过初始化。
) else (
    git init
    if %errorlevel% neq 0 ( echo [错误] git init 失败 & pause & exit /b 1 )
    echo       初始化完成。
)
echo.

echo [3/6] 配置用户名与邮箱...
git config user.name "%USER_NAME%"
git config user.email "%EMAIL%"
echo.

echo [4/6] 添加远程仓库 origin...
git remote remove origin >nul 2>&1
git remote add origin https://%GITHUB_USER%:%GITHUB_TOKEN%@github.com/%GITHUB_USER%/%REPO_NAME%.git
if %errorlevel% neq 0 (
    echo [错误] 远程仓库添加失败，请检查 Token 是否正确。
    pause
    exit /b 1
)
echo       远程地址：https://github.com/%GITHUB_USER%/%REPO_NAME%.git
echo.

echo [5/6] 添加所有文件并首次提交...
git add -A
git commit -m "chore: init GILOS v0.1 MVP - 后端 FastAPI + 前端 Vue3 + 9 平台 Mock + 全家桶搜索" >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 没有新文件需要提交（可能已经提交过）。
) else (
    echo       提交成功。
)
echo.

echo [6/6] 推送到 GitHub main 分支...
git branch -M main
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo [错误] 推送失败！
    echo   可能原因：
    echo     1. Token 过期或无效（去 https://github.com/settings/tokens 重新生成）
    echo     2. 网络问题（需要翻墙？）
    echo     3. 仓库已存在同名文件
    echo.
    echo   解决后重新运行本脚本即可。
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   ✅ 推送成功！
echo ============================================================
echo.
echo   仓库地址：https://github.com/%GITHUB_USER%/%REPO_NAME%
echo.
echo   后续开发（日常提交）：
echo     git add -A
echo     git commit -m "描述"
echo     git push
echo.
pause
