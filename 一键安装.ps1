# PowerShell 一键安装脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "一键安装 cloud-config 命令" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "[1/4] 检查 Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 未找到 Python，请先安装 Python" -ForegroundColor Red
    Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "按 Enter 退出"
    exit 1
}

# 安装依赖
Write-Host ""
Write-Host "[2/4] 安装依赖库..." -ForegroundColor Yellow
python -m pip install --upgrade pip -q
python -m pip install requests supabase -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 依赖库已安装" -ForegroundColor Green
} else {
    Write-Host "⚠️ 安装依赖可能失败，尝试继续..." -ForegroundColor Yellow
}

# 安装工具
Write-Host ""
Write-Host "[3/4] 安装工具到系统目录..." -ForegroundColor Yellow
$toolsDir = Join-Path $env:USERPROFILE "tools\supabase-tools"

if (-not (Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
}

# 复制文件
$sourceFile = Join-Path $PSScriptRoot "cloud_config_reader.py"
if (Test-Path $sourceFile) {
    Copy-Item $sourceFile "$toolsDir\cloud_config_reader.py" -Force
    Write-Host "✅ 已复制 cloud_config_reader.py" -ForegroundColor Green
} else {
    Write-Host "❌ 未找到 cloud_config_reader.py" -ForegroundColor Red
    Write-Host "请确保在项目目录中运行此脚本" -ForegroundColor Yellow
    Read-Host "按 Enter 退出"
    exit 1
}

# 创建启动脚本
$batContent = @"
@echo off
python "%~dp0cloud_config_reader.py" %*
"@
$batContent | Out-File -FilePath "$toolsDir\cloud-config.bat" -Encoding ASCII -NoNewline
Write-Host "✅ 已创建 cloud-config.bat" -ForegroundColor Green

# 配置 PATH
Write-Host ""
Write-Host "[4/4] 配置 PATH 环境变量..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$toolsDir*") {
    $newPath = $currentPath + ";$toolsDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "✅ PATH 已配置" -ForegroundColor Green
} else {
    Write-Host "✅ PATH 已包含工具目录" -ForegroundColor Green
}

# 更新当前会话的 PATH
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User")

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "工具目录: $toolsDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️ 重要提示:" -ForegroundColor Yellow
Write-Host "1. 请重启终端（关闭并重新打开）" -ForegroundColor White
Write-Host "2. 重启后运行: cloud-config" -ForegroundColor White
Write-Host ""
Write-Host "如果不想重启，可以临时使用:" -ForegroundColor Yellow
Write-Host "  & `"$toolsDir\cloud-config.bat`"" -ForegroundColor White
Write-Host ""
Read-Host "按 Enter 退出"

