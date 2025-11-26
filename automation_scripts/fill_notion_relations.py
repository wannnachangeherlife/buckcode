"""
fill_notion_relations.py

用途：自动将已创建的 Notion 数据库 ID 填充到各数据库的 Relation 字段，实现表间关联。

前提：
- 已运行 create_notion_schema.py 并获得所有 database_id
- 在 .env 中配置各数据库 ID，例如：
  COURSE_DB_ID=xxx
  TASK_DB_ID=xxx
  PROGRESS_DB_ID=xxx
  TEMPLATE_DB_ID=xxx
  EVENT_DB_ID=xxx
  RESOURCE_DB_ID=xxx
  NOTION_API_KEY=xxx

运行：
  venv\Scripts\Activate.ps1
  python fill_notion_relations.py

注意：已启用双向关联（dual_property），在目标数据库自动创建反向属性。
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
HEADERS = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}
BASE_URL = 'https://api.notion.com/v1'

# 读取数据库 ID
COURSE_DB_ID = os.getenv('COURSE_DB_ID')
TASK_DB_ID = os.getenv('TASK_DB_ID')
PROGRESS_DB_ID = os.getenv('PROGRESS_DB_ID')
TEMPLATE_DB_ID = os.getenv('TEMPLATE_DB_ID')
EVENT_DB_ID = os.getenv('EVENT_DB_ID')
RESOURCE_DB_ID = os.getenv('RESOURCE_DB_ID')

# 若环境变量缺失，则尝试从 automation_scripts/notion_databases.json 读取
if not all([COURSE_DB_ID, TASK_DB_ID, PROGRESS_DB_ID, TEMPLATE_DB_ID, EVENT_DB_ID, RESOURCE_DB_ID]):
    json_path = os.path.join(os.path.dirname(__file__), r'notion_databases.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            COURSE_DB_ID = COURSE_DB_ID or data.get('Course Management')
            TASK_DB_ID = TASK_DB_ID or data.get('Task Management')
            PROGRESS_DB_ID = PROGRESS_DB_ID or data.get('Daily Progress')
            TEMPLATE_DB_ID = TEMPLATE_DB_ID or data.get('Learning Templates')
            EVENT_DB_ID = EVENT_DB_ID or data.get('Important Events')
            RESOURCE_DB_ID = RESOURCE_DB_ID or data.get('Learning Resources')
        except Exception:
            pass

# 需要填充的数据库及其 Relation 字段
relations = [
    # 课程 ↔ 任务
    {
        'db_id': COURSE_DB_ID,
        'field': 'Related Tasks',
        'target_db_id': TASK_DB_ID,
        'synced_property_name': 'Related Course'
    },
    {
        'db_id': TASK_DB_ID,
        'field': 'Related Course',
        'target_db_id': COURSE_DB_ID,
        'synced_property_name': 'Related Tasks'
    },
    # 进度 ↔ 课程（为课程侧自动创建“Progress Items”反向属性）
    {
        'db_id': PROGRESS_DB_ID,
        'field': 'Course',
        'target_db_id': COURSE_DB_ID,
        'synced_property_name': 'Progress Items'
    },
    # 事件 ↔ 课程（为课程侧自动创建“Related Events”）
    {
        'db_id': EVENT_DB_ID,
        'field': 'Related Courses',
        'target_db_id': COURSE_DB_ID,
        'synced_property_name': 'Related Events'
    },
    # 资源 ↔ 课程（为课程侧自动创建“Related Resources”）
    {
        'db_id': RESOURCE_DB_ID,
        'field': 'Related Courses',
        'target_db_id': COURSE_DB_ID,
        'synced_property_name': 'Related Resources'
    }
]

def update_relation(db_id, field, target_db_id, synced_property_name=None):
    url = f'{BASE_URL}/databases/{db_id}'
    # 使用新版 schema：优先创建双向关联（dual_property），自动在对侧生成/同步属性
    relation_obj = {
        'database_id': target_db_id,
        'type': 'dual_property'
    }
    if synced_property_name:
        relation_obj['dual_property'] = {
            'synced_property_name': synced_property_name
        }
    else:
        # 回退：若未提供反向属性名，则以单向关联创建
        relation_obj['type'] = 'single_property'
        relation_obj['single_property'] = {}

    payload = {
        'properties': {
            field: {
                'relation': relation_obj
            }
        }
    }
    r = requests.patch(url, headers=HEADERS, json=payload)
    if r.status_code == 200:
        print(f'已更新 {db_id} 的 {field} 关联到 {target_db_id}')
    else:
        print(f'更新失败: {db_id} 的 {field} -> {target_db_id}', r.status_code, r.text)


def main():
    for rel in relations:
        if rel['db_id'] and rel['target_db_id']:
            update_relation(rel['db_id'], rel['field'], rel['target_db_id'], rel.get('synced_property_name'))
        else:
            print(f'缺少数据库 ID: {rel}')

if __name__ == '__main__':
    main()
