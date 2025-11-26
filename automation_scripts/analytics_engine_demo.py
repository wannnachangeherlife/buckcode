"""
analytics_engine_demo.py

用途：演示如何从 Notion Progress 表读取数据并生成学习统计报告（支持 dry-run）。

前提：.env 已配置 NOTION_API_KEY 和 PROGRESS_DB_ID

运行：
  python automation_scripts\\analytics_engine_demo.py
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
PROGRESS_DB_ID = os.getenv('PROGRESS_DB_ID')
HEADERS = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}
BASE_URL = 'https://api.notion.com/v1'
DRY_RUN = os.getenv('DRY_RUN', 'True').lower() not in ('false', '0', 'no')


def fetch_progress(last_days=7):
    if DRY_RUN:
        print('DRY_RUN: 模拟 Progress 数据返回')
        return [
            {'Date': '2025-11-20', 'Duration Hours': 2, 'Course': 'PyTorch深度学习', 'Efficiency Score': 8},
            {'Date': '2025-11-21', 'Duration Hours': 1.5, 'Course': '3D建模', 'Efficiency Score': 7},
            {'Date': '2025-11-22', 'Duration Hours': 2.5, 'Course': 'PyTorch深度学习', 'Efficiency Score': 9},
        ]
    url = f'{BASE_URL}/databases/{PROGRESS_DB_ID}/query'
    since = (datetime.now() - timedelta(days=last_days)).strftime('%Y-%m-%d')
    payload = {
        'filter': {
            'property': 'Date',
            'date': {'on_or_after': since}
        }
    }
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code == 200:
        results = r.json().get('results', [])
        rows = []
        for item in results:
            props = item.get('properties', {})
            rows.append({
                'Date': props.get('Date', {}).get('date', {}).get('start'),
                'Duration Hours': props.get('Duration Hours', {}).get('number', 0),
                'Course': props.get('Course', {}).get('relation', [{}])[0].get('id', ''),
                'Efficiency Score': props.get('Efficiency Score', {}).get('number', 0)
            })
        return rows
    else:
        print('API 查询失败:', r.status_code, r.text)
        return []

def generate_report(rows):
    total_hours = sum(r['Duration Hours'] for r in rows)
    course_hours = {}
    for r in rows:
        course = r['Course']
        course_hours[course] = course_hours.get(course, 0) + r['Duration Hours']
    avg_eff = sum(r['Efficiency Score'] for r in rows) / len(rows) if rows else 0
    report = {
        'period': f'最近{len(rows)}天',
        'total_hours': total_hours,
        'course_hours': course_hours,
        'avg_efficiency': round(avg_eff, 2)
    }
    print('统计报告:', report)
    return report

def main():
    rows = fetch_progress()
    generate_report(rows)

if __name__ == '__main__':
    main()
