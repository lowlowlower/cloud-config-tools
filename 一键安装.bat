@echo off
chcp 65001 >nul
echo ========================================
echo 一键安装 cloud-config 命令
echo ========================================
echo.

echo [1/4] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python 已安装

echo.
echo [2/4] 安装依赖库...
python -m pip install --upgrade pip -q
python -m pip install requests supabase -q
if errorlevel 1 (
    echo ⚠️ 安装依赖失败，尝试继续...
) else (
    echo ✅ 依赖库已安装
)

echo.
echo [3/4] 安装工具到系统目录...
set TOOLS_DIR=%USERPROFILE%\tools\supabase-tools
if not exist "%TOOLS_DIR%" mkdir "%TOOLS_DIR%"

REM 复制 cloud_config_reader.py
if exist "cloud_config_reader.py" (
    copy "cloud_config_reader.py" "%TOOLS_DIR%\" >nul
    echo ✅ 已复制 cloud_config_reader.py
) else (
    echo ❌ 未找到 cloud_config_reader.py
    echo 请确保在项目目录中运行此脚本
    pause
    exit /b 1
)

REM 创建启动脚本
(
echo @echo off
echo python "%%~dp0cloud_config_reader.py" %%*
) > "%TOOLS_DIR%\cloud-config.bat"
echo ✅ 已创建 cloud-config.bat

REM 复制 project_config.py
if exist "project_config.py" (
    copy "project_config.py" "%TOOLS_DIR%\" >nul
    echo ✅ 已复制 project_config.py
)

REM 创建 project-config.bat
(
echo @echo off
echo python "%%~dp0project_config.py" %%*
) > "%TOOLS_DIR%\project-config.bat"
echo ✅ 已创建 project-config.bat

echo.
echo [4/4] 配置 PATH 环境变量...
powershell -Command "$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($currentPath -notlike '*%TOOLS_DIR%*') { [Environment]::SetEnvironmentVariable('Path', $currentPath + ';%TOOLS_DIR%', 'User'); Write-Host '✅ PATH 已配置' } else { Write-Host '✅ PATH 已包含工具目录' }"

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo ⚠️ 重要提示:
echo 1. 请重启终端（关闭并重新打开）
echo 2. 重启后可以使用以下命令:
echo    cloud-config          - 导出云端配置
echo    project-config        - 保存项目信息
echo.
echo 如果不想重启，可以临时使用:
echo   %TOOLS_DIR%\cloud-config.bat
echo   %TOOLS_DIR%\project-config.bat
echo.
pause

