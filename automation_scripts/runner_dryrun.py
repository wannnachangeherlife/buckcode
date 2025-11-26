"""
runner_dryrun.py

用途：在本地以 dry-run 模式调用学习系统各组件（不触发外部API写入），用于检查配置与工作流。

运行：
    venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python runner_dryrun.py

说明：脚本会检查环境变量并模拟 Notion->GitHub 同步的逻辑，打印将要执行的操作而不实际调用远程写入接口（除非设置 DRY_RUN=False）。
"""

import os
from dotenv import load_dotenv
from automation_scripts import learning_system_core as core

load_dotenv()

DRY_RUN = os.getenv('DRY_RUN', 'True').lower() != 'false'


def main():
    print('Dry-run 学习系统启动，DRY_RUN=', DRY_RUN)

    # 仅调用部分逻辑进行本地验证
    core.logger.info('模拟 Notion->GitHub 同步（不实际创建 Issue）')

    # 模拟查询（会调用 NotionClient.query_database, 但是这里我们不提供 API keys）
    print('注意：若未配置 Notion API Key，Notion 查询会返回空列表。')

    # 调用检查函数
    core.SyncEngine.sync_notion_to_github()
    core.NotificationEngine.check_deadline_reminders()
    report = core.AnalyticsEngine.generate_weekly_report()
    print('模拟周报：', report)


if __name__ == '__main__':
    main()
