#!/usr/bin/env python3
"""
创建 Notion 复习数据库
自动创建符合间隔复习系统要求的数据库结构
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_VERSION = '2022-06-28'

def create_review_database():
    """创建复习数据库"""
    
    # 数据库 schema
    database_schema = {
        "parent": {
            "type": "page_id",
            "page_id": os.getenv('NOTION_PARENT_PAGE_ID')  # 使用父页面ID
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "文化遗产学习复习数据库"
                }
            }
        ],
        "properties": {
            "Name": {
                "title": {}
            },
            "Source": {
                "rich_text": {}
            },
            "Tags": {
                "multi_select": {
                    "options": [
                        {"name": "计算机视觉", "color": "blue"},
                        {"name": "三维重建", "color": "green"},
                        {"name": "文化遗产", "color": "red"},
                        {"name": "机器学习", "color": "purple"},
                        {"name": "数据处理", "color": "orange"},
                        {"name": "可视化", "color": "pink"}
                    ]
                }
            },
            "Related Notes": {
                "rich_text": {}
            },
            "Review Count": {
                "number": {
                    "format": "number"
                }
            },
            "Next Review": {
                "date": {}
            },
            "Last Review": {
                "date": {}
            },
            "Last Quality": {
                "number": {
                    "format": "number"
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "未复习", "color": "gray"},
                        {"name": "进行中", "color": "yellow"},
                        {"name": "已掌握", "color": "green"}
                    ]
                }
            }
        }
    }
    
    headers = {
        'Authorization': f'Bearer {NOTION_API_KEY}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION
    }
    
    print("正在创建 Notion 复习数据库...")
    
    response = requests.post(
        'https://api.notion.com/v1/databases',
        headers=headers,
        json=database_schema
    )
    
    if response.status_code == 200:
        db_data = response.json()
        db_id = db_data['id']
        
        print(f"✅ 复习数据库创建成功!")
        print(f"\n数据库 ID: {db_id}")
        print(f"\n请将以下内容添加到 .env 文件:")
        print(f"NOTION_REVIEW_DB_ID={db_id}")
        print(f"\n同时添加到 GitHub Secrets:")
        print(f"  1. 进入 Heritage-Learning-System 仓库")
        print(f"  2. Settings → Secrets and variables → Actions")
        print(f"  3. 添加 NOTION_REVIEW_DB_ID = {db_id}")
        
        # 保存到 notion_databases.json
        try:
            with open('notion_databases.json', 'r', encoding='utf-8') as f:
                databases = json.load(f)
        except FileNotFoundError:
            databases = {}
        
        databases['review_database_id'] = db_id
        
        with open('notion_databases.json', 'w', encoding='utf-8') as f:
            json.dump(databases, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 数据库 ID 已保存到 notion_databases.json")
        
        return db_id
    else:
        print(f"❌ 创建失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        return None

def get_parent_page():
    """获取任务管理数据库的父页面ID"""
    
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    headers = {
        'Authorization': f'Bearer {NOTION_API_KEY}',
        'Notion-Version': NOTION_VERSION
    }
    
    response = requests.get(
        f'https://api.notion.com/v1/databases/{database_id}',
        headers=headers
    )
    
    if response.status_code == 200:
        db_data = response.json()
        parent = db_data.get('parent', {})
        
        if parent.get('type') == 'page_id':
            return parent['page_id']
        elif parent.get('type') == 'workspace':
            print("⚠️ 任务管理数据库直接在工作空间下，需要手动指定父页面")
            print("请提供一个 Notion 页面 ID 作为复习数据库的父页面")
            return None
    
    return None

if __name__ == '__main__':
    if not NOTION_API_KEY:
        print("❌ 错误: 未找到 NOTION_API_KEY")
        print("请确保 .env 文件中配置了 NOTION_API_KEY")
        sys.exit(1)
    
    create_review_database()
