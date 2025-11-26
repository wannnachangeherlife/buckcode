"""
import_week1_tasks.py

快速将第1周任务导入 Notion Task Management
"""
import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
NOTION_API_KEY = os.getenv('NOTION_API_KEY')

# 读取 Task DB ID
json_path = os.path.join(os.path.dirname(__file__), 'notion_databases.json')
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
TASK_DB_ID = data.get('Task Management')

HEADERS = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

# 第1周任务列表
week1_tasks = [
    {
        'title': '环境配置：Python 3.10 + Node.js + Git',
        'type': '🛠️ 项目开发',
        'due_days': 2,
        'priority': '🔴 P0-极高',
        'estimated_hours': 3,
        'tags': ['#环境配置']
    },
    {
        'title': '配置 VS Code 开发环境',
        'type': '🛠️ 项目开发',
        'due_days': 2,
        'priority': '🟠 P1-高',
        'estimated_hours': 2,
        'tags': ['#环境配置']
    },
    {
        'title': 'Python 语法基础复习',
        'type': '📺 讲座学习',
        'due_days': 4,
        'priority': '🟠 P1-高',
        'estimated_hours': 5,
        'tags': ['#基础学习']
    },
    {
        'title': 'Git 基础操作学习',
        'type': '📺 讲座学习',
        'due_days': 5,
        'priority': '🟡 P2-中',
        'estimated_hours': 2,
        'tags': ['#基础学习']
    },
    {
        'title': 'FastAPI Hello World 项目',
        'type': '🛠️ 项目开发',
        'due_days': 6,
        'priority': '🟠 P1-高',
        'estimated_hours': 3,
        'tags': ['#后端开发', '#优质成果']
    },
    {
        'title': 'Three.js 基础示例 - 旋转立方体',
        'type': '🛠️ 项目开发',
        'due_days': 7,
        'priority': '🟠 P1-高',
        'estimated_hours': 4,
        'tags': ['#前端开发', '#优质成果']
    }
]

def create_task(task_info):
    url = 'https://api.notion.com/v1/pages'
    due_date = (datetime.now() + timedelta(days=task_info['due_days'])).strftime('%Y-%m-%d')
    
    payload = {
        'parent': {'database_id': TASK_DB_ID},
        'properties': {
            'Title': {
                'title': [{'text': {'content': task_info['title']}}]
            },
            'Type': {
                'select': {'name': task_info['type']}
            },
            'Due Date': {
                'date': {'start': due_date}
            },
            'Priority': {
                'select': {'name': task_info['priority']}
            },
            'Status': {
                'select': {'name': '⏳ 未开始'}
            },
            'Progress': {
                'number': 0
            },
            'Estimated Hours': {
                'number': task_info['estimated_hours']
            },
            'Tags': {
                'multi_select': [{'name': tag} for tag in task_info['tags']]
            }
        }
    }
    
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code == 200:
        print(f"✅ 已创建: {task_info['title']}")
        return True
    else:
        print(f"❌ 创建失败: {task_info['title']}")
        print(f"   错误: {r.status_code} - {r.text[:200]}")
        return False

def main():
    print("开始导入第1周任务到 Notion...\n")
    success_count = 0
    
    for task in week1_tasks:
        if create_task(task):
            success_count += 1
    
    print(f"\n✅ 完成！成功导入 {success_count}/{len(week1_tasks)} 个任务")
    print("\n💡 提示：访问 Notion Task Management 数据库查看任务")

if __name__ == '__main__':
    main()
