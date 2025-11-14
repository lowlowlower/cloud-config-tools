# Cloud Config Tools

一个简单的云端配置管理工具，从 Supabase 数据库导出配置为 JSON 文件。

## 🚀 快速开始

### 3步完成安装

1. **下载项目**
   ```bash
   git clone <repository-url>
   cd cloud-config-tools
   ```

2. **运行安装脚本**
   ```
   双击运行: 一键安装.bat
   ```
   或 PowerShell:
   ```powershell
   .\一键安装.ps1
   ```

3. **重启终端并使用**
   ```powershell
   cloud-config
   ```

## 📋 使用方法

### cloud-config - 导出云端配置

```powershell
# 导出所有配置为 config.json
cloud-config

# 导出到指定文件
cloud-config --output my_config.json

# 只导出指定配置组
cloud-config --group path_config
```

### project-config - 保存项目信息

```powershell
# 保存当前项目信息到数据库
project-config

# 保存指定项目
project-config --path D:\github\my-project

# 添加描述和标签
project-config --description "我的项目" --tags python,web,api

# 列出所有项目
project-config --list
```

### config-manager - 管理云端配置

#### 图形界面版本（推荐）✨

```powershell
# 打开图形界面
config-manager-gui
```

图形界面功能：
- 📋 左侧显示所有配置组列表
- 📊 右侧显示选中配置组的配置项表格
- ➕ 添加配置组/配置项
- ✏️ 编辑配置项（双击或点击编辑按钮）
- 🗑️ 删除配置项
- 🔄 刷新数据

#### 命令行版本

```powershell
# 添加配置组
config-manager add-group --name my_api --category api --description "我的 API 配置"

# 添加配置项
config-manager add-item --group my_api --key API_KEY --value "your-key" --secret

# 更新配置项
config-manager update-item --group my_api --key API_KEY --value "new-key"

# 删除配置项
config-manager delete-item --group my_api --key API_KEY

# 列出所有配置组
config-manager list-groups

# 列出配置组的所有配置项
config-manager list-items --group my_api
```

## 📁 项目结构

```
cloud-config-tools/
├── cloud_config_reader.py    # 配置导出脚本（cloud-config）
├── project_config.py         # 项目信息脚本（project-config）
├── config_manager.py         # 配置管理脚本（config-manager）
├── cloud_config_schema.sql   # 数据库表结构
├── 一键安装.bat              # Windows 安装脚本
├── 一键安装.ps1              # PowerShell 安装脚本
├── requirements.txt          # Python 依赖
└── README.md                 # 说明文档
```

## 🔧 依赖

- Python 3.7+
- requests
- supabase (可选，如果失败会自动使用 REST API)

## 📝 数据库设置

1. 在 Supabase Dashboard 中打开 SQL Editor
2. 执行 `cloud_config_schema.sql` 创建表结构
3. 配置你的配置项

## 💡 特性

- ✅ 一键安装，无需手动配置
- ✅ 自动兼容处理（支持 REST API 备选方案）
- ✅ 简单易用，直接导出 JSON
- ✅ 支持导出全部或单个配置组

## 📚 更多信息

查看 `新电脑快速配置.md` 获取详细说明。

