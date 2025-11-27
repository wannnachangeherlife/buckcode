"""
学习系统工作流调度器
===================

统一调度四端协作流程：
1. Obsidian → Notion 同步 (知识沉淀)
2. 生成复习计划 (间隔复习)
3. VSCode 任务同步 (Notion ↔ GitHub)
4. AI 辅助分析 (学习建议)

作者：Heritage Learning System
版本：v2.0
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入各模块
try:
    from obsidian_to_notion_sync import ObsidianNotionSync
    from spaced_repetition import SpacedRepetitionEngine
    from learning_system_core import SyncEngine, NotificationEngine, AnalyticsEngine
except ImportError as e:
    print(f"错误: 无法导入模块 - {e}")
    print("请确保所有依赖已安装: pip install -r requirements.txt")
    sys.exit(1)

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """工作流编排器"""
    
    def __init__(self):
        self.obsidian_vault = os.getenv('OBSIDIAN_VAULT_PATH', './obsidian_vault')
        self.notion_db = os.getenv('NOTION_DATABASE_ID')
        self.review_db = os.getenv('NOTION_REVIEW_DB_ID')
    
    def run_morning_workflow(self):
        """晨间工作流: 生成今日计划"""
        logger.info("=" * 60)
        logger.info("🌅 晨间工作流启动")
        logger.info("=" * 60)
        
        # 1. 生成复习计划
        logger.info("\n📚 步骤 1/2: 生成今日复习计划")
        if self.review_db:
            try:
                engine = SpacedRepetitionEngine(self.review_db)
                plan = engine.generate_review_plan()
                engine.export_to_obsidian(plan)
                logger.info(f"✓ 今日待复习: {plan['total_count']} 条")
            except Exception as e:
                logger.error(f"✗ 复习计划生成失败: {e}")
        else:
            logger.warning("⚠ 跳过: 未设置 NOTION_REVIEW_DB_ID")
        
        # 2. 同步 GitHub Issues 到 Notion
        logger.info("\n📥 步骤 2/2: 同步 GitHub 任务")
        try:
            SyncEngine.sync_github_to_notion()
            logger.info("✓ GitHub → Notion 同步完成")
        except Exception as e:
            logger.error(f"✗ 同步失败: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 晨间工作流完成")
        logger.info("=" * 60)
    
    def run_evening_workflow(self):
        """晚间工作流: 整理与同步"""
        logger.info("=" * 60)
        logger.info("🌙 晚间工作流启动")
        logger.info("=" * 60)
        
        # 1. Obsidian → Notion 同步
        logger.info("\n📝 步骤 1/4: Obsidian → Notion 同步")
        if self.review_db:
            try:
                sync = ObsidianNotionSync(self.obsidian_vault, self.review_db)
                sync.sync_all()
            except Exception as e:
                logger.error(f"✗ Obsidian 同步失败: {e}")
        else:
            logger.warning("⚠ 跳过: 未设置 NOTION_REVIEW_DB_ID")
        
        # 2. Notion → GitHub 同步
        logger.info("\n📤 步骤 2/4: Notion → GitHub 同步")
        try:
            SyncEngine.sync_notion_to_github()
            logger.info("✓ Notion → GitHub 同步完成")
        except Exception as e:
            logger.error(f"✗ 同步失败: {e}")
        
        # 3. 发送每日摘要
        logger.info("\n📧 步骤 3/4: 发送每日摘要")
        try:
            NotificationEngine.send_email_summary()
            logger.info("✓ 邮件发送完成")
        except Exception as e:
            logger.error(f"✗ 邮件发送失败: {e}")
        
        # 4. 生成学习统计
        logger.info("\n📊 步骤 4/4: 生成学习统计")
        try:
            AnalyticsEngine.export_analytics_json()
            logger.info("✓ 统计数据已导出")
        except Exception as e:
            logger.error(f"✗ 统计生成失败: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 晚间工作流完成")
        logger.info("=" * 60)
    
    def run_full_workflow(self):
        """完整工作流: 晨间 + 晚间"""
        self.run_morning_workflow()
        print("\n" * 2)
        self.run_evening_workflow()

def main():
    """主程序"""
    import argparse
    
    parser = argparse.ArgumentParser(description='学习系统工作流调度器')
    parser.add_argument(
        'workflow',
        choices=['morning', 'evening', 'full'],
        help='工作流类型: morning(晨间), evening(晚间), full(完整)'
    )
    
    args = parser.parse_args()
    
    orchestrator = WorkflowOrchestrator()
    
    if args.workflow == 'morning':
        orchestrator.run_morning_workflow()
    elif args.workflow == 'evening':
        orchestrator.run_evening_workflow()
    else:
        orchestrator.run_full_workflow()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 无参数时默认运行完整流程
        print("未指定工作流类型,运行完整流程...")
        print("提示: 可使用参数指定工作流类型")
        print("  python workflow.py morning  # 晨间工作流")
        print("  python workflow.py evening  # 晚间工作流")
        print("  python workflow.py full     # 完整工作流")
        print("\n" + "=" * 60 + "\n")
        
        WorkflowOrchestrator().run_full_workflow()
    else:
        main()
