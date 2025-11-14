@echo off
chcp 65001 >nul
echo 初始化 Git 仓库...
git init

echo 添加文件...
git add .

echo 提交...
git commit -m "Initial commit: Cloud Config Tools"

echo 创建 GitHub 仓库...
gh repo create cloud-config-tools --public --source=. --remote=origin --push

echo 完成！
pause

