# config-manager 使用指南

## 🎯 功能

`config-manager` 命令用于管理 Supabase 中的配置，可以添加、修改、删除配置组和配置项。

## 🚀 快速开始

### 添加配置组

```powershell
# 添加新的配置组
config-manager add-group --name my_api --category api --description "我的 API 配置"
```

### 添加配置项

```powershell
# 添加普通配置项
config-manager add-item --group my_api --key API_URL --value "https://api.example.com"

# 添加敏感信息（会标记为 secret）
config-manager add-item --group my_api --key API_KEY --value "your-secret-key" --secret

# 添加数字类型
config-manager add-item --group my_api --key TIMEOUT --value "30" --type number

# 添加布尔类型
config-manager add-item --group my_api --key ENABLED --value "true" --type boolean
```

### 更新配置项

```powershell
# 更新配置值
config-manager update-item --group my_api --key API_KEY --value "new-key"

# 更新描述
config-manager update-item --group my_api --key API_URL --description "新的 API 地址"

# 标记为敏感信息
config-manager update-item --group my_api --key API_KEY --secret

# 取消敏感信息标记
config-manager update-item --group my_api --key API_URL --no-secret
```

### 删除配置项

```powershell
config-manager delete-item --group my_api --key API_KEY
```

### 查看配置

```powershell
# 列出所有配置组
config-manager list-groups

# 列出配置组的所有配置项
config-manager list-items --group my_api
```

## 📋 完整命令参考

### add-group - 添加配置组

```powershell
config-manager add-group \
  --name <组名> \
  --category <分类> \
  --description <描述> \
  --active
```

**示例：**
```powershell
config-manager add-group --name database --category db --description "数据库配置"
```

### add-item - 添加配置项

```powershell
config-manager add-item \
  --group <组名> \
  --key <键名> \
  --value <值> \
  --type <类型> \
  --description <描述> \
  --secret \
  --order <排序>
```

**参数说明：**
- `--group, -g`: 配置组名称（必需）
- `--key, -k`: 配置键名（必需）
- `--value, -v`: 配置值（必需）
- `--type, -t`: 值类型（string/number/boolean/json/array，默认：string）
- `--description, -d`: 描述
- `--secret`: 标记为敏感信息
- `--order, -o`: 排序索引（默认：0）

**示例：**
```powershell
# 添加字符串配置
config-manager add-item --group database --key DB_HOST --value "localhost"

# 添加敏感配置
config-manager add-item --group database --key DB_PASSWORD --value "secret123" --secret

# 添加数字配置
config-manager add-item --group database --key DB_PORT --value "5432" --type number --description "数据库端口"
```

### update-item - 更新配置项

```powershell
config-manager update-item \
  --group <组名> \
  --key <键名> \
  --value <新值> \
  --type <类型> \
  --description <描述> \
  --secret \
  --no-secret \
  --order <排序>
```

**示例：**
```powershell
# 更新值
config-manager update-item --group database --key DB_HOST --value "new-host"

# 更新描述
config-manager update-item --group database --key DB_HOST --description "新的数据库主机"

# 标记为敏感信息
config-manager update-item --group database --key DB_PASSWORD --secret
```

### delete-item - 删除配置项

```powershell
config-manager delete-item --group <组名> --key <键名>
```

**示例：**
```powershell
config-manager delete-item --group database --key OLD_KEY
```

### list-groups - 列出所有配置组

```powershell
config-manager list-groups
```

### list-items - 列出配置组的所有配置项

```powershell
config-manager list-items --group <组名>
```

**示例：**
```powershell
config-manager list-items --group database
```

## 💡 使用场景

### 场景 1: 添加新的 API 配置

```powershell
# 1. 创建配置组
config-manager add-group --name new_api --category api --description "新 API 配置"

# 2. 添加配置项
config-manager add-item --group new_api --key API_URL --value "https://api.example.com"
config-manager add-item --group new_api --key API_KEY --value "your-key" --secret
config-manager add-item --group new_api --key TIMEOUT --value "30" --type number

# 3. 验证
config-manager list-items --group new_api
```

### 场景 2: 更新现有配置

```powershell
# 更新 API Key
config-manager update-item --group my_api --key API_KEY --value "new-api-key"

# 更新描述
config-manager update-item --group my_api --key API_URL --description "更新后的 API 地址"
```

### 场景 3: 批量添加配置

```powershell
# 添加多个配置项
config-manager add-item --group redis --key REDIS_HOST --value "localhost" --order 1
config-manager add-item --group redis --key REDIS_PORT --value "6379" --type number --order 2
config-manager add-item --group redis --key REDIS_PASSWORD --value "password" --secret --order 3
```

## 🔒 敏感信息处理

使用 `--secret` 标记敏感配置：

```powershell
# 添加敏感配置
config-manager add-item --group api --key SECRET_KEY --value "secret-value" --secret

# 查看时敏感信息会显示为 ***HIDDEN***
config-manager list-items --group api
```

## 📝 数据类型

支持的数据类型：

- `string` - 字符串（默认）
- `number` - 数字
- `boolean` - 布尔值（true/false）
- `json` - JSON 对象
- `array` - 数组

**示例：**
```powershell
# 字符串
config-manager add-item --group config --key NAME --value "My App" --type string

# 数字
config-manager add-item --group config --key PORT --value "8080" --type number

# 布尔值
config-manager add-item --group config --key DEBUG --value "true" --type boolean

# JSON
config-manager add-item --group config --key SETTINGS --value '{"key":"value"}' --type json

# 数组
config-manager add-item --group config --key TAGS --value '["tag1","tag2"]' --type array
```

## 🎯 工作流程

```
1. 创建配置组（如果需要）
   config-manager add-group --name my_group

2. 添加配置项
   config-manager add-item --group my_group --key KEY1 --value VALUE1

3. 查看配置
   config-manager list-items --group my_group

4. 更新配置（如果需要）
   config-manager update-item --group my_group --key KEY1 --value NEW_VALUE

5. 使用 cloud-config 导出
   cloud-config --group my_group
```

## 💡 最佳实践

1. **先创建配置组**: 在添加配置项之前先创建配置组
2. **使用描述**: 为配置项添加清晰的描述，方便理解
3. **标记敏感信息**: 使用 `--secret` 标记 API Key、密码等敏感信息
4. **合理排序**: 使用 `--order` 参数控制配置项的显示顺序
5. **定期备份**: 使用 `cloud-config` 导出配置作为备份

## 🔍 常见问题

### 问题：配置组不存在

**错误**: `❌ 配置组 'xxx' 不存在，请先创建`

**解决**: 先创建配置组
```powershell
config-manager add-group --name xxx --category api
```

### 问题：配置项已存在

**错误**: 添加配置项时提示已存在

**解决**: 使用 `update-item` 更新，或先删除再添加
```powershell
config-manager update-item --group xxx --key KEY --value NEW_VALUE
```

## 📚 相关命令

- `cloud-config` - 导出配置为 JSON
- `project-config` - 保存项目信息
- `config-manager` - 管理云端配置

