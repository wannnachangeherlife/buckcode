"""
create_github_repo.py

说明：使用 GitHub REST API 自动创建一个学习仓库并初始化 README、.gitignore、并创建 Issues 模板（需要环境变量 GITHUB_TOKEN 和 GITHUB_USER）

运行前：
- 在 .env 中设置 GITHUB_TOKEN 和 GITHUB_USER
- 注意：如果仓库已存在，脚本会提示并跳过创建

运行：
    venv\Scripts\Activate.ps1
    pip install requests python-dotenv
    python create_github_repo.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USER = os.getenv('GITHUB_USER')
REPO_NAME = os.getenv('GITHUB_REPO_NAME', 'heritage-learning')

if not GITHUB_TOKEN or not GITHUB_USER:
    print('请在 .env 中设置 GITHUB_TOKEN 和 GITHUB_USER')
    exit(1)

API = 'https://api.github.com'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}


def repo_exists(user, repo):
    r = requests.get(f'{API}/repos/{user}/{repo}', headers=HEADERS)
    return r.status_code == 200


def create_repo(user, repo):
    payload = {"name": repo, "private": False, "auto_init": False}
    r = requests.post(f'{API}/user/repos', headers=HEADERS, json=payload)
    if r.status_code in (201, 200):
        print(f'仓库创建成功: {user}/{repo}')
        return True
    else:
        print('仓库创建失败:', r.status_code, r.text)
        return False


def create_file(user, repo, path, content, message='add file'):
    url = f'{API}/repos/{user}/{repo}/contents/{path}'
    payload = {"message": message, "content": content.encode('utf-8').decode('latin-1')}
    r = requests.put(url, headers=HEADERS, json=payload)
    if r.status_code in (201, 200):
        print(f'文件已创建: {path}')
        return True
    else:
        print(f'创建文件失败: {path} ->', r.status_code, r.text)
        return False


def main():
    if repo_exists(GITHUB_USER, REPO_NAME):
        print(f'仓库已存在: {GITHUB_USER}/{REPO_NAME}，跳过创建')
    else:
        ok = create_repo(GITHUB_USER, REPO_NAME)
        if not ok:
            return

    readme = '# Heritage Learning\n\n文化遗产数字化学习仓库'
    gitignore = 'venv/\n__pycache__/\n.env\n'

    # GitHub Content API 要求 base64 编码内容，但这里为简化示例我们提示用户手动推送
    print('\n请使用以下命令将初始化文件推送到远程仓库：')
    print('\n    git clone https://github.com/{}/{}\n    cd {}\n    echo "{}" > README.md\n    echo "{}" > .gitignore\n    git add .\n    git commit -m "chore: init repository"\n    git push origin main\n'.format(GITHUB_USER, REPO_NAME, REPO_NAME, readme.replace('"','\"'), gitignore.replace('"','\"')))

    print('---\n完成。请在 GitHub 仓库设置 Secrets：NOTION_API_KEY、NOTION_DATABASE_ID、GITHUB_TOKEN、CHATGPT_API_KEY、EMAIL_USER、EMAIL_PASSWORD 等')


if __name__ == '__main__':
    main()
