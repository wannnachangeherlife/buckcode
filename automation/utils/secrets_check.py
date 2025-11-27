"""
secrets_check.py

验证 GitHub Actions Secrets 是否存在，并进行基本连通性检测。
不会写入任何外部系统。
"""
import os
import sys
import json
import smtplib
import requests

REQUIRED_SECRETS = [
    'NOTION_API_KEY',
    'NOTION_DATABASE_ID',
    'GH_TOKEN',
    'GH_REPO',
    'AI_API_KEY',
    'AI_BASE_URL',
    'AI_MODEL',
    'EMAIL_USER',
    'EMAIL_PASSWORD',
    'EMAIL_SMTP_SERVER',
    'EMAIL_SMTP_PORT',
]


def check_presence():
    missing = []
    for key in REQUIRED_SECRETS:
        if not os.getenv(key):
            missing.append(key)
    return missing


def check_notion():
    api_key = os.getenv('NOTION_API_KEY')
    db_id = os.getenv('NOTION_DATABASE_ID')
    if not api_key or not db_id:
        return {'ok': False, 'error': 'Notion secrets missing'}
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    url = f'https://api.notion.com/v1/databases/{db_id}/query'
    try:
        r = requests.post(url, headers=headers, json={'page_size': 1}, timeout=10)
        return {'ok': r.status_code in (200, 400), 'status': r.status_code}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def check_github():
    token = os.getenv('GH_TOKEN')
    repo = os.getenv('GH_REPO')
    if not token or not repo:
        return {'ok': False, 'error': 'GitHub secrets missing'}
    owner, name = repo.split('/')
    url = f'https://api.github.com/repos/{owner}/{name}'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github+json'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return {'ok': r.status_code == 200, 'status': r.status_code}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def check_ai():
    base = os.getenv('AI_BASE_URL')
    key = os.getenv('AI_API_KEY')
    model = os.getenv('AI_MODEL')
    if not base or not key or not model:
        return {'ok': False, 'error': 'AI secrets missing'}
    # 仅进行基本可达性检测
    try:
        r = requests.get(base, timeout=10)
        return {'ok': r.status_code in (200, 403, 404), 'status': r.status_code}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def check_email():
    server = os.getenv('EMAIL_SMTP_SERVER')
    port = int(os.getenv('EMAIL_SMTP_PORT') or '0')
    user = os.getenv('EMAIL_USER')
    pwd = os.getenv('EMAIL_PASSWORD')
    if not server or not port or not user or not pwd:
        return {'ok': False, 'error': 'Email secrets missing'}
    try:
        with smtplib.SMTP(server, port, timeout=10) as s:
            s.starttls()
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def main():
    report = {
        'missing_secrets': check_presence(),
        'notion': check_notion(),
        'github': check_github(),
        'ai': check_ai(),
        'email': check_email(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # 若有缺失或关键检查失败，退出非零码以便 Actions 标红
    if report['missing_secrets']:
        sys.exit(1)
    if not report['notion'].get('ok') or not report['github'].get('ok'):
        sys.exit(1)

if __name__ == '__main__':
    main()
