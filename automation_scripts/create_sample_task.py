"""
create_sample_task.py

快速创建一个示例任务到 Task Management 数据库
"""
import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
NOTION_API_KEY = os.getenv('NOTION_API_KEY')

# 从 JSON 读取 Task DB ID
json_path = os.path.join(os.path.dirname(__file__), 'notion_databases.json')
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
TASK_DB_ID = data.get('Task Management')

HEADERS = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

# 创建示例任务
url = f'https://api.notion.com/v1/pages'
payload = {
    'parent': {'database_id': TASK_DB_ID},
    'properties': {
        'Title': {
            'title': [{'text': {'content': '学习 Three.js 光照系统'}}]
        },
        'Type': {
            'select': {'name': '📺 讲座学习'}
        },
        'Due Date': {
            'date': {'start': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}
        },
        'Priority': {
            'select': {'name': '🟠 P1-高'}
        },
        'Status': {
            'select': {'name': '🔄 进行中'}
        },
        'Progress': {
            'number': 30
        },
        'Estimated Hours': {
            'number': 5
        },
        'Tags': {
            'multi_select': [
                {'name': '#考试周'},
                {'name': '#需AI反馈'}
            ]
        },
        'Note Link': {
            'rich_text': [{'text': {'content': 'obsidian://vault/notes/threejs-lighting'}}]
        }
    }
}

r = requests.post(url, headers=HEADERS, json=payload)
if r.status_code == 200:
    print('✅ 示例任务创建成功!')
    print(f"任务 ID: {r.json()['id']}")
else:
    print(f'❌ 创建失败: {r.status_code}')
    print(r.text)
