# project-config 使用指南

## 🎯 功能

`project-config` 命令用于将当前项目信息保存到 Supabase 的 `project_info` 表中。

## 🚀 快速开始

### 基本用法

```powershell
# 保存当前项目信息
project-config

# 保存指定项目
project-config --path D:\github\my-project

# 添加描述和标签
project-config --description "我的 Python 项目" --tags python,web,api

# 指定项目类型
project-config --type python

# 列出所有已保存的项目
project-config --list
```

## 📋 自动检测的信息

脚本会自动检测以下信息：

- **项目名称**: 使用目录名
- **项目路径**: 完整路径
- **项目类型**: 根据项目文件自动检测
  - `package.json` → nodejs
  - `requirements.txt` / `setup.py` → python
  - `Cargo.toml` → rust
  - `go.mod` → go
  - `pom.xml` → java
  - `composer.json` → php
  - `Gemfile` → ruby
  - `.csproj` → dotnet
- **Git 仓库**: 自动检测 Git 远程仓库 URL
- **最后打开时间**: 自动更新

## 💡 使用示例

### 示例 1: 保存当前项目

```powershell
# 在项目目录中运行
cd D:\github\my-project
project-config
```

输出：
```
✅ 项目信息已保存: my-project

项目 ID: 123
项目路径: D:\github\my-project
```

### 示例 2: 添加详细信息

```powershell
project-config \
  --description "图片处理工具" \
  --tags python,image-processing,supabase \
  --type python
```

### 示例 3: 更新已存在的项目

```powershell
# 如果项目已存在，默认会更新
project-config --description "更新后的描述"

# 如果不想更新，使用 --no-update
project-config --no-update
```

### 示例 4: 列出所有项目

```powershell
project-config --list
```

输出：
```
📋 项目列表 (共 3 个):

  [my-project]
    路径: D:\github\my-project
    类型: python
    Git: https://github.com/user/my-project.git
    描述: 图片处理工具

  [another-project]
    路径: D:\github\another-project
    类型: nodejs
    Git: https://github.com/user/another-project.git
```

## 🔧 数据库表结构

项目信息保存在 `project_info` 表中：

```sql
CREATE TABLE project_info (
    id bigserial PRIMARY KEY,
    project_name text NOT NULL,
    project_path text NOT NULL,
    project_type text,
    git_repo text,
    description text,
    tags text[],
    last_opened timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
```

## 📝 完整参数说明

```powershell
project-config [选项]

选项:
  --path, -p PATH        项目路径（默认：当前目录）
  --name, -n NAME        项目名称（默认：目录名）
  --description, -d DESC 项目描述
  --tags, -t TAGS        标签（逗号分隔，如：python,web,api）
  --type TYPE            项目类型（如：python, nodejs, rust）
  --list, -l             列出所有项目
  --update               如果项目已存在则更新（默认：True）
  --no-update            如果项目已存在则不更新
```

## 🎯 工作流程

```
1. 检测当前项目信息
   ├─ 项目路径
   ├─ 项目名称
   ├─ Git 仓库信息
   └─ 项目类型

2. 检查数据库
   └─ 根据 project_path 查找是否已存在

3. 保存或更新
   ├─ 如果不存在 → 插入新记录
   └─ 如果已存在 → 更新记录（默认）

4. 返回结果
   └─ 显示项目 ID 和路径
```

## 💡 最佳实践

1. **在项目根目录运行**: 确保能正确检测 Git 信息和项目类型
2. **添加描述和标签**: 方便后续查找和管理
3. **定期更新**: 每次打开项目时运行，更新 `last_opened` 时间
4. **使用标签**: 用标签分类项目（如：work, personal, python, web）

## 🔍 常见问题

### 问题：Git 信息未检测到

**原因**: 项目不是 Git 仓库，或 Git 未安装

**解决**: 
- 确保项目已初始化 Git: `git init`
- 确保已安装 Git 并添加到 PATH

### 问题：项目类型未检测到

**解决**: 使用 `--type` 参数手动指定

### 问题：项目已存在但想创建新记录

**解决**: 使用 `--no-update` 参数（但会报错，因为 project_path 是唯一的）

## 📚 相关命令

- `cloud-config` - 导出云端配置
- `project-config` - 保存项目信息



