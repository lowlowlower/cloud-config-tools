#!/usr/bin/env python3
"""
项目信息配置工具
将当前项目信息保存到 Supabase project_info 表
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any

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


class ProjectConfigManager:
    """项目信息配置管理器"""
    
    # 硬编码的默认配置（和 cloud-config 一致）
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
    
    def _rest_api_patch(self, table: str, id_value: Any, data: Dict) -> Dict:
        """使用 REST API 更新数据"""
        url = f"{self.supabase_url}/rest/v1/{table}?id=eq.{id_value}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result[0] if isinstance(result, list) else result
    
    def get_git_info(self, project_path: Path) -> Dict[str, Optional[str]]:
        """获取 Git 仓库信息"""
        git_info = {
            "git_repo": None,
            "git_branch": None,
            "git_remote": None
        }
        
        try:
            # 检查是否是 Git 仓库
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # 获取远程仓库 URL
                result = subprocess.run(
                    ["git", "config", "--get", "remote.origin.url"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    git_info["git_repo"] = result.stdout.strip()
                    git_info["git_remote"] = "origin"
                
                # 获取当前分支
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    git_info["git_branch"] = result.stdout.strip()
        except Exception:
            pass
        
        return git_info
    
    def detect_project_type(self, project_path: Path) -> Optional[str]:
        """检测项目类型"""
        # 检查常见项目文件
        if (project_path / "package.json").exists():
            return "nodejs"
        elif (project_path / "requirements.txt").exists() or (project_path / "setup.py").exists():
            return "python"
        elif (project_path / "Cargo.toml").exists():
            return "rust"
        elif (project_path / "go.mod").exists():
            return "go"
        elif (project_path / "pom.xml").exists():
            return "java"
        elif (project_path / "composer.json").exists():
            return "php"
        elif (project_path / "Gemfile").exists():
            return "ruby"
        elif (project_path / ".csproj").exists():
            return "dotnet"
        else:
            return None
    
    def get_project_info(self, project_path: str = None) -> Dict[str, Any]:
        """获取当前项目信息"""
        if not project_path:
            project_path = os.getcwd()
        
        project_path = Path(project_path).resolve()
        
        # 获取项目名称（使用目录名）
        project_name = project_path.name
        
        # 获取 Git 信息
        git_info = self.get_git_info(project_path)
        
        # 检测项目类型
        project_type = self.detect_project_type(project_path)
        
        return {
            "project_name": project_name,
            "project_path": str(project_path),
            "project_type": project_type,
            "git_repo": git_info.get("git_repo"),
            "description": None,
            "tags": None,
            "last_opened": datetime.now().isoformat()
        }
    
    def save_project_info(self, project_info: Dict[str, Any], update_if_exists: bool = True) -> Dict[str, Any]:
        """保存项目信息到数据库"""
        try:
            # 检查项目是否已存在（根据 project_path）
            if self.use_rest_api:
                existing = self._rest_api_get("project_info", {"project_path": project_info["project_path"]})
            else:
                result = self.client.table("project_info")\
                    .select("*")\
                    .eq("project_path", project_info["project_path"])\
                    .execute()
                existing = result.data
            
            if existing and update_if_exists:
                # 更新现有项目
                project_id = existing[0]["id"]
                
                # 准备更新数据（排除 id）
                update_data = {k: v for k, v in project_info.items() if k != "id"}
                update_data["updated_at"] = datetime.now().isoformat()
                
                if self.use_rest_api:
                    updated = self._rest_api_patch("project_info", project_id, update_data)
                else:
                    result = self.client.table("project_info")\
                        .update(update_data)\
                        .eq("id", project_id)\
                        .execute()
                    updated = result.data[0] if result.data else None
                
                if updated:
                    print(f"✅ 项目信息已更新: {project_info['project_name']}")
                    return updated
            else:
                # 插入新项目
                insert_data = project_info.copy()
                insert_data["created_at"] = datetime.now().isoformat()
                insert_data["updated_at"] = datetime.now().isoformat()
                
                if self.use_rest_api:
                    inserted = self._rest_api_post("project_info", insert_data)
                else:
                    result = self.client.table("project_info")\
                        .insert(insert_data)\
                        .execute()
                    inserted = result.data[0] if result.data else None
                
                if inserted:
                    print(f"✅ 项目信息已保存: {project_info['project_name']}")
                    return inserted
            
            return {}
        
        except Exception as e:
            raise Exception(f"❌ 保存项目信息失败: {str(e)}")
    
    def list_projects(self) -> list:
        """列出所有项目"""
        try:
            if self.use_rest_api:
                return self._rest_api_get("project_info", order="last_opened.desc")
            else:
                result = self.client.table("project_info")\
                    .select("*")\
                    .order("last_opened", desc=True)\
                    .execute()
                return result.data
        except Exception as e:
            raise Exception(f"❌ 列出项目失败: {str(e)}")


def main():
    """命令行工具"""
    parser = argparse.ArgumentParser(
        description="项目信息配置工具 - 保存项目信息到 Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
示例:
  # 保存当前项目信息
  project-config
  
  # 保存指定项目
  project-config --path D:\github\my-project
  
  # 添加描述和标签
  project-config --description "我的项目" --tags python,web
  
  # 列出所有项目
  project-config --list
  
  # 更新项目（如果已存在）
  project-config --update
        """
    )
    
    parser.add_argument(
        "--path", "-p",
        help="项目路径（默认：当前目录）"
    )
    parser.add_argument(
        "--name", "-n",
        help="项目名称（默认：目录名）"
    )
    parser.add_argument(
        "--description", "-d",
        help="项目描述"
    )
    parser.add_argument(
        "--tags", "-t",
        help="标签（逗号分隔，如：python,web,api）"
    )
    parser.add_argument(
        "--type",
        help="项目类型（如：python, nodejs, rust）"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有项目"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        default=True,
        help="如果项目已存在则更新（默认：True）"
    )
    parser.add_argument(
        "--no-update",
        action="store_false",
        dest="update",
        help="如果项目已存在则不更新"
    )
    
    args = parser.parse_args()
    
    try:
        manager = ProjectConfigManager()
        
        if args.list:
            # 列出所有项目
            projects = manager.list_projects()
            if projects:
                print(f"\n📋 项目列表 (共 {len(projects)} 个):\n")
                for project in projects:
                    print(f"  [{project.get('project_name', 'N/A')}]")
                    print(f"    路径: {project.get('project_path', 'N/A')}")
                    print(f"    类型: {project.get('project_type', 'N/A')}")
                    if project.get('git_repo'):
                        print(f"    Git: {project['git_repo']}")
                    if project.get('description'):
                        print(f"    描述: {project['description']}")
                    print()
            else:
                print("📋 暂无项目")
        else:
            # 获取项目信息
            project_info = manager.get_project_info(args.path)
            
            # 覆盖用户指定的值
            if args.name:
                project_info["project_name"] = args.name
            if args.description:
                project_info["description"] = args.description
            if args.tags:
                project_info["tags"] = [tag.strip() for tag in args.tags.split(",")]
            if args.type:
                project_info["project_type"] = args.type
            
            # 保存项目信息
            result = manager.save_project_info(project_info, update_if_exists=args.update)
            
            if result:
                print(f"\n项目 ID: {result.get('id', 'N/A')}")
                print(f"项目路径: {project_info['project_path']}")
    
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

