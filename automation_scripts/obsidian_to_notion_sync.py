"""
Obsidian → Notion 同步脚本
============================

功能：
1. 扫描 Obsidian vault 中带 #publish 或 #to-notion 标签的笔记
2. 解析 Markdown 内容、双链 [[链接]]、标签 #tag
3. 同步到 Notion 复习数据库，保留知识图谱
4. 支持增量更新和选择性发布

作者：Heritage Learning System
版本：v1.0
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

# 配置
OBSIDIAN_VAULT_PATH = os.getenv('OBSIDIAN_VAULT_PATH', './obsidian_vault')
NOTION_REVIEW_DB_ID = os.getenv('NOTION_REVIEW_DB_ID')  # Notion 复习数据库 ID
DRY_RUN = os.getenv('DRY_RUN', 'True').lower() not in ('false', '0', 'no')

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('obsidian_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
                logger.info(f"DRY_RUN: 查询 Notion 数据库 {database_id}")
                return []
            response = requests.post(url, headers=NotionClient._headers(), json=payload)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            logger.error(f"Notion 查询失败: {e}")
            return []
    
    @staticmethod
    def create_page(database_id: str, properties: Dict, children: List[Dict] = None) -> Optional[str]:
        """创建页面"""
        url = f"{NotionClient.BASE_URL}/pages"
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        if children:
            payload["children"] = children
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 创建 Notion 页面到数据库 {database_id}")
                logger.debug(f"属性: {json.dumps(properties, ensure_ascii=False, indent=2)}")
                return 'dry-run-page-id'
            response = requests.post(url, headers=NotionClient._headers(), json=payload)
            response.raise_for_status()
            page_id = response.json().get('id')
            logger.info(f"✓ 创建 Notion 页面成功: {page_id}")
            return page_id
        except requests.RequestException as e:
            logger.error(f"创建 Notion 页面失败: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"响应: {e.response.text}")
            return None
    
    @staticmethod
    def update_page(page_id: str, properties: Dict) -> bool:
        """更新页面属性"""
        url = f"{NotionClient.BASE_URL}/pages/{page_id}"
        payload = {"properties": properties}
        
        try:
            if DRY_RUN:
                logger.info(f"DRY_RUN: 更新 Notion 页面 {page_id}")
                return True
            response = requests.patch(url, headers=NotionClient._headers(), json=payload)
            response.raise_for_status()
            logger.info(f"✓ 更新 Notion 页面成功: {page_id}")
            return True
        except requests.RequestException as e:
            logger.error(f"更新 Notion 页面失败: {e}")
            return False

# ==================== Obsidian 解析器 ====================

class ObsidianParser:
    """Obsidian Markdown 解析器"""
    
    # 发布标签
    PUBLISH_TAGS = ['#publish', '#to-notion', '#复习']
    
    @staticmethod
    def extract_frontmatter(content: str) -> tuple[Dict, str]:
        """提取 YAML frontmatter"""
        frontmatter = {}
        body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm_text = parts[1].strip()
                body = parts[2].strip()
                
                # 简单解析 YAML (仅支持 key: value 格式)
                for line in fm_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()
        
        return frontmatter, body
    
    @staticmethod
    def extract_tags(content: str) -> Set[str]:
        """提取所有标签 #tag"""
        return set(re.findall(r'#([\w\u4e00-\u9fa5]+)', content))
    
    @staticmethod
    def extract_wikilinks(content: str) -> Set[str]:
        """提取双链 [[链接]]"""
        return set(re.findall(r'\[\[([^\]]+)\]\]', content))
    
    @staticmethod
    def should_publish(content: str, tags: Set[str]) -> bool:
        """判断是否应该发布到 Notion"""
        for pub_tag in ObsidianParser.PUBLISH_TAGS:
            if pub_tag.lstrip('#') in tags or pub_tag in content:
                return True
        return False
    
    @staticmethod
    def markdown_to_notion_blocks(content: str) -> List[Dict]:
        """将 Markdown 转换为 Notion blocks（简化版）"""
        blocks = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 标题
            if line.startswith('#'):
                level = len(re.match(r'^#+', line).group())
                text = line.lstrip('#').strip()
                block_type = f"heading_{min(level, 3)}"
                blocks.append({
                    "object": "block",
                    "type": block_type,
                    block_type: {
                        "rich_text": [{"type": "text", "text": {"content": text}}]
                    }
                })
            # 列表
            elif line.startswith('- ') or line.startswith('* '):
                text = line[2:].strip()
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": text}}]
                    }
                })
            # 段落
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line}}]
                    }
                })
        
        return blocks[:100]  # Notion API 限制单次最多 100 个 blocks

# ==================== 同步引擎 ====================

class ObsidianNotionSync:
    """Obsidian → Notion 同步引擎"""
    
    def __init__(self, vault_path: str, notion_db_id: str):
        self.vault_path = Path(vault_path)
        self.notion_db_id = notion_db_id
        self.sync_map_file = Path(__file__).parent / 'obsidian_notion_map.json'
        self.sync_map = self._load_sync_map()
    
    def _load_sync_map(self) -> Dict[str, str]:
        """加载同步映射 (Obsidian 文件路径 -> Notion 页面 ID)"""
        if self.sync_map_file.exists():
            try:
                with open(self.sync_map_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载同步映射失败: {e}")
        return {}
    
    def _save_sync_map(self):
        """保存同步映射"""
        try:
            with open(self.sync_map_file, 'w', encoding='utf-8') as f:
                json.dump(self.sync_map, f, ensure_ascii=False, indent=2)
            logger.info(f"✓ 同步映射已保存: {self.sync_map_file}")
        except Exception as e:
            logger.error(f"保存同步映射失败: {e}")
    
    def scan_vault(self) -> List[Path]:
        """扫描 vault 中所有 Markdown 文件"""
        if not self.vault_path.exists():
            logger.error(f"Obsidian vault 路径不存在: {self.vault_path}")
            return []
        
        md_files = list(self.vault_path.rglob('*.md'))
        logger.info(f"扫描到 {len(md_files)} 个 Markdown 文件")
        return md_files
    
    def sync_file(self, file_path: Path) -> bool:
        """同步单个文件到 Notion"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return False
        
        # 解析内容
        frontmatter, body = ObsidianParser.extract_frontmatter(content)
        tags = ObsidianParser.extract_tags(content)
        wikilinks = ObsidianParser.extract_wikilinks(content)
        
        # 判断是否发布
        if not ObsidianParser.should_publish(content, tags):
            return False
        
        logger.info(f"→ 准备同步: {file_path.name}")
        
        # 构建 Notion 属性
        title = frontmatter.get('title', file_path.stem)
        properties = {
            "Title": {
                "title": [{"type": "text", "text": {"content": title}}]
            },
            "Source": {
                "rich_text": [{"type": "text", "text": {"content": f"Obsidian: {file_path.name}"}}]
            },
            "Tags": {
                "multi_select": [{"name": tag} for tag in tags if tag not in ['publish', 'to-notion', '复习']]
            },
            "Last Synced": {
                "date": {"start": datetime.now().isoformat()}
            }
        }
        
        # 如果有关联笔记（双链），添加到属性
        if wikilinks:
            properties["Related Notes"] = {
                "rich_text": [{"type": "text", "text": {"content": ", ".join(wikilinks)}}]
            }
        
        # 转换为 Notion blocks
        blocks = ObsidianParser.markdown_to_notion_blocks(body)
        
        # 检查是否已同步过
        file_key = str(file_path.relative_to(self.vault_path))
        
        if file_key in self.sync_map:
            # 更新已有页面
            page_id = self.sync_map[file_key]
            success = NotionClient.update_page(page_id, properties)
        else:
            # 创建新页面
            page_id = NotionClient.create_page(self.notion_db_id, properties, blocks)
            if page_id:
                self.sync_map[file_key] = page_id
                success = True
            else:
                success = False
        
        return success
    
    def sync_all(self):
        """同步所有符合条件的文件"""
        logger.info("=" * 50)
        logger.info("开始 Obsidian → Notion 同步")
        logger.info("=" * 50)
        logger.info(f"DRY_RUN 模式: {'开启' if DRY_RUN else '关闭'}")
        logger.info(f"Vault 路径: {self.vault_path}")
        logger.info(f"Notion 数据库: {self.notion_db_id}")
        
        files = self.scan_vault()
        synced_count = 0
        
        for file_path in files:
            if self.sync_file(file_path):
                synced_count += 1
        
        self._save_sync_map()
        
        logger.info("=" * 50)
        logger.info(f"同步完成: 成功 {synced_count}/{len(files)} 个文件")
        logger.info("=" * 50)

# ==================== 主程序 ====================

def main():
    """主程序"""
    # 检查必要配置
    if not NOTION_REVIEW_DB_ID:
        logger.error("错误: 未设置 NOTION_REVIEW_DB_ID 环境变量")
        logger.info("请在 .env 文件中设置: NOTION_REVIEW_DB_ID=你的复习数据库ID")
        return
    
    # 创建同步引擎
    sync = ObsidianNotionSync(OBSIDIAN_VAULT_PATH, NOTION_REVIEW_DB_ID)
    
    # 执行同步
    sync.sync_all()

if __name__ == "__main__":
    main()
