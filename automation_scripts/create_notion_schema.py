"""
create_notion_schema.py

说明：此脚本使用 Notion REST API 在指定父页面下自动创建 6 个数据库（Course, Task, Daily Progress, Templates, Important Events, Resources）。

运行前：
- 在仓库根目录创建 `.env`，包含：
  NOTION_API_KEY=...
  NOTION_PARENT_PAGE_ID=...

运行：
  powershell> venv\Scripts\Activate.ps1
  powershell> pip install requests python-dotenv
  powershell> python create_notion_schema.py

注意：Notion integration 必须已被添加到目标父页面的共享权限中。

"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_PARENT_PAGE_ID = os.getenv('NOTION_PARENT_PAGE_ID')

if not NOTION_API_KEY or not NOTION_PARENT_PAGE_ID:
    print("请先在 .env 中设置 NOTION_API_KEY 和 NOTION_PARENT_PAGE_ID")
    exit(1)

BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}


def create_database(title: str, properties: dict):
    url = f"{BASE_URL}/databases"
    payload = {
        "parent": {"type": "page_id", "page_id": NOTION_PARENT_PAGE_ID},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties
    }

    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code == 200:
        data = r.json()
        db_id = data.get('id')
        print(f"创建数据库成功: {title} -> {db_id}")
        return db_id
    else:
        print(f"创建数据库失败: {title}")
        print(r.status_code, r.text)
        return None


# 定义六个数据库的 properties（简化版，满足自动化与基本字段）
COURSE_PROPERTIES = {
    "Name": {"title": {}},
    "Category": {"select": {"options": [
        {"name": "AI算法"}, {"name": "3D建模"}, {"name": "前端开发"}, {"name": "后端开发"}, {"name": "数学基础"}, {"name": "英语"}, {"name": "考试准备"}, {"name": "工作任务"}
    ]}},
    "Start Date": {"date": {}},
    "End Date": {"date": {}},
    "Weekly Hours": {"number": {}},
    "Priority": {"select": {"options": [
        {"name": "P0-极高"},{"name": "P1-高"},{"name": "P2-中"},{"name": "P3-低"}
    ]}},
    "Status": {"select": {"options": [{"name": "未开始"},{"name": "进行中"},{"name": "已完成"},{"name": "暂停"}]}},
    "Resources": {"rich_text": {}}
}

TASK_PROPERTIES = {
    "Title": {"title": {}},
    "Type": {"select": {"options": [{"name": "讲座"},{"name": "作业"},{"name": "项目"},{"name": "复习"},{"name": "考试"},{"name": "阅读"},{"name": "其他"}]}},
    "Due Date": {"date": {}},
    "Estimated Hours": {"number": {}},
    "Actual Hours": {"number": {}},
    "Priority": {"select": {"options": [{"name": "P0-极高"},{"name": "P1-高"},{"name": "P2-中"},{"name": "P3-低"}]}},
    "Status": {"select": {"options": [{"name": "未开始"},{"name": "进行中"},{"name": "已完成"},{"name": "延期"},{"name": "取消"}]}},
    "Progress": {"number": {}},
    "Need AI Feedback": {"checkbox": {}},
    "Review Schedule": {"multi_select": {"options": [{"name": "D+1"},{"name": "D+3"},{"name": "D+7"},{"name": "D+14"},{"name": "D+30"}]}},
    "Note Link": {"rich_text": {}},
    "Tags": {"multi_select": {"options": [{"name": "考试周"},{"name": "突发"},{"name": "延期"},{"name": "加急"}]}}
}

PROGRESS_PROPERTIES = {
    "Title": {"title": {}},
    "Date": {"date": {}},
    "Duration Hours": {"number": {}},
    "Learning Content": {"rich_text": {}},
    "Efficiency Score": {"number": {}},
    "Learning Method": {"select": {"options": [{"name": "视频"},{"name": "阅读"},{"name": "编码"},{"name": "讨论"},{"name": "实验"}]}},
    "Notes Count": {"number": {}},
    "Questions": {"rich_text": {}},
    "Completed Tasks": {"number": {}},
    "Reflection": {"rich_text": {}},
    "Evidence": {"rich_text": {}}
}

TEMPLATE_PROPERTIES = {
    "Name": {"title": {}},
    "Type": {"select": {"options": [{"name": "周计划"},{"name": "日计划"},{"name": "笔记"},{"name": "费曼讲解"},{"name": "复习卡片"},{"name": "项目提案"}]}},
    "Content": {"rich_text": {}},
    "Last Used": {"date": {}},
    "Usage Count": {"number": {}},
    "Tags": {"multi_select": {"options": [{"name": "模板"}]}}
}

EVENT_PROPERTIES = {
    "Name": {"title": {}},
    "Type": {"select": {"options": [{"name": "考试"},{"name": "工作截止"},{"name": "会议"},{"name": "假期"}] }},
    "Date": {"date": {}},
    "Duration": {"number": {}},
    "Priority": {"select": {"options": [{"name": "P0-极高"},{"name": "P1-高"},{"name": "P2-中"},{"name": "P3-低"}]}},
    "Prep Progress": {"number": {}},
    "Reminders": {"multi_select": {"options": [{"name": "-7天"},{"name": "-3天"},{"name": "-1天"},{"name": "当天上午"}]}}
}

RESOURCE_PROPERTIES = {
    "Name": {"title": {}},
    "Type": {"select": {"options": [{"name": "教程"},{"name": "论文"},{"name": "代码"},{"name": "工具"},{"name": "数据集"},{"name": "视频"}] }},
    "URL": {"url": {}},
    "Priority": {"select": {"options": [{"name": "P0-极高"},{"name": "P1-高"},{"name": "P2-中"},{"name": "P3-低"}]}},
    "Status": {"select": {"options": [{"name": "未读"},{"name": "阅读中"},{"name": "已读"},{"name": "已归档"}] }},
    "Notes": {"rich_text": {}},
    "Tags": {"multi_select": {"options": [{"name": "重要"},{"name": "必读"}]}}
}


def main():
    print("开始创建 Notion 数据库（请确保 Integration 已共享到父页面）\n")

    created = {}
    created['Course Management'] = create_database('Course Management', COURSE_PROPERTIES)
    created['Task Management'] = create_database('Task Management', TASK_PROPERTIES)
    created['Daily Progress'] = create_database('Daily Progress', PROGRESS_PROPERTIES)
    created['Learning Templates'] = create_database('Learning Templates', TEMPLATE_PROPERTIES)
    created['Important Events'] = create_database('Important Events', EVENT_PROPERTIES)
    created['Learning Resources'] = create_database('Learning Resources', RESOURCE_PROPERTIES)

    print('\n创建结果（数据库名: database_id）：')
    print(json.dumps(created, indent=2, ensure_ascii=False))

    # 保存到文件，供后续脚本自动填充 relation 使用
    out_path = os.path.join(os.path.dirname(__file__), 'notion_databases.json')
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(created, f, indent=2, ensure_ascii=False)
        print(f'已将 database id 保存到: {out_path}')
    except Exception as e:
        print('保存 database id 到文件失败:', e)

    print('\n创建完成。请在 Notion 中打开父页面验证。若需自动填充 relation 字段，请运行 fill_relations.py')


if __name__ == '__main__':
    main()
