-- ========================================
-- 云端配置存储表结构
-- 在 Supabase SQL Editor 中执行此文件来创建配置表
-- ========================================

-- 配置组表：用于组织不同类型的配置（如：项目配置、API配置等）
CREATE TABLE IF NOT EXISTS config_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE, -- 配置组名称（如：'image_processing', 'api_keys'）
    description TEXT, -- 配置组描述
    category TEXT, -- 分类（如：'supabase', 'api', 'worker', 'redis'）
    is_active BOOLEAN DEFAULT true, -- 是否激活
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 配置项表：存储具体的配置键值对
CREATE TABLE IF NOT EXISTS config_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES config_groups(id) ON DELETE CASCADE,
    key TEXT NOT NULL, -- 配置键（如：'SUPABASE_URL', 'GEMINI_API_KEY_1'）
    value TEXT NOT NULL, -- 配置值（敏感信息应加密存储）
    value_type TEXT DEFAULT 'string', -- 值类型：string, number, boolean, json, array
    description TEXT, -- 配置项描述
    is_encrypted BOOLEAN DEFAULT false, -- 是否为加密值
    is_secret BOOLEAN DEFAULT false, -- 是否为敏感信息（用于显示时隐藏）
    order_index INTEGER DEFAULT 0, -- 排序索引
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(group_id, key) -- 同一组内键名唯一
);

-- 配置环境表：用于区分不同环境（开发、测试、生产等）
CREATE TABLE IF NOT EXISTS config_environments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE, -- 环境名称（如：'dev', 'prod', 'test'）
    description TEXT,
    is_default BOOLEAN DEFAULT false, -- 是否为默认环境
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 环境配置关联表：将配置组关联到特定环境
CREATE TABLE IF NOT EXISTS environment_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    environment_id UUID REFERENCES config_environments(id) ON DELETE CASCADE,
    group_id UUID REFERENCES config_groups(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(environment_id, group_id)
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_config_items_group_id ON config_items(group_id);
CREATE INDEX IF NOT EXISTS idx_config_items_key ON config_items(key);
CREATE INDEX IF NOT EXISTS idx_config_groups_category ON config_groups(category);
CREATE INDEX IF NOT EXISTS idx_config_groups_is_active ON config_groups(is_active);
CREATE INDEX IF NOT EXISTS idx_environment_configs_env_id ON environment_configs(environment_id);
CREATE INDEX IF NOT EXISTS idx_environment_configs_group_id ON environment_configs(group_id);

-- 更新 updated_at 的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为表添加触发器
DROP TRIGGER IF EXISTS update_config_groups_updated_at ON config_groups;
CREATE TRIGGER update_config_groups_updated_at
    BEFORE UPDATE ON config_groups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_config_items_updated_at ON config_items;
CREATE TRIGGER update_config_items_updated_at
    BEFORE UPDATE ON config_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 初始化默认环境
-- ========================================
INSERT INTO config_environments (name, description, is_default)
VALUES ('default', '默认环境', true)
ON CONFLICT (name) DO NOTHING;

-- ========================================
-- 示例：插入配置组和配置项
-- ========================================

-- 插入 Supabase 配置组
INSERT INTO config_groups (name, description, category, is_active)
VALUES 
    ('supabase', 'Supabase 数据库配置', 'supabase', true),
    ('gemini_api', 'Gemini API 密钥配置', 'api', true),
    ('redis', 'Redis 消息队列配置', 'redis', true),
    ('worker', 'Worker 工作节点配置', 'worker', true),
    ('image_processing', '图片处理相关配置', 'processing', true),
    ('path_config', 'PATH 环境变量配置', 'system', true)
ON CONFLICT (name) DO NOTHING;

-- 插入 Supabase 配置项（示例，请替换为实际值）
INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'SUPABASE_URL',
    'https://yjeeaegldbsyslnlbesr.supabase.co',
    'string',
    'Supabase 项目 URL',
    false,
    1
FROM config_groups g WHERE g.name = 'supabase'
ON CONFLICT (group_id, key) DO NOTHING;

INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'SUPABASE_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlqZWVhZWdsZGJzeXNsbmxiZXNyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5NzUxODQsImV4cCI6MjA3MjU1MTE4NH0.b4rK2iCdX6uissLqeZep_oW1G0aTROpacfUug59PrSI',
    'string',
    'Supabase Anon Key',
    true,
    2
FROM config_groups g WHERE g.name = 'supabase'
ON CONFLICT (group_id, key) DO NOTHING;

-- 插入 Gemini API 配置项（示例）
INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'GEMINI_API_KEY_1',
    'YOUR_GEMINI_API_KEY_1',
    'string',
    'Gemini API Key 1',
    true,
    1
FROM config_groups g WHERE g.name = 'gemini_api'
ON CONFLICT (group_id, key) DO NOTHING;

INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'GEMINI_API_KEY_2',
    'YOUR_GEMINI_API_KEY_2',
    'string',
    'Gemini API Key 2',
    true,
    2
FROM config_groups g WHERE g.name = 'gemini_api'
ON CONFLICT (group_id, key) DO NOTHING;

-- 插入 Redis 配置项
INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'REDIS_URL',
    'redis://localhost:6379/0',
    'string',
    'Redis 连接 URL',
    false,
    1
FROM config_groups g WHERE g.name = 'redis'
ON CONFLICT (group_id, key) DO NOTHING;

-- 插入 Worker 配置项
INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'WORKER_ID_PREFIX',
    'worker',
    'string',
    'Worker ID 前缀',
    false,
    1
FROM config_groups g WHERE g.name = 'worker'
ON CONFLICT (group_id, key) DO NOTHING;

INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'HEARTBEAT_INTERVAL',
    '30',
    'number',
    '心跳间隔（秒）',
    false,
    2
FROM config_groups g WHERE g.name = 'worker'
ON CONFLICT (group_id, key) DO NOTHING;

INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'TASK_POLL_INTERVAL',
    '5',
    'number',
    '任务轮询间隔（秒）',
    false,
    3
FROM config_groups g WHERE g.name = 'worker'
ON CONFLICT (group_id, key) DO NOTHING;

-- 插入图片处理配置项
INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'OUTPUT_DIR',
    'processed_images',
    'string',
    '处理后的图片输出目录',
    false,
    1
FROM config_groups g WHERE g.name = 'image_processing'
ON CONFLICT (group_id, key) DO NOTHING;

INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'MAX_RETRIES',
    '3',
    'number',
    '任务最大重试次数',
    false,
    2
FROM config_groups g WHERE g.name = 'image_processing'
ON CONFLICT (group_id, key) DO NOTHING;

INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'TASK_TIMEOUT',
    '300',
    'number',
    '任务超时时间（秒）',
    false,
    3
FROM config_groups g WHERE g.name = 'image_processing'
ON CONFLICT (group_id, key) DO NOTHING;

-- 插入 PATH 配置项
INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'TOOLS_DIR',
    '%USERPROFILE%\\tools\\supabase-tools',
    'string',
    '工具目录路径（Windows）',
    false,
    1
FROM config_groups g WHERE g.name = 'path_config'
ON CONFLICT (group_id, key) DO NOTHING;

INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'TOOLS_DIR_LINUX',
    '$HOME/tools/supabase-tools',
    'string',
    '工具目录路径（Linux/Mac）',
    false,
    2
FROM config_groups g WHERE g.name = 'path_config'
ON CONFLICT (group_id, key) DO NOTHING;

INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'SETUP_SCRIPT_WINDOWS',
    'setup_path.bat',
    'string',
    'Windows PATH 配置脚本',
    false,
    3
FROM config_groups g WHERE g.name = 'path_config'
ON CONFLICT (group_id, key) DO NOTHING;

INSERT INTO config_items (group_id, key, value, value_type, description, is_secret, order_index)
SELECT 
    g.id,
    'SETUP_SCRIPT_LINUX',
    'setup_path.sh',
    'string',
    'Linux/Mac PATH 配置脚本',
    false,
    4
FROM config_groups g WHERE g.name = 'path_config'
ON CONFLICT (group_id, key) DO NOTHING;

-- 将配置组关联到默认环境
INSERT INTO environment_configs (environment_id, group_id, is_active)
SELECT 
    e.id,
    g.id,
    true
FROM config_environments e, config_groups g
WHERE e.name = 'default' AND g.is_active = true
ON CONFLICT (environment_id, group_id) DO NOTHING;

-- ========================================
-- 查询视图：方便查看配置
-- ========================================

-- 创建配置视图：显示所有配置组及其配置项
CREATE OR REPLACE VIEW config_view AS
SELECT 
    cg.id as group_id,
    cg.name as group_name,
    cg.category,
    cg.description as group_description,
    ci.id as item_id,
    ci.key,
    CASE 
        WHEN ci.is_secret THEN '***HIDDEN***'
        ELSE ci.value
    END as value,
    ci.value_type,
    ci.description as item_description,
    ci.is_secret,
    ci.order_index,
    ci.created_at,
    ci.updated_at
FROM config_groups cg
LEFT JOIN config_items ci ON cg.id = ci.group_id
WHERE cg.is_active = true
ORDER BY cg.name, ci.order_index, ci.key;

-- 创建环境配置视图：显示特定环境的所有配置
CREATE OR REPLACE VIEW environment_config_view AS
SELECT 
    e.name as environment_name,
    cg.name as group_name,
    cg.category,
    ci.key,
    CASE 
        WHEN ci.is_secret THEN '***HIDDEN***'
        ELSE ci.value
    END as value,
    ci.value_type,
    ci.description
FROM config_environments e
JOIN environment_configs ec ON e.id = ec.environment_id
JOIN config_groups cg ON ec.group_id = cg.id
LEFT JOIN config_items ci ON cg.id = ci.group_id
WHERE ec.is_active = true AND cg.is_active = true
ORDER BY e.name, cg.name, ci.order_index, ci.key;

