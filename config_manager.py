#!/usr/bin/env python3
"""
配置管理工具
用于添加、修改、删除 Supabase 中的配置
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional, Any

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class ConfigManager:
    """配置管理器"""
    
    # 硬编码的默认配置
    DEFAULT_SUPABASE_URL = "https://yjeeaegldbsyslnlbesr.supabase.co"
    DEFAULT_SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlqZWVhZWdsZGJzeXNsbmxiZXNyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5NzUxODQsImV4cCI6MjA3MjU1MTE4NH0.b4rK2iCdX6uissLqeZep_oW1G0aTROpacfUug59PrSI"
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """初始化管理器"""
        self.supabase_url = supabase_url or self.DEFAULT_SUPABASE_URL
        self.supabase_key = supabase_key or self.DEFAULT_SUPABASE_KEY
        
        # 创建 Supabase 客户端或使用 REST API
        self.client = None
        self.use_rest_api = False
        
        if HAS_SUPABASE:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
            except (TypeError, Exception) as e:
                error_msg = str(e)
                if "proxy" in error_msg or "unexpected keyword" in error_msg:
                    if HAS_REQUESTS:
                        self.use_rest_api = True
                        print("⚠️ supabase 库有兼容性问题，改用 REST API 方式", file=sys.stderr)
                    else:
                        raise ValueError("❌ 需要安装 requests 库: pip install requests")
                else:
                    raise ValueError(f"❌ 创建 Supabase 客户端失败: {error_msg}")
        else:
            if HAS_REQUESTS:
                self.use_rest_api = True
            else:
                raise ValueError("❌ 需要安装 supabase 或 requests 库")
    
    def _rest_api_post(self, table: str, data: Dict) -> Dict:
        """使用 REST API 插入数据"""
        url = f"{self.supabase_url}/rest/v1/{table}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result[0] if isinstance(result, list) else result
    
    def _rest_api_get(self, table: str, filters: Dict = None, order: str = None) -> list:
        """使用 REST API 查询数据"""
        url = f"{self.supabase_url}/rest/v1/{table}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        
        params = {}
        if filters:
            for key, value in filters.items():
                params[key] = f"eq.{value}"
        if order:
            params["order"] = order
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def _rest_api_patch(self, table: str, filters: Dict, data: Dict) -> Dict:
        """使用 REST API 更新数据"""
        url = f"{self.supabase_url}/rest/v1/{table}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # 构建查询参数
        params = {}
        for key, value in filters.items():
            params[key] = f"eq.{value}"
        
        response = requests.patch(url, headers=headers, params=params, json=data)
        response.raise_for_status()
        result = response.json()
        return result[0] if isinstance(result, list) and result else result
    
    def _rest_api_delete(self, table: str, filters: Dict) -> bool:
        """使用 REST API 删除数据"""
        url = f"{self.supabase_url}/rest/v1/{table}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        
        params = {}
        for key, value in filters.items():
            params[key] = f"eq.{value}"
        
        response = requests.delete(url, headers=headers, params=params)
        response.raise_for_status()
        return True
    
    def get_group_id(self, group_name: str) -> Optional[str]:
        """获取配置组 ID"""
        try:
            if self.use_rest_api:
                groups = self._rest_api_get("config_groups", {"name": group_name})
            else:
                result = self.client.table("config_groups")\
                    .select("id")\
                    .eq("name", group_name)\
                    .execute()
                groups = result.data
            
            return groups[0]["id"] if groups else None
        except Exception as e:
            raise Exception(f"❌ 获取配置组失败: {str(e)}")
    
    def add_group(self, name: str, description: str = "", category: str = "", is_active: bool = True) -> Dict:
        """添加配置组"""
        try:
            data = {
                "name": name,
                "description": description,
                "category": category,
                "is_active": is_active
            }
            
            if self.use_rest_api:
                result = self._rest_api_post("config_groups", data)
            else:
                result = self.client.table("config_groups")\
                    .insert(data)\
                    .execute()
                result = result.data[0] if result.data else None
            
            if result:
                print(f"✅ 配置组已添加: {name}")
                return result
            return {}
        except Exception as e:
            raise Exception(f"❌ 添加配置组失败: {str(e)}")
    
    def add_item(self, group_name: str, key: str, value: str, 
                 value_type: str = "string", description: str = "", 
                 is_secret: bool = False, order_index: int = 0) -> Dict:
        """添加配置项"""
        try:
            # 获取配置组 ID
            group_id = self.get_group_id(group_name)
            if not group_id:
                raise ValueError(f"❌ 配置组 '{group_name}' 不存在，请先创建")
            
            data = {
                "group_id": group_id,
                "key": key,
                "value": value,
                "value_type": value_type,
                "description": description,
                "is_secret": is_secret,
                "order_index": order_index
            }
            
            if self.use_rest_api:
                result = self._rest_api_post("config_items", data)
            else:
                result = self.client.table("config_items")\
                    .insert(data)\
                    .execute()
                result = result.data[0] if result.data else None
            
            if result:
                print(f"✅ 配置项已添加: {group_name}.{key} = {value if not is_secret else '***'}")
                return result
            return {}
        except Exception as e:
            raise Exception(f"❌ 添加配置项失败: {str(e)}")
    
    def update_item(self, group_name: str, key: str, value: str = None,
                   value_type: str = None, description: str = None,
                   is_secret: bool = None, order_index: int = None) -> Dict:
        """更新配置项"""
        try:
            # 获取配置组 ID
            group_id = self.get_group_id(group_name)
            if not group_id:
                raise ValueError(f"❌ 配置组 '{group_name}' 不存在")
            
            # 构建更新数据
            update_data = {}
            if value is not None:
                update_data["value"] = value
            if value_type is not None:
                update_data["value_type"] = value_type
            if description is not None:
                update_data["description"] = description
            if is_secret is not None:
                update_data["is_secret"] = is_secret
            if order_index is not None:
                update_data["order_index"] = order_index
            
            if not update_data:
                raise ValueError("❌ 没有提供要更新的字段")
            
            filters = {"group_id": group_id, "key": key}
            
            if self.use_rest_api:
                result = self._rest_api_patch("config_items", filters, update_data)
            else:
                result = self.client.table("config_items")\
                    .update(update_data)\
                    .eq("group_id", group_id)\
                    .eq("key", key)\
                    .execute()
                result = result.data[0] if result.data else None
            
            if result:
                print(f"✅ 配置项已更新: {group_name}.{key}")
                return result
            return {}
        except Exception as e:
            raise Exception(f"❌ 更新配置项失败: {str(e)}")
    
    def delete_item(self, group_name: str, key: str) -> bool:
        """删除配置项"""
        try:
            # 获取配置组 ID
            group_id = self.get_group_id(group_name)
            if not group_id:
                raise ValueError(f"❌ 配置组 '{group_name}' 不存在")
            
            filters = {"group_id": group_id, "key": key}
            
            if self.use_rest_api:
                self._rest_api_delete("config_items", filters)
            else:
                self.client.table("config_items")\
                    .delete()\
                    .eq("group_id", group_id)\
                    .eq("key", key)\
                    .execute()
            
            print(f"✅ 配置项已删除: {group_name}.{key}")
            return True
        except Exception as e:
            raise Exception(f"❌ 删除配置项失败: {str(e)}")
    
    def list_groups(self) -> list:
        """列出所有配置组"""
        try:
            if self.use_rest_api:
                return self._rest_api_get("config_groups", order="name")
            else:
                result = self.client.table("config_groups")\
                    .select("*")\
                    .order("name")\
                    .execute()
                return result.data
        except Exception as e:
            raise Exception(f"❌ 列出配置组失败: {str(e)}")
    
    def list_items(self, group_name: str) -> list:
        """列出配置组的所有配置项"""
        try:
            group_id = self.get_group_id(group_name)
            if not group_id:
                raise ValueError(f"❌ 配置组 '{group_name}' 不存在")
            
            if self.use_rest_api:
                return self._rest_api_get("config_items", {"group_id": group_id}, "order_index,key")
            else:
                result = self.client.table("config_items")\
                    .select("*")\
                    .eq("group_id", group_id)\
                    .order("order_index, key")\
                    .execute()
                return result.data
        except Exception as e:
            raise Exception(f"❌ 列出配置项失败: {str(e)}")


def main():
    """命令行工具"""
    parser = argparse.ArgumentParser(
        description="配置管理工具 - 管理 Supabase 中的配置",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
示例:
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
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # add-group 命令
    add_group_parser = subparsers.add_parser("add-group", help="添加配置组")
    add_group_parser.add_argument("--name", "-n", required=True, help="配置组名称")
    add_group_parser.add_argument("--description", "-d", default="", help="描述")
    add_group_parser.add_argument("--category", "-c", default="", help="分类")
    add_group_parser.add_argument("--active", action="store_true", default=True, help="是否激活")
    
    # add-item 命令
    add_item_parser = subparsers.add_parser("add-item", help="添加配置项")
    add_item_parser.add_argument("--group", "-g", required=True, help="配置组名称")
    add_item_parser.add_argument("--key", "-k", required=True, help="配置键")
    add_item_parser.add_argument("--value", "-v", required=True, help="配置值")
    add_item_parser.add_argument("--type", "-t", default="string", choices=["string", "number", "boolean", "json", "array"], help="值类型")
    add_item_parser.add_argument("--description", "-d", default="", help="描述")
    add_item_parser.add_argument("--secret", action="store_true", help="是否为敏感信息")
    add_item_parser.add_argument("--order", "-o", type=int, default=0, help="排序索引")
    
    # update-item 命令
    update_item_parser = subparsers.add_parser("update-item", help="更新配置项")
    update_item_parser.add_argument("--group", "-g", required=True, help="配置组名称")
    update_item_parser.add_argument("--key", "-k", required=True, help="配置键")
    update_item_parser.add_argument("--value", "-v", help="新值")
    update_item_parser.add_argument("--type", "-t", choices=["string", "number", "boolean", "json", "array"], help="值类型")
    update_item_parser.add_argument("--description", "-d", help="描述")
    update_item_parser.add_argument("--secret", action="store_true", help="标记为敏感信息")
    update_item_parser.add_argument("--no-secret", action="store_true", help="取消敏感信息标记")
    update_item_parser.add_argument("--order", "-o", type=int, help="排序索引")
    
    # delete-item 命令
    delete_item_parser = subparsers.add_parser("delete-item", help="删除配置项")
    delete_item_parser.add_argument("--group", "-g", required=True, help="配置组名称")
    delete_item_parser.add_argument("--key", "-k", required=True, help="配置键")
    
    # list-groups 命令
    subparsers.add_parser("list-groups", help="列出所有配置组")
    
    # list-items 命令
    list_items_parser = subparsers.add_parser("list-items", help="列出配置组的所有配置项")
    list_items_parser.add_argument("--group", "-g", required=True, help="配置组名称")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        manager = ConfigManager()
        
        if args.command == "add-group":
            manager.add_group(
                name=args.name,
                description=args.description,
                category=args.category,
                is_active=args.active
            )
        
        elif args.command == "add-item":
            manager.add_item(
                group_name=args.group,
                key=args.key,
                value=args.value,
                value_type=args.type,
                description=args.description,
                is_secret=args.secret,
                order_index=args.order
            )
        
        elif args.command == "update-item":
            is_secret = None
            if args.secret:
                is_secret = True
            elif args.no_secret:
                is_secret = False
            
            manager.update_item(
                group_name=args.group,
                key=args.key,
                value=args.value,
                value_type=args.type,
                description=args.description,
                is_secret=is_secret,
                order_index=args.order
            )
        
        elif args.command == "delete-item":
            manager.delete_item(
                group_name=args.group,
                key=args.key
            )
        
        elif args.command == "list-groups":
            groups = manager.list_groups()
            if groups:
                print(f"\n📋 配置组列表 (共 {len(groups)} 个):\n")
                for group in groups:
                    status = "✅" if group.get("is_active") else "❌"
                    print(f"  {status} [{group['name']}]")
                    print(f"     分类: {group.get('category', 'N/A')}")
                    print(f"     描述: {group.get('description', 'N/A')}")
                    print()
            else:
                print("📋 暂无配置组")
        
        elif args.command == "list-items":
            items = manager.list_items(args.group)
            if items:
                print(f"\n📋 配置项列表 ({args.group}, 共 {len(items)} 个):\n")
                for item in items:
                    value = item["value"] if not item.get("is_secret") else "***HIDDEN***"
                    secret_mark = "🔒" if item.get("is_secret") else "  "
                    print(f"  {secret_mark} {item['key']} = {value}")
                    print(f"     类型: {item.get('value_type', 'string')}")
                    if item.get('description'):
                        print(f"     描述: {item['description']}")
                    print()
            else:
                print(f"📋 配置组 '{args.group}' 暂无配置项")
    
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

