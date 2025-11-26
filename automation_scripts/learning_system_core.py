"""
跨平台学习管理系统 - 核心自动化脚本
===========================================

功能：
1. Notion ↔ GitHub 双向同步
2. 定时提醒与日历集成
3. AI反馈生成
4. 学习统计与可视化数据生成

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
from enum import Enum

# ==================== 配置 ====================

# 加载环境变量
load_dotenv()

# 运行时配置
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

GITHUB_REPO = os.getenv('GITHUB_REPO')  # format: owner/repo
APPLE_CALENDAR_URL = os.getenv('APPLE_CALENDAR_URL')  # CalDAV URL

# DRY_RUN: 若为 True 则不会执行外部写操作（默认 True，便于本地测试）
DRY_RUN = os.getenv('DRY_RUN', 'True').lower() not in ('false', '0', 'no')

def get_notion_api_key():
    return os.getenv('NOTION_API_KEY')

def get_github_token():
    return os.getenv('GITHUB_TOKEN')

def get_ai_api_key():
    """获取 AI API 密钥（支持 DeepSeek/ChatGPT/通义千问等）"""
    return os.getenv('AI_API_KEY') or os.getenv('DEEPSEEK_API_KEY') or os.getenv('CHATGPT_API_KEY')

def get_ai_base_url():
    """获取 AI API Base URL（默认 DeepSeek）"""
    return os.getenv('AI_BASE_URL', 'https://api.deepseek.com')

def get_ai_model():
    """获取 AI 模型名称（默认 DeepSeek）"""
    return os.getenv('AI_MODEL', 'deepseek-chat')

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# 日志配置（修复 Windows 控制台编码问题）
import sys
if sys.platform == 'win32':
    # Windows 环境强制使用 UTF-8
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('learning_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 枚举定义 ====================

class TaskStatus(Enum):
    """任务状态"""
    TODO = "未开始"
    IN_PROGRESS = "进行中"
    DONE = "已完成"
    DELAYED = "延期"
    CANCELLED = "取消"

class Priority(Enum):
    """优先级"""
    P0 = "🔴 极高"
    P1 = "🟠 高"
    P2 = "🟡 中"
    P3 = "🟢 低"

# ==================== Notion API 操作 ====================

class NotionClient:
    """Notion数据库操作客户端"""
    BASE_URL = "https://api.notion.com/v1"

    @staticmethod
    def _headers():
        key = get_notion_api_key()
        return {
            "Authorization": f"Bearer {key}" if key else "",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    @staticmethod
    def query_database(database_id: str, filter_params: Optional[Dict] = None) -> List[Dict]:
        """查询Notion数据库"""
        url = f"{NotionClient.BASE_URL}/databases/{database_id}/query"
        payload = {"filter": filter_params} if filter_params else {}
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 查询 Notion 数据库 {database_id}（请求被模拟）")
                return []
            response = requests.post(url, headers=NotionClient._headers(), json=payload)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            logger.error(f"Notion查询失败: {e}")
            return []
    
    @staticmethod
    def get_page(page_id: str) -> Dict:
        """获取Notion页面详情"""
        url = f"{NotionClient.BASE_URL}/pages/{page_id}"
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 获取 Notion 页面 {page_id}（请求被模拟）")
                return {}
            response = requests.get(url, headers=NotionClient._headers())
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取Notion页面失败: {e}")
            return {}
    
    @staticmethod
    def update_page(page_id: str, properties: Dict) -> bool:
        """更新Notion页面属性"""
        url = f"{NotionClient.BASE_URL}/pages/{page_id}"
        payload = {"properties": properties}
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 将跳过更新 Notion 页面 {page_id}，属性: {properties}")
                return True
            response = requests.patch(url, headers=NotionClient._headers(), json=payload)
            response.raise_for_status()
            logger.info(f"更新Notion页面成功: {page_id}")
            return True
        except requests.RequestException as e:
            logger.error(f"更新Notion页面失败: {e}")
            return False
    
    @staticmethod
    def create_page(database_id: str, properties: Dict) -> Optional[str]:
        """在数据库中创建新页面"""
        url = f"{NotionClient.BASE_URL}/pages"
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 模拟创建 Notion 页面到数据库 {database_id}，属性: {properties}")
                return 'dry-run-page-id'
            response = requests.post(url, headers=NotionClient._headers(), json=payload)
            response.raise_for_status()
            page_id = response.json().get('id')
            logger.info(f"创建Notion页面成功: {page_id}")
            return page_id
        except requests.RequestException as e:
            logger.error(f"创建Notion页面失败: {e}")
            return None

# ==================== GitHub API 操作 ====================

class GitHubClient:
    """GitHub操作客户端"""
    
    BASE_URL = "https://api.github.com"

    @staticmethod
    def _headers():
        token = get_github_token()
        return {
            "Authorization": f"Bearer {token}" if token else "",
            "Accept": "application/vnd.github.v3+json"
        }
    
    @staticmethod
    def create_issue(title: str, body: str, labels: List[str] = None, 
                     assignee: str = None, due_date: str = None) -> Optional[str]:
        """创建GitHub Issue"""
        owner, repo = GITHUB_REPO.split('/')
        url = f"{GitHubClient.BASE_URL}/repos/{owner}/{repo}/issues"
        
        payload = {
            "title": title,
            "body": body,
            "labels": labels or [],
        }
        if assignee:
            payload["assignee"] = assignee
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 模拟创建 GitHub Issue: {title}，labels={labels}")
                return 'dry-run-issue'
            response = requests.post(url, headers=GitHubClient._headers(), json=payload)
            response.raise_for_status()
            issue_number = response.json().get('number')
            logger.info(f"创建GitHub Issue成功: #{issue_number}")
            return str(issue_number)
        except requests.RequestException as e:
            logger.error(f"创建GitHub Issue失败: {e}")
            return None
    
    @staticmethod
    def close_issue(issue_number: int) -> bool:
        """关闭GitHub Issue"""
        owner, repo = GITHUB_REPO.split('/')
        url = f"{GitHubClient.BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}"
        payload = {"state": "closed"}
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 模拟关闭 GitHub Issue #{issue_number}")
                return True
            response = requests.patch(url, headers=GitHubClient._headers(), json=payload)
            response.raise_for_status()
            logger.info(f"关闭GitHub Issue成功: #{issue_number}")
            return True
        except requests.RequestException as e:
            logger.error(f"关闭GitHub Issue失败: {e}")
            return False
    
    @staticmethod
    def get_issues(labels: List[str] = None, state: str = "open") -> List[Dict]:
        """查询GitHub Issues"""
        owner, repo = GITHUB_REPO.split('/')
        url = f"{GitHubClient.BASE_URL}/repos/{owner}/{repo}/issues"
        params = {"state": state}
        if labels:
            params["labels"] = ",".join(labels)
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 模拟查询 GitHub Issues，labels={labels}, state={state}")
                return []
            response = requests.get(url, headers=GitHubClient._headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"查询GitHub Issues失败: {e}")
            return []

# ==================== 同步核心逻辑 ====================

class SyncEngine:
    """Notion-GitHub同步引擎"""
    
    @staticmethod
    def sync_notion_to_github():
        """从Notion同步任务到GitHub"""
        logger.info("开始Notion→GitHub同步...")
        
        # 查询所有"未开始"和"进行中"的任务
        filter_params = {
            "or": [
                {"property": "Status", "select": {"equals": "未开始"}},
                {"property": "Status", "select": {"equals": "进行中"}}
            ]
        }
        
        tasks = NotionClient.query_database(NOTION_DATABASE_ID, filter_params)
        
        for task in tasks:
            properties = task.get('properties', {})
            
            # 提取关键信息
            title = properties.get('Title', {}).get('title', [{}])[0].get('text', {}).get('content', 'Untitled')
            due_date = properties.get('Due Date', {}).get('date', {})
            priority = properties.get('Priority', {}).get('select', {}).get('name', 'P2')
            task_type = properties.get('Type', {}).get('select', {}).get('name', '通用')
            
            # 生成Issue描述
            body = f"""
## 任务详情

**任务类型**: {task_type}  
**优先级**: {priority}  
**截止日期**: {due_date.get('start', '无期限') if due_date else '无期限'}

### 任务描述
{properties.get('Content', {}).get('rich_text', [{}])[0].get('text', {}).get('content', '无详细描述')}

---
_此Issue从Notion自动生成_  
_Notion页面ID: {task['id']}_
"""
            
            # 映射优先级到标签
            labels = [f"priority:{priority.split()[-1].lower()}", f"type:{task_type}"]
            
            # 检查是否已经有对应的Issue（通过Notion页面ID）
            existing_issues = GitHubClient.get_issues()
            page_id = task['id']
            
            issue_exists = any(page_id in issue.get('body', '') for issue in existing_issues)
            
            if not issue_exists:
                GitHubClient.create_issue(
                    title=f"[{task_type}] {title}",
                    body=body,
                    labels=labels,
                    due_date=due_date.get('start') if due_date else None
                )
        
        logger.info("Notion→GitHub同步完成")
    
    @staticmethod
    def sync_github_to_notion():
        """从GitHub同步完成状态到Notion"""
        logger.info("开始GitHub→Notion同步...")
        
        closed_issues = GitHubClient.get_issues(state="closed")
        
        for issue in closed_issues:
            # 从Issue描述中提取Notion页面ID
            body = issue.get('body', '')
            if 'Notion页面ID:' in body:
                page_id = body.split('Notion页面ID:')[-1].strip().split('\n')[0]
                
                # 更新Notion页面状态为"已完成"
                NotionClient.update_page(page_id, {
                    "Status": {"select": {"name": "已完成"}},
                    "Completion Time": {"date": {"start": datetime.now().isoformat()}}
                })
        
        logger.info("GitHub→Notion同步完成")

# ==================== 提醒与通知 ====================

class NotificationEngine:
    """提醒与通知引擎"""
    
    @staticmethod
    def send_email_summary():
        """发送每日学习摘要邮件"""
        logger.info("生成并发送每日摘要邮件...")
        
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # 查询今日任务
        today = datetime.now().strftime('%Y-%m-%d')
        tasks = NotionClient.query_database(NOTION_DATABASE_ID)
        
        # 安全地筛选今日任务
        today_tasks = []
        for t in tasks:
            due_date_prop = t.get('properties', {}).get('Due Date', {})
            if due_date_prop and due_date_prop.get('date'):
                due_start = due_date_prop.get('date', {}).get('start', '')
                if due_start == today:
                    today_tasks.append(t)
        
        # 构建邮件内容
        html_content = "<h2>🎓 今日学习任务摘要</h2>"
        html_content += f"<p>日期: {today}</p>"
        html_content += "<ul>"
        
        for task in today_tasks:
            title_prop = task.get('properties', {}).get('Title', {}).get('title', [])
            title = title_prop[0].get('text', {}).get('content', 'Untitled') if title_prop else 'Untitled'
            priority_prop = task.get('properties', {}).get('Priority', {}).get('select')
            priority = priority_prop.get('name', 'P2') if priority_prop else 'P2'
            html_content += f"<li>[{priority}] {title}</li>"
        
        html_content += "</ul>"
        
        # 发送邮件（需要配置SMTP）
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"📚 {today} 学习任务摘要"
            msg['From'] = EMAIL_USER
            msg['To'] = EMAIL_USER
            
            part = MIMEText(html_content, 'html')
            msg.attach(part)
            
            if DRY_RUN:
                logger.info("DRY_RUN: 已生成邮件摘要（未发送），内容预览:\n%s", html_content)
            else:
                # 使用环境变量配置的 SMTP 服务器
                smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
                smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
                
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(EMAIL_USER, EMAIL_PASSWORD)
                    server.send_message(msg)
                logger.info("每日摘要邮件发送成功")
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
    
    @staticmethod
    def check_deadline_reminders():
        """检查并发送截止日期提醒"""
        logger.info("检查截止日期提醒...")
        
        tasks = NotionClient.query_database(NOTION_DATABASE_ID)
        
        for task in tasks:
            due_date_prop = task.get('properties', {}).get('Due Date', {})
            if not due_date_prop or not due_date_prop.get('date'):
                continue
            
            due_date_obj = due_date_prop.get('date')
            due_start = due_date_obj.get('start')
            if not due_start:
                continue
                
            try:
                due_date = datetime.fromisoformat(due_start)
                days_until_due = (due_date - datetime.now()).days
                
                # 发送提醒（-3天、-1天、当天）
                if days_until_due in [3, 1, 0]:
                    title_prop = task.get('properties', {}).get('Title', {}).get('title', [])
                    title = title_prop[0].get('text', {}).get('content', 'Untitled') if title_prop else 'Untitled'
                    logger.warning(f"⏰ 提醒: 《{title}》 将在 {days_until_due} 天内截止")
                    # TODO: 集成推送通知服务（如企业微信、Pushplus等）
            except (ValueError, TypeError) as e:
                logger.debug(f"日期解析失败: {e}")

# ==================== 学习统计 ====================

class AnalyticsEngine:
    """学习数据统计与分析"""
    
    @staticmethod
    def generate_weekly_report() -> Dict:
        """生成周学习报告"""
        logger.info("生成周学习报告...")
        
        # 查询本周Progress表数据
        one_week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        # 这里假设有Progress表，实际需要根据Notion数据库配置调整
        
        report = {
            "period": "本周",
            "total_hours": 0,
            "courses": {},
            "efficiency_score": 0,
            "completed_tasks": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"周报告生成完成: {json.dumps(report, indent=2, ensure_ascii=False)}")
        return report
    
    @staticmethod
    def export_analytics_json(filename: str = 'analytics_data.json'):
        """导出分析数据为JSON（供Figma可视化）"""
        report = AnalyticsEngine.generate_weekly_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"分析数据已导出: {filename}")

# ==================== AI反馈生成 ====================

class AIFeedbackEngine:
    """AI反馈生成引擎"""
    
    @staticmethod
    def generate_feedback(task_description: str, learning_content: str) -> str:
        """使用ChatGPT生成学习反馈"""
        logger.info("生成AI学习反馈...")
        
        prompt = f"""
基于以下学习任务和学习内容，生成个性化、建设性的反馈和改进建议。

**学习任务**: {task_description}

**学习内容总结**: {learning_content}

请从以下方面提供反馈：
1. 学习内容的理解程度评估
2. 可能的改进方向
3. 下一步学习建议
4. 相关的高质量学习资源推荐

反馈应简洁、具体、可操作。
"""
        
        try:
            if DRY_RUN:
                logger.info("DRY_RUN: 模拟调用 AI 生成反馈")
                return "[DRY_RUN] 模拟反馈：请在真实环境中运行以获取完整建议。"

            key = get_ai_api_key()
            base_url = get_ai_base_url()
            model = get_ai_model()
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            feedback = response.json()['choices'][0]['message']['content']
            logger.info("AI反馈生成成功")
            return feedback
        except Exception as e:
            logger.error(f"AI反馈生成失败: {e}")
            return "无法生成AI反馈，请稍后重试"

# ==================== 主程序 ====================

def main():
    """主程序 - 定时执行各项任务"""
    logger.info("=" * 50)
    logger.info("学习管理系统启动")
    logger.info("=" * 50)
    logger.info(f"DRY_RUN 模式: {'开启' if DRY_RUN else '关闭'}")
    
    # 执行同步
    SyncEngine.sync_notion_to_github()
    SyncEngine.sync_github_to_notion()
    
    # 检查提醒
    NotificationEngine.send_email_summary()
    NotificationEngine.check_deadline_reminders()
    
    # 生成统计（避免重复生成日志，仅导出一次）
    AnalyticsEngine.export_analytics_json()
    
    logger.info("=" * 50)
    logger.info("学习管理系统任务完成")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
