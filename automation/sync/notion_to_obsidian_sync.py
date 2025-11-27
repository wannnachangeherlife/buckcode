"""
notion_to_obsidian_sync.py

用途：自动将 Notion 中的任务/笔记内容同步到本地 Obsidian Vault（以 Markdown 文件形式），支持 dry-run。

前提：.env 已配置 NOTION_API_KEY、NOTION_DATABASE_ID、OBSIDIAN_VAULT_PATH

运行：
  python automation_scripts\\notion_to_obsidian_sync.py

注意：默认同步 Task Management 数据库，可通过 NOTION_DATABASE_ID 环境变量或 notion_databases.json 自动获取。
"""
import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

# 若环境变量未设置，从 notion_databases.json 读取 Task Management ID
if not NOTION_DATABASE_ID:
    json_path = os.path.join(os.path.dirname(__file__), 'notion_databases.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            NOTION_DATABASE_ID = data.get('Task Management')
            print(f'从 notion_databases.json 读取 Task Management ID: {NOTION_DATABASE_ID}')
        except Exception as e:
            print(f'读取 notion_databases.json 失败: {e}')

OBSIDIAN_VAULT_PATH = os.getenv('OBSIDIAN_VAULT_PATH', './obsidian_vault')
DRY_RUN = os.getenv('DRY_RUN', 'True').lower() not in ('false', '0', 'no')
HEADERS = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}
BASE_URL = 'https://api.notion.com/v1'


def fetch_tasks():
    """从 Notion Task Management 数据库查询未完成任务"""
    url = f'{BASE_URL}/databases/{NOTION_DATABASE_ID}/query'
    payload = {
        'filter': {
            'property': 'Status',
            'select': {'does_not_equal': '已完成'}
        }
    }
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code == 200:
        return r.json().get('results', [])
    else:
        print('API 查询失败:', r.status_code, r.text)
        return []


def notion_task_to_md(task):
    """将 Notion 任务转换为 Markdown 格式"""
    props = task.get('properties', {})
    
    # 安全获取 title
    title_prop = props.get('Title', {}).get('title', [])
    title = title_prop[0].get('text', {}).get('content', 'Untitled') if title_prop else 'Untitled'
    
    # 获取其他属性
    due_date_obj = props.get('Due Date', {}).get('date')
    due = due_date_obj.get('start', '') if due_date_obj else ''
    
    status_obj = props.get('Status', {}).get('select')
    status = status_obj.get('name', '') if status_obj else ''
    
    priority_obj = props.get('Priority', {}).get('select')
    priority = priority_obj.get('name', '') if priority_obj else ''
    
    progress = props.get('Progress', {}).get('number', 0)
    
    type_obj = props.get('Type', {}).get('select')
    task_type = type_obj.get('name', '') if type_obj else ''
    
    # 获取笔记链接
    note_link_prop = props.get('Note Link', {}).get('rich_text', [])
    note_link = note_link_prop[0].get('text', {}).get('content', '') if note_link_prop else ''
    
    # 获取标签
    tags = props.get('Tags', {}).get('multi_select', [])
    tag_names = [tag.get('name', '') for tag in tags]
    
    # 构建 Markdown
    md_lines = [
        f"# {title}",
        "",
        f"- 类型: {task_type}",
        f"- 截止日期: {due}",
        f"- 状态: {status}",
        f"- 优先级: {priority}",
        f"- 完成度: {progress}%",
        f"- 标签: {', '.join(tag_names)}"
    ]
    
    if note_link:
        md_lines.append(f"- 笔记链接: {note_link}")
    
    md_lines.extend([
        "",
        "---",
        f"同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ""
    ])
    
    return '\n'.join(md_lines)


def save_md(title, md):
    """保存 Markdown 文件到 Obsidian Vault"""
    safe_title = title.replace('/', '_').replace('\\', '_').replace(':', '-')
    path = os.path.join(OBSIDIAN_VAULT_PATH, f'{safe_title}.md')
    
    if DRY_RUN:
        print(f'DRY_RUN: 将生成 Obsidian 笔记 {path}')
        print(f'内容预览:\n{md[:200]}...\n')
    else:
        os.makedirs(OBSIDIAN_VAULT_PATH, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f'已同步到 Obsidian: {path}')


def main():
    """主函数"""
    if not NOTION_DATABASE_ID:
        print('错误: 未找到 NOTION_DATABASE_ID，请在 .env 中设置或确保 notion_databases.json 存在')
        return
    
    tasks = fetch_tasks()
    print(f'共找到 {len(tasks)} 个未完成任务\n')
    
    for t in tasks:
        md = notion_task_to_md(t)
        title_prop = t.get('properties', {}).get('Title', {}).get('title', [])
        title = title_prop[0].get('text', {}).get('content', 'Untitled') if title_prop else 'Untitled'
        save_md(title, md)


if __name__ == '__main__':
    main()
