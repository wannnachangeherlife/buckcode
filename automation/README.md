# 🤖 自动化脚本

四端协作学习系统的核心自动化工具集。

## 📁 目录结构

```
automation/
├── workflows/              # 工作流脚本
│   ├── workflow.py        # 主工作流 (morning/evening)
│   └── learning_system_core.py  # 学习系统核心
│
├── sync/                   # 同步脚本
│   ├── obsidian_to_notion_sync.py  # Obsidian → Notion
│   └── notion_to_obsidian_sync.py  # Notion → Obsidian
│
├── review/                 # 复习系统
│   └── spaced_repetition.py  # 艾宾浩斯间隔复习
│
├── utils/                  # 工具脚本
│   ├── check_env.py       # 环境检查
│   ├── secrets_check.py   # 密钥验证
│   ├── system_diagnosis.py  # 系统诊断
│   ├── analytics_data.json  # 分析数据
│   └── notion_databases.json  # Notion数据库配置
│
└── requirements.txt        # Python依赖
```

## 🚀 快速开始

### 安装依赖
```bash
pip install -r automation/requirements.txt
```

### 配置环境变量
在项目根目录的 `.env` 文件中配置:
```env
NOTION_TOKEN=secret_xxx
NOTION_TASK_DB_ID=xxx
NOTION_REVIEW_DB_ID=xxx
OBSIDIAN_VAULT_PATH=./notes/vault
DRY_RUN=0
```

## 📝 使用说明

### 1️⃣ 早晨工作流
```bash
python automation/workflows/workflow.py morning
```
- 从 Notion 拉取今日复习任务
- 检查 GitHub Actions 状态
- 生成每日任务清单

### 2️⃣ 晚间工作流
```bash
python automation/workflows/workflow.py evening
```
- 同步 Obsidian 笔记到 Notion
- 计算艾宾浩斯复习时间
- 生成学习数据分析

### 3️⃣ Obsidian → Notion 同步
```bash
python automation/sync/obsidian_to_notion_sync.py
```
同步带 `#publish` 或 `#to-notion` 标签的笔记。

### 4️⃣ 生成复习计划
```bash
python automation/review/spaced_repetition.py
```
基于艾宾浩斯遗忘曲线生成复习计划。

### 5️⃣ 环境检查
```bash
python automation/utils/check_env.py
```
验证所有必需的环境变量。

### 6️⃣ 系统诊断
```bash
python automation/utils/system_diagnosis.py
```
全面检查系统配置和连接状态。

## 🔧 故障排查

### 同步失败
```bash
# 检查环境配置
python automation/utils/check_env.py

# 验证 Notion 连接
python automation/utils/secrets_check.py

# 查看日志
cat logs/obsidian_sync.log
```

## 📚 相关文档

- [系统架构](../docs/architecture/SYSTEM_ARCHITECTURE_V2.md)
- [Notion配置](../docs/guides/NOTION_DATABASE_SETUP.md)
- [Obsidian同步](../docs/guides/OBSIDIAN_SYNC_GUIDE.md)

---
**版本**: v2.0  
**更新**: 2025-11-27

