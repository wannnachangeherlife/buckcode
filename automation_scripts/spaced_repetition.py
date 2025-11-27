"""
间隔复习系统 - 基于艾宾浩斯遗忘曲线
====================================

功能：
1. 根据遗忘曲线计算下次复习时间
2. 从 Notion 复习数据库查询待复习内容
3. 根据复习质量动态调整间隔
4. 推送复习任务到 VSCode/Obsidian

复习间隔：
- 第1次: 5分钟后
- 第2次: 30分钟后
- 第3次: 12小时后
- 第4次: 1天后
- 第5次: 2天后
- 第6次: 4天后
- 第7次: 7天后
- 第8次: 15天后
- 第9次+: 30天后

作者：Heritage Learning System
版本：v1.0
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

# 配置
NOTION_REVIEW_DB_ID = os.getenv('NOTION_REVIEW_DB_ID')
DRY_RUN = os.getenv('DRY_RUN', 'True').lower() not in ('false', '0', 'no')

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spaced_repetition.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 复习间隔配置 ====================

class ReviewIntervals:
    """艾宾浩斯复习间隔"""
    INTERVALS = {
        0: timedelta(minutes=5),      # 第1次
        1: timedelta(minutes=30),     # 第2次
        2: timedelta(hours=12),       # 第3次
        3: timedelta(days=1),         # 第4次
        4: timedelta(days=2),         # 第5次
        5: timedelta(days=4),         # 第6次
        6: timedelta(days=7),         # 第7次
        7: timedelta(days=15),        # 第8次
        8: timedelta(days=30),        # 第9次+
    }
    
    @staticmethod
    def get_next_review_time(review_count: int, quality: int = 3) -> datetime:
        """
        计算下次复习时间
        
        Args:
            review_count: 已复习次数 (0-based)
            quality: 复习质量 (1-5)
                5 - 完美记忆
                4 - 正确但犹豫
                3 - 正确但困难
                2 - 错误但想起来
                1 - 完全忘记
        
        Returns:
            下次复习的时间
        """
        # 质量低于3，重置复习进度
        if quality < 3:
            review_count = max(0, review_count - 2)
        
        # 获取间隔
        interval_key = min(review_count, 8)
        interval = ReviewIntervals.INTERVALS[interval_key]
        
        # 质量调整系数
        quality_factor = {
            5: 1.2,   # 记得很好，延长间隔
            4: 1.0,   # 正常
            3: 0.8,   # 稍微缩短
            2: 0.5,   # 明显缩短
            1: 0.3    # 大幅缩短
        }.get(quality, 1.0)
        
        adjusted_interval = interval * quality_factor
        return datetime.now() + adjusted_interval

# ==================== Notion 客户端 ====================

class NotionClient:
    """Notion API 客户端"""
    BASE_URL = "https://api.notion.com/v1"
    
    @staticmethod
    def _headers():
        api_key = os.getenv('NOTION_API_KEY')
        return {
            "Authorization": f"Bearer {api_key}" if api_key else "",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    @staticmethod
    def query_database(database_id: str, filter_params: Optional[Dict] = None) -> List[Dict]:
        """查询数据库"""
        url = f"{NotionClient.BASE_URL}/databases/{database_id}/query"
        payload = {"filter": filter_params} if filter_params else {}
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 查询 Notion 复习数据库")
                return []
            response = requests.post(url, headers=NotionClient._headers(), json=payload)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            logger.error(f"Notion 查询失败: {e}")
            return []
    
    @staticmethod
    def update_page(page_id: str, properties: Dict) -> bool:
        """更新页面"""
        url = f"{NotionClient.BASE_URL}/pages/{page_id}"
        payload = {"properties": properties}
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 更新复习记录 {page_id}")
                logger.debug(f"属性: {json.dumps(properties, ensure_ascii=False, indent=2)}")
                return True
            response = requests.patch(url, headers=NotionClient._headers(), json=payload)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"更新失败: {e}")
            return False

# ==================== 复习引擎 ====================

class SpacedRepetitionEngine:
    """间隔复习引擎"""
    
    def __init__(self, database_id: str):
        self.database_id = database_id
    
    def get_due_reviews(self) -> List[Dict]:
        """获取今日待复习内容"""
        now = datetime.now().isoformat()
        
        # 查询 Next Review <= 今天 的内容
        filter_params = {
            "and": [
                {
                    "property": "Next Review",
                    "date": {
                        "on_or_before": now
                    }
                },
                {
                    "property": "Status",
                    "select": {
                        "does_not_equal": "已掌握"
                    }
                }
            ]
        }
        
        reviews = NotionClient.query_database(self.database_id, filter_params)
        logger.info(f"📚 发现 {len(reviews)} 条待复习内容")
        return reviews
    
    def record_review(self, page_id: str, quality: int):
        """记录一次复习"""
        # 这里简化处理，实际需要先获取当前的 Review Count
        # 假设通过页面属性获取
        review_count = 0  # TODO: 从页面属性读取
        
        # 计算下次复习时间
        next_review = ReviewIntervals.get_next_review_time(review_count, quality)
        
        # 更新 Notion
        properties = {
            "Review Count": {
                "number": review_count + 1
            },
            "Next Review": {
                "date": {"start": next_review.isoformat()}
            },
            "Last Review": {
                "date": {"start": datetime.now().isoformat()}
            },
            "Last Quality": {
                "number": quality
            }
        }
        
        # 如果复习次数达到阈值且质量高，标记为已掌握
        if review_count >= 6 and quality >= 4:
            properties["Status"] = {"select": {"name": "已掌握"}}
        
        NotionClient.update_page(page_id, properties)
        logger.info(f"✓ 已记录复习: 下次复习时间 {next_review.strftime('%Y-%m-%d %H:%M')}")
    
    def generate_review_plan(self) -> Dict:
        """生成今日复习计划"""
        due_reviews = self.get_due_reviews()
        
        plan = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "total_count": len(due_reviews),
            "reviews": []
        }
        
        for review in due_reviews:
            props = review.get('properties', {})
            
            # 提取标题
            title_prop = props.get('Title', {}).get('title', [])
            title = title_prop[0].get('text', {}).get('content', 'Untitled') if title_prop else 'Untitled'
            
            # 提取标签
            tags_prop = props.get('Tags', {}).get('multi_select', [])
            tags = [tag.get('name', '') for tag in tags_prop]
            
            # 提取复习次数
            review_count = props.get('Review Count', {}).get('number', 0)
            
            plan["reviews"].append({
                "id": review['id'],
                "title": title,
                "tags": tags,
                "review_count": review_count,
                "url": review.get('url', '')
            })
        
        return plan
    
    def export_to_obsidian(self, plan: Dict):
        """导出复习计划到 Obsidian"""
        vault_path = os.getenv('OBSIDIAN_VAULT_PATH', './obsidian_vault')
        review_file = os.path.join(vault_path, f"复习计划-{plan['date']}.md")
        
        content = f"""---
date: {plan['date']}
type: review-plan
total: {plan['total_count']}
---

# 📅 今日复习计划 ({plan['date']})

> 待复习内容: **{plan['total_count']}** 条

"""
        
        for idx, review in enumerate(plan['reviews'], 1):
            content += f"\n## {idx}. {review['title']}\n"
            content += f"- 标签: {', '.join(f'#{tag}' for tag in review['tags'])}\n"
            content += f"- 复习次数: {review['review_count']}\n"
            content += f"- 链接: [打开Notion]({review['url']})\n"
            content += "\n### 复习笔记\n\n"
            content += "<!-- 在此记录复习要点 -->\n\n"
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 导出复习计划到 {review_file}")
                logger.debug(f"内容预览:\n{content[:500]}...")
            else:
                os.makedirs(os.path.dirname(review_file), exist_ok=True)
                with open(review_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✓ 复习计划已导出: {review_file}")
        except Exception as e:
            logger.error(f"导出失败: {e}")

# ==================== 主程序 ====================

def main():
    """主程序"""
    logger.info("=" * 50)
    logger.info("间隔复习系统启动")
    logger.info("=" * 50)
    logger.info(f"DRY_RUN 模式: {'开启' if DRY_RUN else '关闭'}")
    
    if not NOTION_REVIEW_DB_ID:
        logger.error("错误: 未设置 NOTION_REVIEW_DB_ID")
        return
    
    engine = SpacedRepetitionEngine(NOTION_REVIEW_DB_ID)
    
    # 生成今日复习计划
    plan = engine.generate_review_plan()
    
    # 导出到 Obsidian
    engine.export_to_obsidian(plan)
    
    logger.info("=" * 50)
    logger.info("复习计划生成完成")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
