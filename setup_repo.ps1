# 设置 Git 仓库并推送到 GitHub
$ErrorActionPreference = "Stop"

Write-Host "初始化 Git 仓库..." -ForegroundColor Yellow
git init

Write-Host "添加文件..." -ForegroundColor Yellow
git add .

Write-Host "提交..." -ForegroundColor Yellow
git commit -m "Initial commit: Cloud Config Tools - 一键安装云端配置管理工具"

Write-Host "创建 GitHub 仓库..." -ForegroundColor Yellow
gh repo create cloud-config-tools --public --source=. --remote=origin --push

Write-Host "完成！" -ForegroundColor Green

