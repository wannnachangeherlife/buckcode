"""
check_env.py

用途：快速检查所需环境变量是否已在 `.env` 中配置，便于在运行自动化脚本前进行验证。

运行：
powershell> venv\Scripts\Activate.ps1
powershell> python check_env.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

required = [
    'NOTION_API_KEY',
    'NOTION_PARENT_PAGE_ID',
    'GITHUB_TOKEN',
    'GITHUB_REPO',
    'AI_API_KEY',  # 支持 DeepSeek/ChatGPT/通义千问等
    'EMAIL_USER',
    'EMAIL_PASSWORD'
]

missing = []
for k in required:
    if not os.getenv(k):
        missing.append(k)

if not missing:
    print("环境变量检查通过：所有必需项已配置。")
else:
    print("缺少以下环境变量，请编辑 .env 并添加：")
    for k in missing:
        print(f" - {k}")
    print("\n示例 .env 内容：")
    print("NOTION_API_KEY=your_notion_api_key_here")
    print("NOTION_PARENT_PAGE_ID=your_parent_page_id_here")
    print("GITHUB_TOKEN=your_github_token_here")
    print("GITHUB_REPO=your_username/your_repo")
    print("AI_API_KEY=your_deepseek_or_openai_api_key")
    print("AI_BASE_URL=https://api.deepseek.com  # 可选，默认 DeepSeek")
    print("AI_MODEL=deepseek-chat  # 可选，默认 deepseek-chat")
    print("EMAIL_USER=your_email@example.com")
    print("EMAIL_PASSWORD=your_email_app_password")
