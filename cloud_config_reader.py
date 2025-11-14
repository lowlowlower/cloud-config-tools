#!/usr/bin/env python3
"""
云端配置读取器
从 Supabase 读取配置，支持通过 path 命令直接执行
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

# 如果 supabase 库有问题，使用 requests 直接调用 REST API
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class CloudConfigReader:
    """云端配置读取器"""
    
    # 硬编码的默认配置（优先级最低）
    DEFAULT_SUPABASE_URL = "https://yjeeaegldbsyslnlbesr.supabase.co"
    DEFAULT_SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlqZWVhZWdsZGJzeXNsbmxiZXNyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5NzUxODQsImV4cCI6MjA3MjU1MTE4NH0.b4rK2iCdX6uissLqeZep_oW1G0aTROpacfUug59PrSI"
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        初始化配置读取器
        
        配置读取优先级（从高到低）:
        1. 传入参数
        2. 环境变量 (SUPABASE_URL, SUPABASE_KEY)
        3. 硬编码默认值（DEFAULT_SUPABASE_URL, DEFAULT_SUPABASE_KEY）
        4. 本地配置文件 (config.py)
        
        Args:
            supabase_url: Supabase URL（如果为 None，按优先级自动查找）
            supabase_key: Supabase Key（如果为 None，按优先级自动查找）
        """
        self.supabase_url = supabase_url or self._get_supabase_url()
        self.supabase_key = supabase_key or self._get_supabase_key()
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ 错误: 未设置 Supabase URL 或 Key")
        
        # 创建 Supabase 客户端或使用 REST API
        self.client = None
        self.use_rest_api = False
        
        # 尝试使用 supabase 库
        if HAS_SUPABASE:
            try:
                # 方法1: 位置参数
                self.client = create_client(self.supabase_url, self.supabase_key)
            except (TypeError, Exception) as e:
                error_msg = str(e)
                if "proxy" in error_msg or "unexpected keyword" in error_msg:
                    # supabase 库有兼容性问题，改用 REST API
                    if HAS_REQUESTS:
                        self.use_rest_api = True
                        print("⚠️ supabase 库有兼容性问题，改用 REST API 方式", file=sys.stderr)
                    else:
                        raise ValueError(
                            f"❌ supabase 库兼容性问题，且未安装 requests 库\n"
                            f"请运行: pip install requests\n"
                            f"或升级 supabase: pip install --upgrade supabase"
                        )
                else:
                    raise ValueError(f"❌ 创建 Supabase 客户端失败: {error_msg}")
        else:
            # 没有 supabase 库，使用 REST API
            if HAS_REQUESTS:
                self.use_rest_api = True
            else:
                raise ValueError(
                    "❌ 未安装 supabase 或 requests 库\n"
                    "请运行: pip install supabase 或 pip install requests"
                )
    
    def _get_supabase_url(self) -> Optional[str]:
        """
        获取 Supabase URL
        
        优先级顺序:
        1. 环境变量 SUPABASE_URL
        2. 硬编码默认值 DEFAULT_SUPABASE_URL
        3. 本地配置文件 config.py 中的 SUPABASE_URL
        """
        # 1. 从环境变量读取
        url = os.getenv("SUPABASE_URL")
        if url:
            return url
        
        # 2. 使用硬编码默认值
        if self.DEFAULT_SUPABASE_URL:
            return self.DEFAULT_SUPABASE_URL
        
        # 3. 从本地配置文件读取
        try:
            # 尝试导入本地配置
            sys.path.insert(0, str(Path(__file__).parent))
            from config import SUPABASE_URL
            return SUPABASE_URL
        except ImportError:
            pass
        
        return None
    
    def _get_supabase_key(self) -> Optional[str]:
        """
        获取 Supabase Key
        
        优先级顺序:
        1. 环境变量 SUPABASE_KEY
        2. 硬编码默认值 DEFAULT_SUPABASE_KEY
        3. 本地配置文件 config.py 中的 SUPABASE_KEY
        """
        # 1. 从环境变量读取
        key = os.getenv("SUPABASE_KEY")
        if key:
            return key
        
        # 2. 使用硬编码默认值
        if self.DEFAULT_SUPABASE_KEY:
            return self.DEFAULT_SUPABASE_KEY
        
        # 3. 从本地配置文件读取
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from config import SUPABASE_KEY
            return SUPABASE_KEY
        except ImportError:
            pass
        
        return None
    
    def _rest_api_query(self, table: str, select: str = "*", filters: Dict = None, order: str = None) -> List[Dict]:
        """使用 REST API 查询数据（PostgREST 格式）"""
        url = f"{self.supabase_url}/rest/v1/{table}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        params = {"select": select}
        
        # PostgREST 格式：name=eq.value 或 is_active=eq.true
        if filters:
            for key, value in filters.items():
                # 处理布尔值
                if isinstance(value, bool):
                    value = str(value).lower()
                elif value == "true" or value == "false":
                    value = value.lower()
                params[key] = f"eq.{value}"
        
        if order:
            params["order"] = order
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_config_group(self, group_name: str, environment: str = "default") -> Dict[str, Any]:
        """
        获取配置组的所有配置项
        
        Args:
            group_name: 配置组名称
            environment: 环境名称（默认：default）
        
        Returns:
            配置字典，键为配置项名称，值为配置值
        """
        try:
            if self.use_rest_api:
                # 使用 REST API
                groups = self._rest_api_query(
                    "config_groups",
                    select="id,name,category",
                    filters={"name": group_name, "is_active": True}
                )
                
                if not groups:
                    raise ValueError(f"❌ 配置组 '{group_name}' 不存在或未激活")
                
                group_id = groups[0]["id"]
                
                # 查询配置项
                items = self._rest_api_query(
                    "config_items",
                    select="key,value,value_type",
                    filters={"group_id": group_id},
                    order="order_index,key"
                )
            else:
                # 使用 supabase 客户端
                group_response = self.client.table("config_groups")\
                    .select("id, name, category")\
                    .eq("name", group_name)\
                    .eq("is_active", True)\
                    .execute()
                
                if not group_response.data:
                    raise ValueError(f"❌ 配置组 '{group_name}' 不存在或未激活")
                
                group_id = group_response.data[0]["id"]
                
                items_response = self.client.table("config_items")\
                    .select("key, value, value_type")\
                    .eq("group_id", group_id)\
                    .order("order_index, key")\
                .execute()
                
                items = items_response.data
            
            config = {}
            for item in items:
                key = item["key"]
                value = item["value"]
                value_type = item.get("value_type", "string")
                
                # 根据类型转换值
                if value_type == "number":
                    try:
                        value = int(value) if "." not in value else float(value)
                    except ValueError:
                        pass
                elif value_type == "boolean":
                    value = value.lower() in ("true", "1", "yes", "on")
                elif value_type == "json":
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                elif value_type == "array":
                    try:
                        value = json.loads(value) if isinstance(value, str) else value
                    except json.JSONDecodeError:
                        value = [value]
                
                config[key] = value
            
            return config
        
        except Exception as e:
            raise Exception(f"❌ 读取配置失败: {str(e)}")
    
    def get_all_configs(self, environment: str = "default") -> Dict[str, Dict[str, Any]]:
        """
        获取所有配置组
        
        Args:
            environment: 环境名称（默认：default）
        
        Returns:
            配置字典，键为配置组名称，值为配置项字典
        """
        try:
            if self.use_rest_api:
                # 使用 REST API
                groups = self._rest_api_query(
                    "config_groups",
                    select="id,name,category",
                    filters={"is_active": True},
                    order="category,name"
                )
            else:
                # 使用 supabase 客户端
                groups_response = self.client.table("config_groups")\
                    .select("id, name, category")\
                    .eq("is_active", True)\
                    .execute()
                groups = groups_response.data
            
            all_configs = {}
            for group in groups:
                group_name = group["name"]
                try:
                    all_configs[group_name] = self.get_config_group(group_name, environment)
                except Exception as e:
                    print(f"⚠️ 跳过配置组 '{group_name}': {str(e)}", file=sys.stderr)
            
            return all_configs
        
        except Exception as e:
            raise Exception(f"❌ 读取所有配置失败: {str(e)}")
    
    def list_groups(self) -> List[Dict[str, Any]]:
        """列出所有配置组"""
        try:
            if self.use_rest_api:
                # 使用 REST API
                return self._rest_api_query(
                    "config_groups",
                    select="name,description,category,is_active",
                    filters={"is_active": True},
                    order="category,name"
                )
            else:
                # 使用 supabase 客户端
                response = self.client.table("config_groups")\
                    .select("name, description, category, is_active")\
                    .eq("is_active", True)\
                    .order("category, name")\
                    .execute()
                return response.data
        
        except Exception as e:
            raise Exception(f"❌ 列出配置组失败: {str(e)}")


def export_all_to_json(output_file="config.json"):
    """导出所有配置为 JSON 文件"""
    try:
        reader = CloudConfigReader()
        all_configs = reader.get_all_configs()
        
        # 构建完整的配置结构
        result = {}
        for group_name, config in all_configs.items():
            # 获取配置组信息
            groups = reader.list_groups()
            group_info = next((g for g in groups if g['name'] == group_name), {})
            
            result[group_name] = {
                "category": group_info.get("category"),
                "description": group_info.get("description"),
                "config": config
            }
        
        # 保存为 JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置已导出到: {output_file}")
        print(f"   共 {len(result)} 个配置组")
        return True
    
    except Exception as e:
        print(f"❌ 导出配置失败: {str(e)}")
        return False


def main():
    """命令行工具 - 简化版：直接导出 JSON 配置"""
    parser = argparse.ArgumentParser(
        description="云端配置导出工具 - 从 Supabase 导出配置为 JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 导出所有配置为 config.json
  cloud-config
  
  # 导出到指定文件
  cloud-config --output my_config.json
  
  # 导出指定配置组
  cloud-config --group path_config
        """
    )
    
    parser.add_argument(
        "--output", "-o",
        default="config.json",
        help="输出文件路径（默认：config.json）"
    )
    parser.add_argument(
        "--group", "-g",
        help="只导出指定配置组（如：path_config, supabase）"
    )
    
    args = parser.parse_args()
    
    try:
        reader = CloudConfigReader()
        
        if args.group:
            # 导出单个配置组
            config = reader.get_config_group(args.group)
            groups = reader.list_groups()
            group_info = next((g for g in groups if g['name'] == args.group), {})
            
            result = {
                args.group: {
                    "category": group_info.get("category"),
                    "description": group_info.get("description"),
                    "config": config
                }
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置组 '{args.group}' 已导出到: {args.output}")
        else:
            # 导出所有配置
            export_all_to_json(args.output)
    
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

