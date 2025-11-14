#!/usr/bin/env python3
"""
配置管理工具 - GUI 版本（现代化设计）
图形界面管理 Supabase 中的配置
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
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


class ModernConfigManagerGUI:
    """现代化配置管理器 GUI"""
    
    # 硬编码的默认配置
    DEFAULT_SUPABASE_URL = "https://yjeeaegldbsyslnlbesr.supabase.co"
    DEFAULT_SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlqZWVhZWdsZGJzeXNsbmxiZXNyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5NzUxODQsImV4cCI6MjA3MjU1MTE4NH0.b4rK2iCdX6uissLqeZep_oW1G0aTROpacfUug59PrSI"
    
    # 现代化配色方案
    COLORS = {
        'bg_primary': '#1e1e1e',           # 深色背景
        'bg_secondary': '#252526',          # 次要背景
        'bg_tertiary': '#2d2d30',           # 第三背景
        'bg_hover': '#3e3e42',              # 悬停背景
        'bg_selected': '#007acc',           # 选中背景
        'text_primary': '#cccccc',          # 主文本
        'text_secondary': '#858585',         # 次要文本
        'text_accent': '#4ec9b0',           # 强调文本
        'border': '#3e3e42',                # 边框
        'button_bg': '#0e639c',             # 按钮背景
        'button_hover': '#1177bb',          # 按钮悬停
        'success': '#4ec9b0',               # 成功色
        'warning': '#dcdcaa',               # 警告色
        'error': '#f48771',                 # 错误色
        'secret_bg': '#3a3a3a',             # 敏感信息背景
    }
    
    def __init__(self, root):
        """初始化 GUI"""
        self.root = root
        self.root.title("配置管理器 - Cloud Config Manager")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.COLORS['bg_primary'])
        
        # 设置现代化主题
        self._setup_theme()
        
        # 初始化 Supabase 连接
        self.supabase_url = self.DEFAULT_SUPABASE_URL
        self.supabase_key = self.DEFAULT_SUPABASE_KEY
        self.client = None
        self.use_rest_api = False
        
        self._init_supabase()
        
        # 当前选中的配置组
        self.current_group = None
        self.groups = []
        self.items = []
        
        # 创建界面
        self._create_widgets()
        
        # 加载配置组列表
        self.refresh_groups()
    
    def _setup_theme(self):
        """设置现代化主题"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置 Treeview 样式
        style.configure('Modern.Treeview',
                       background=self.COLORS['bg_secondary'],
                       foreground=self.COLORS['text_primary'],
                       fieldbackground=self.COLORS['bg_secondary'],
                       borderwidth=0,
                       rowheight=30)
        
        style.map('Modern.Treeview',
                 background=[('selected', self.COLORS['bg_selected'])],
                 foreground=[('selected', 'white')])
        
        # 配置 Treeview 标题样式
        style.configure('Modern.Treeview.Heading',
                       background=self.COLORS['bg_tertiary'],
                       foreground=self.COLORS['text_primary'],
                       borderwidth=1,
                       relief='flat',
                       font=('Segoe UI', 10, 'bold'))
        
        # 配置按钮样式
        style.configure('Modern.TButton',
                       background=self.COLORS['button_bg'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8),
                       font=('Segoe UI', 9))
        
        style.map('Modern.TButton',
                 background=[('active', self.COLORS['button_hover']),
                           ('pressed', self.COLORS['button_bg'])])
        
        # 配置 LabelFrame 样式
        style.configure('Modern.TLabelframe',
                       background=self.COLORS['bg_primary'],
                       foreground=self.COLORS['text_primary'],
                       borderwidth=1,
                       relief='flat')
        
        style.configure('Modern.TLabelframe.Label',
                       background=self.COLORS['bg_primary'],
                       foreground=self.COLORS['text_accent'],
                       font=('Segoe UI', 11, 'bold'))
    
    def _init_supabase(self):
        """初始化 Supabase 连接"""
        if HAS_SUPABASE:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
            except (TypeError, Exception) as e:
                error_msg = str(e)
                if "proxy" in error_msg or "unexpected keyword" in error_msg:
                    if HAS_REQUESTS:
                        self.use_rest_api = True
                    else:
                        messagebox.showerror("错误", "需要安装 requests 库: pip install requests")
                        sys.exit(1)
                else:
                    messagebox.showerror("错误", f"创建 Supabase 客户端失败: {error_msg}")
                    sys.exit(1)
        else:
            if HAS_REQUESTS:
                self.use_rest_api = True
            else:
                messagebox.showerror("错误", "需要安装 supabase 或 requests 库")
                sys.exit(1)
    
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
    
    def _create_widgets(self):
        """创建界面组件"""
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg=self.COLORS['bg_tertiary'], height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="⚙️ 配置管理器",
                              bg=self.COLORS['bg_tertiary'],
                              fg=self.COLORS['text_accent'],
                              font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # 顶部工具栏
        toolbar = tk.Frame(self.root, bg=self.COLORS['bg_secondary'], height=60)
        toolbar.pack(fill=tk.X, padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        toolbar_inner = tk.Frame(toolbar, bg=self.COLORS['bg_secondary'])
        toolbar_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 按钮容器
        btn_frame = tk.Frame(toolbar_inner, bg=self.COLORS['bg_secondary'])
        btn_frame.pack(side=tk.LEFT)
        
        self._create_button(btn_frame, "🔄 刷新", self.refresh_all, padx=5)
        self._create_button(btn_frame, "➕ 添加配置组", self.add_group_dialog, padx=5)
        
        separator = tk.Frame(toolbar_inner, bg=self.COLORS['border'], width=1)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        self._create_button(btn_frame, "➕ 添加配置项", self.add_item_dialog, padx=5)
        self._create_button(btn_frame, "✏️ 编辑", self.edit_item_dialog, padx=5)
        self._create_button(btn_frame, "🗑️ 删除", self.delete_item, padx=5, color='error')
        
        # 主容器：左右分栏
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：配置组列表
        left_frame = tk.LabelFrame(main_frame,
                                   text="📁 配置组列表",
                                   bg=self.COLORS['bg_primary'],
                                   fg=self.COLORS['text_accent'],
                                   font=('Segoe UI', 11, 'bold'),
                                   relief='flat',
                                   borderwidth=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.config(width=280)
        
        # 配置组列表容器
        group_list_frame = tk.Frame(left_frame, bg=self.COLORS['bg_secondary'])
        group_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 使用 Canvas 和 Scrollbar 实现滚动
        canvas = tk.Canvas(group_list_frame,
                          bg=self.COLORS['bg_secondary'],
                          highlightthickness=0)
        scrollbar = tk.Scrollbar(group_list_frame,
                                orient=tk.VERTICAL,
                                command=canvas.yview,
                                bg=self.COLORS['bg_tertiary'],
                                troughcolor=self.COLORS['bg_secondary'],
                                width=12)
        
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['bg_secondary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.group_container = scrollable_frame
        self.group_canvas = canvas
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右侧：配置项列表
        right_frame = tk.LabelFrame(main_frame,
                                    text="📋 配置项列表",
                                    bg=self.COLORS['bg_primary'],
                                    fg=self.COLORS['text_accent'],
                                    font=('Segoe UI', 11, 'bold'),
                                    relief='flat',
                                    borderwidth=1)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置项表格容器
        item_frame = tk.Frame(right_frame, bg=self.COLORS['bg_secondary'])
        item_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ('key', 'value', 'type', 'secret', 'description')
        self.item_tree = ttk.Treeview(item_frame,
                                      columns=columns,
                                      show='headings',
                                      height=25,
                                      style='Modern.Treeview')
        
        # 设置列标题和宽度
        self.item_tree.heading('key', text='🔑 键名')
        self.item_tree.heading('value', text='💎 值')
        self.item_tree.heading('type', text='📝 类型')
        self.item_tree.heading('secret', text='🔒 敏感')
        self.item_tree.heading('description', text='📄 描述')
        
        self.item_tree.column('key', width=200, anchor='w')
        self.item_tree.column('value', width=300, anchor='w')
        self.item_tree.column('type', width=100, anchor='center')
        self.item_tree.column('secret', width=80, anchor='center')
        self.item_tree.column('description', width=400, anchor='w')
        
        # 滚动条
        scrollbar_items = ttk.Scrollbar(item_frame,
                                       orient=tk.VERTICAL,
                                       command=self.item_tree.yview)
        self.item_tree.configure(yscrollcommand=scrollbar_items.set)
        
        self.item_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_items.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 双击编辑
        self.item_tree.bind('<Double-1>', lambda e: self.edit_item_dialog())
        
        # 绑定鼠标悬停效果
        self.item_tree.bind('<Motion>', self._on_tree_hover)
    
    def _create_button(self, parent, text, command, padx=0, color='primary'):
        """创建现代化按钮"""
        if color == 'error':
            bg = self.COLORS['error']
            hover_bg = '#ff6b5a'
        else:
            bg = self.COLORS['button_bg']
            hover_bg = self.COLORS['button_hover']
        
        btn = tk.Button(parent,
                       text=text,
                       command=command,
                       bg=bg,
                       fg='white',
                       font=('Segoe UI', 9),
                       relief='flat',
                       borderwidth=0,
                       padx=15,
                       pady=8,
                       cursor='hand2',
                       activebackground=hover_bg,
                       activeforeground='white')
        
        def on_enter(e):
            btn.config(bg=hover_bg)
        
        def on_leave(e):
            btn.config(bg=bg)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.pack(side=tk.LEFT, padx=padx)
        
        return btn
    
    def _on_tree_hover(self, event):
        """树形控件悬停效果"""
        region = self.item_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.item_tree.identify_row(event.y)
            if item:
                self.item_tree.selection_set(item)
    
    def refresh_all(self):
        """刷新所有数据"""
        self.refresh_groups()
        if self.current_group:
            self.refresh_items()
        messagebox.showinfo("成功", "数据已刷新")
    
    def refresh_groups(self):
        """刷新配置组列表"""
        try:
            if self.use_rest_api:
                self.groups = self._rest_api_get("config_groups", order="name")
            else:
                result = self.client.table("config_groups").select("*").order("name").execute()
                self.groups = result.data
            
            # 清空现有按钮
            for widget in self.group_container.winfo_children():
                widget.destroy()
            
            # 创建配置组按钮
            for group in self.groups:
                self._create_group_button(group)
            
            # 更新滚动区域
            self.group_container.update_idletasks()
            self.group_canvas.configure(scrollregion=self.group_canvas.bbox("all"))
        except Exception as e:
            messagebox.showerror("错误", f"加载配置组失败: {str(e)}")
    
    def _create_group_button(self, group):
        """创建配置组按钮"""
        status = "✅" if group.get("is_active") else "❌"
        text = f"{status} {group['name']}"
        
        btn = tk.Button(self.group_container,
                       text=text,
                       command=lambda g=group: self._select_group(g),
                       bg=self.COLORS['bg_tertiary'],
                       fg=self.COLORS['text_primary'],
                       font=('Segoe UI', 10),
                       relief='flat',
                       borderwidth=0,
                       anchor='w',
                       padx=15,
                       pady=12,
                       cursor='hand2',
                       activebackground=self.COLORS['bg_hover'],
                       activeforeground=self.COLORS['text_primary'])
        
        btn.pack(fill=tk.X, pady=2)
        
        # 存储按钮引用以便后续更新样式
        btn.group = group
    
    def _select_group(self, group):
        """选择配置组"""
        self.current_group = group
        
        # 更新按钮样式
        for widget in self.group_container.winfo_children():
            if hasattr(widget, 'group'):
                if widget.group['id'] == group['id']:
                    widget.config(bg=self.COLORS['bg_selected'], fg='white')
                else:
                    widget.config(bg=self.COLORS['bg_tertiary'], fg=self.COLORS['text_primary'])
        
        self.refresh_items()
    
    def refresh_items(self):
        """刷新配置项列表"""
        if not self.current_group:
            return
        
        try:
            group_id = self.current_group["id"]
            
            if self.use_rest_api:
                self.items = self._rest_api_get("config_items", {"group_id": group_id}, "order_index,key")
            else:
                result = self.client.table("config_items")\
                    .select("*")\
                    .eq("group_id", group_id)\
                    .order("order_index, key")\
                    .execute()
                self.items = result.data
            
            # 清空表格
            for item in self.item_tree.get_children():
                self.item_tree.delete(item)
            
            # 填充表格
            for item in self.items:
                # 直接显示值，不隐藏
                value = item["value"]
                secret = "🔒" if item.get("is_secret") else ""
                
                # 根据类型添加图标
                type_icon = {
                    'string': '📝',
                    'number': '🔢',
                    'boolean': '✓',
                    'json': '📦',
                    'array': '📋'
                }.get(item.get('value_type', 'string'), '📝')
                
                type_display = f"{type_icon} {item.get('value_type', 'string')}"
                
                self.item_tree.insert('', tk.END, values=(
                    item['key'],
                    value,
                    type_display,
                    secret,
                    item.get('description', '')
                ))
        except Exception as e:
            messagebox.showerror("错误", f"加载配置项失败: {str(e)}")
    
    def add_group_dialog(self):
        """添加配置组对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ 添加配置组")
        dialog.geometry("450x280")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.COLORS['bg_primary'])
        
        # 标题
        title_label = tk.Label(dialog,
                              text="添加新配置组",
                              bg=self.COLORS['bg_primary'],
                              fg=self.COLORS['text_accent'],
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # 表单容器
        form_frame = tk.Frame(dialog, bg=self.COLORS['bg_primary'])
        form_frame.pack(padx=30, pady=10)
        
        tk.Label(form_frame,
                text="配置组名称:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=10)
        name_entry = tk.Entry(form_frame,
                             width=35,
                             font=('Segoe UI', 10),
                             bg=self.COLORS['bg_secondary'],
                             fg=self.COLORS['text_primary'],
                             insertbackground=self.COLORS['text_primary'],
                             relief='flat',
                             borderwidth=1)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(form_frame,
                text="分类:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=10)
        category_entry = tk.Entry(form_frame,
                                  width=35,
                                  font=('Segoe UI', 10),
                                  bg=self.COLORS['bg_secondary'],
                                  fg=self.COLORS['text_primary'],
                                  insertbackground=self.COLORS['text_primary'],
                                  relief='flat',
                                  borderwidth=1)
        category_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(form_frame,
                text="描述:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', pady=10)
        desc_entry = tk.Entry(form_frame,
                             width=35,
                             font=('Segoe UI', 10),
                             bg=self.COLORS['bg_secondary'],
                             fg=self.COLORS['text_primary'],
                             insertbackground=self.COLORS['text_primary'],
                             relief='flat',
                             borderwidth=1)
        desc_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("错误", "配置组名称不能为空")
                return
            
            try:
                data = {
                    "name": name,
                    "category": category_entry.get().strip(),
                    "description": desc_entry.get().strip(),
                    "is_active": True
                }
                
                if self.use_rest_api:
                    self._rest_api_post("config_groups", data)
                else:
                    self.client.table("config_groups").insert(data).execute()
                
                messagebox.showinfo("成功", f"配置组 '{name}' 已添加")
                dialog.destroy()
                self.refresh_groups()
            except Exception as e:
                messagebox.showerror("错误", f"添加配置组失败: {str(e)}")
        
        # 按钮容器
        btn_frame = tk.Frame(dialog, bg=self.COLORS['bg_primary'])
        btn_frame.pack(pady=20)
        
        save_btn = tk.Button(btn_frame,
                            text="💾 保存",
                            command=save,
                            bg=self.COLORS['success'],
                            fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief='flat',
                            padx=30,
                            pady=10,
                            cursor='hand2',
                            activebackground='#5ed9c9')
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(btn_frame,
                              text="❌ 取消",
                              command=dialog.destroy,
                              bg=self.COLORS['bg_tertiary'],
                              fg=self.COLORS['text_primary'],
                              font=('Segoe UI', 10),
                              relief='flat',
                              padx=30,
                              pady=10,
                              cursor='hand2',
                              activebackground=self.COLORS['bg_hover'])
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        name_entry.focus()
    
    def add_item_dialog(self):
        """添加配置项对话框"""
        if not self.current_group:
            messagebox.showwarning("警告", "请先选择一个配置组")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"➕ 添加配置项 - {self.current_group['name']}")
        dialog.geometry("550x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.COLORS['bg_primary'])
        
        # 标题
        title_label = tk.Label(dialog,
                              text=f"添加配置项到: {self.current_group['name']}",
                              bg=self.COLORS['bg_primary'],
                              fg=self.COLORS['text_accent'],
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(20, 20))
        
        # 表单容器
        form_frame = tk.Frame(dialog, bg=self.COLORS['bg_primary'])
        form_frame.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(form_frame,
                text="键名:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=0, column=0, sticky='nw', pady=10)
        key_entry = tk.Entry(form_frame,
                            width=40,
                            font=('Segoe UI', 10),
                            bg=self.COLORS['bg_secondary'],
                            fg=self.COLORS['text_primary'],
                            insertbackground=self.COLORS['text_primary'],
                            relief='flat',
                            borderwidth=1)
        key_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        
        tk.Label(form_frame,
                text="值:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=1, column=0, sticky='nw', pady=10)
        value_text = scrolledtext.ScrolledText(form_frame,
                                               width=40,
                                               height=6,
                                               font=('Consolas', 10),
                                               bg=self.COLORS['bg_secondary'],
                                               fg=self.COLORS['text_primary'],
                                               insertbackground=self.COLORS['text_primary'],
                                               relief='flat',
                                               borderwidth=1,
                                               wrap=tk.WORD)
        value_text.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        
        tk.Label(form_frame,
                text="类型:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', pady=10)
        type_combo = ttk.Combobox(form_frame,
                                 values=["string", "number", "boolean", "json", "array"],
                                 width=37,
                                 font=('Segoe UI', 10),
                                 state='readonly')
        type_combo.set("string")
        type_combo.grid(row=2, column=1, padx=10, pady=10, sticky='ew')
        
        tk.Label(form_frame,
                text="描述:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=3, column=0, sticky='w', pady=10)
        desc_entry = tk.Entry(form_frame,
                             width=40,
                             font=('Segoe UI', 10),
                             bg=self.COLORS['bg_secondary'],
                             fg=self.COLORS['text_primary'],
                             insertbackground=self.COLORS['text_primary'],
                             relief='flat',
                             borderwidth=1)
        desc_entry.grid(row=3, column=1, padx=10, pady=10, sticky='ew')
        
        is_secret = tk.BooleanVar()
        secret_check = tk.Checkbutton(form_frame,
                                     text="🔒 标记为敏感信息",
                                     variable=is_secret,
                                     bg=self.COLORS['bg_primary'],
                                     fg=self.COLORS['text_primary'],
                                     font=('Segoe UI', 10),
                                     selectcolor=self.COLORS['bg_secondary'],
                                     activebackground=self.COLORS['bg_primary'],
                                     activeforeground=self.COLORS['text_primary'])
        secret_check.grid(row=4, column=1, padx=10, pady=10, sticky='w')
        
        tk.Label(form_frame,
                text="排序:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=5, column=0, sticky='w', pady=10)
        order_entry = tk.Entry(form_frame,
                              width=40,
                              font=('Segoe UI', 10),
                              bg=self.COLORS['bg_secondary'],
                              fg=self.COLORS['text_primary'],
                              insertbackground=self.COLORS['text_primary'],
                              relief='flat',
                              borderwidth=1)
        order_entry.insert(0, "0")
        order_entry.grid(row=5, column=1, padx=10, pady=10, sticky='ew')
        
        form_frame.columnconfigure(1, weight=1)
        
        def save():
            key = key_entry.get().strip()
            value = value_text.get("1.0", tk.END).strip()
            
            if not key:
                messagebox.showerror("错误", "键名不能为空")
                return
            
            try:
                order_index = int(order_entry.get().strip() or "0")
            except ValueError:
                order_index = 0
            
            try:
                data = {
                    "group_id": self.current_group["id"],
                    "key": key,
                    "value": value,
                    "value_type": type_combo.get(),
                    "description": desc_entry.get().strip(),
                    "is_secret": is_secret.get(),
                    "order_index": order_index
                }
                
                if self.use_rest_api:
                    self._rest_api_post("config_items", data)
                else:
                    self.client.table("config_items").insert(data).execute()
                
                messagebox.showinfo("成功", f"配置项 '{key}' 已添加")
                dialog.destroy()
                self.refresh_items()
            except Exception as e:
                messagebox.showerror("错误", f"添加配置项失败: {str(e)}")
        
        # 按钮容器
        btn_frame = tk.Frame(dialog, bg=self.COLORS['bg_primary'])
        btn_frame.pack(pady=20)
        
        save_btn = tk.Button(btn_frame,
                            text="💾 保存",
                            command=save,
                            bg=self.COLORS['success'],
                            fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief='flat',
                            padx=30,
                            pady=10,
                            cursor='hand2',
                            activebackground='#5ed9c9')
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(btn_frame,
                              text="❌ 取消",
                              command=dialog.destroy,
                              bg=self.COLORS['bg_tertiary'],
                              fg=self.COLORS['text_primary'],
                              font=('Segoe UI', 10),
                              relief='flat',
                              padx=30,
                              pady=10,
                              cursor='hand2',
                              activebackground=self.COLORS['bg_hover'])
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        key_entry.focus()
    
    def edit_item_dialog(self):
        """编辑配置项对话框"""
        if not self.current_group:
            messagebox.showwarning("警告", "请先选择一个配置组")
            return
        
        selection = self.item_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个配置项")
            return
        
        item_values = self.item_tree.item(selection[0])['values']
        key = item_values[0]
        
        # 查找配置项
        item = next((i for i in self.items if i['key'] == key), None)
        if not item:
            messagebox.showerror("错误", "找不到配置项")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"✏️ 编辑配置项 - {key}")
        dialog.geometry("550x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.COLORS['bg_primary'])
        
        # 标题
        title_label = tk.Label(dialog,
                              text=f"编辑配置项: {key}",
                              bg=self.COLORS['bg_primary'],
                              fg=self.COLORS['text_accent'],
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(20, 20))
        
        # 表单容器
        form_frame = tk.Frame(dialog, bg=self.COLORS['bg_primary'])
        form_frame.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(form_frame,
                text="键名:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=10)
        key_entry = tk.Entry(form_frame,
                            width=40,
                            font=('Segoe UI', 10),
                            bg=self.COLORS['bg_tertiary'],
                            fg=self.COLORS['text_secondary'],
                            relief='flat',
                            borderwidth=1,
                            state='readonly')
        key_entry.insert(0, item['key'])
        key_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        
        tk.Label(form_frame,
                text="值:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=1, column=0, sticky='nw', pady=10)
        value_text = scrolledtext.ScrolledText(form_frame,
                                               width=40,
                                               height=6,
                                               font=('Consolas', 10),
                                               bg=self.COLORS['bg_secondary'],
                                               fg=self.COLORS['text_primary'],
                                               insertbackground=self.COLORS['text_primary'],
                                               relief='flat',
                                               borderwidth=1,
                                               wrap=tk.WORD)
        value_text.insert("1.0", item['value'])
        value_text.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        
        tk.Label(form_frame,
                text="类型:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', pady=10)
        type_combo = ttk.Combobox(form_frame,
                                 values=["string", "number", "boolean", "json", "array"],
                                 width=37,
                                 font=('Segoe UI', 10),
                                 state='readonly')
        type_combo.set(item.get('value_type', 'string'))
        type_combo.grid(row=2, column=1, padx=10, pady=10, sticky='ew')
        
        tk.Label(form_frame,
                text="描述:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=3, column=0, sticky='w', pady=10)
        desc_entry = tk.Entry(form_frame,
                             width=40,
                             font=('Segoe UI', 10),
                             bg=self.COLORS['bg_secondary'],
                             fg=self.COLORS['text_primary'],
                             insertbackground=self.COLORS['text_primary'],
                             relief='flat',
                             borderwidth=1)
        desc_entry.insert(0, item.get('description', ''))
        desc_entry.grid(row=3, column=1, padx=10, pady=10, sticky='ew')
        
        is_secret = tk.BooleanVar(value=item.get('is_secret', False))
        secret_check = tk.Checkbutton(form_frame,
                                     text="🔒 标记为敏感信息",
                                     variable=is_secret,
                                     bg=self.COLORS['bg_primary'],
                                     fg=self.COLORS['text_primary'],
                                     font=('Segoe UI', 10),
                                     selectcolor=self.COLORS['bg_secondary'],
                                     activebackground=self.COLORS['bg_primary'],
                                     activeforeground=self.COLORS['text_primary'])
        secret_check.grid(row=4, column=1, padx=10, pady=10, sticky='w')
        
        tk.Label(form_frame,
                text="排序:",
                bg=self.COLORS['bg_primary'],
                fg=self.COLORS['text_primary'],
                font=('Segoe UI', 10)).grid(row=5, column=0, sticky='w', pady=10)
        order_entry = tk.Entry(form_frame,
                              width=40,
                              font=('Segoe UI', 10),
                              bg=self.COLORS['bg_secondary'],
                              fg=self.COLORS['text_primary'],
                              insertbackground=self.COLORS['text_primary'],
                              relief='flat',
                              borderwidth=1)
        order_entry.insert(0, str(item.get('order_index', 0)))
        order_entry.grid(row=5, column=1, padx=10, pady=10, sticky='ew')
        
        form_frame.columnconfigure(1, weight=1)
        
        def save():
            value = value_text.get("1.0", tk.END).strip()
            
            try:
                order_index = int(order_entry.get().strip() or "0")
            except ValueError:
                order_index = 0
            
            try:
                update_data = {
                    "value": value,
                    "value_type": type_combo.get(),
                    "description": desc_entry.get().strip(),
                    "is_secret": is_secret.get(),
                    "order_index": order_index
                }
                
                filters = {"group_id": self.current_group["id"], "key": key}
                
                if self.use_rest_api:
                    self._rest_api_patch("config_items", filters, update_data)
                else:
                    self.client.table("config_items")\
                        .update(update_data)\
                        .eq("group_id", self.current_group["id"])\
                        .eq("key", key)\
                        .execute()
                
                messagebox.showinfo("成功", f"配置项 '{key}' 已更新")
                dialog.destroy()
                self.refresh_items()
            except Exception as e:
                messagebox.showerror("错误", f"更新配置项失败: {str(e)}")
        
        # 按钮容器
        btn_frame = tk.Frame(dialog, bg=self.COLORS['bg_primary'])
        btn_frame.pack(pady=20)
        
        save_btn = tk.Button(btn_frame,
                            text="💾 保存",
                            command=save,
                            bg=self.COLORS['success'],
                            fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief='flat',
                            padx=30,
                            pady=10,
                            cursor='hand2',
                            activebackground='#5ed9c9')
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(btn_frame,
                              text="❌ 取消",
                              command=dialog.destroy,
                              bg=self.COLORS['bg_tertiary'],
                              fg=self.COLORS['text_primary'],
                              font=('Segoe UI', 10),
                              relief='flat',
                              padx=30,
                              pady=10,
                              cursor='hand2',
                              activebackground=self.COLORS['bg_hover'])
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        value_text.focus()
    
    def delete_item(self):
        """删除配置项"""
        if not self.current_group:
            messagebox.showwarning("警告", "请先选择一个配置组")
            return
        
        selection = self.item_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个配置项")
            return
        
        item_values = self.item_tree.item(selection[0])['values']
        key = item_values[0]
        
        if not messagebox.askyesno("确认删除", f"确定要删除配置项 '{key}' 吗？\n\n此操作不可撤销！"):
            return
        
        try:
            filters = {"group_id": self.current_group["id"], "key": key}
            
            if self.use_rest_api:
                self._rest_api_delete("config_items", filters)
            else:
                self.client.table("config_items")\
                    .delete()\
                    .eq("group_id", self.current_group["id"])\
                    .eq("key", key)\
                    .execute()
            
            messagebox.showinfo("成功", f"配置项 '{key}' 已删除")
            self.refresh_items()
        except Exception as e:
            messagebox.showerror("错误", f"删除配置项失败: {str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = ModernConfigManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
