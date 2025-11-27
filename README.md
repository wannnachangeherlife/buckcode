# 🎓 Heritage Learning System v2.0

> 文化遗产数字化竞赛 - 两年学习计划管理系统

## 🌟 系统定位

四端协作的智能学习生态：

- **VSCode** = 学习端 (任务管理、代码学习、GitHub 同步)
- **Obsidian** = 笔记端 (知识沉淀、双链笔记、灵感捕捉)
- **Notion** = 复习端 (间隔复习、知识库管理、统计分析)
- **DeepSeek AI** = 搜索引擎 (智能问答、学习反馈、复习建议)

## 🚀 快速开始

### 1. 环境配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
notepad .env
```

必需配置：
- `NOTION_API_KEY`: Notion 集成密钥
- `NOTION_DATABASE_ID`: 任务管理数据库 ID
- `NOTION_REVIEW_DB_ID`: 复习数据库 ID
- `OBSIDIAN_VAULT_PATH`: Obsidian vault 路径
- `AI_API_KEY`: DeepSeek API 密钥

### 2. 安装依赖
```bash
python -m venv venv
venv\Scripts\activate
pip install -r automation_scripts\requirements.txt
```

### 3. 运行脚本

#### Obsidian → Notion 同步
```bash
python automation_scripts\obsidian_to_notion_sync.py
```

#### 生成复习计划
```bash
python automation_scripts\spaced_repetition.py
```

#### 任务管理与同步
```bash
python automation_scripts\learning_system_core.py
```

## 📖 详细文档

- [系统架构 v2.0](SYSTEM_ARCHITECTURE_V2.md) - 完整架构说明
- [Notion 数据库设置](NOTION_DATABASE_SETUP.md) - 数据库配置指南
- [Obsidian 同步](OBSIDIAN_SYNC_GUIDE.md) - 笔记同步教程
- [间隔复习算法](automation_scripts/spaced_repetition.py) - 艾宾浩斯遗忘曲线

## GitHub Actions

- 必需 Secrets（Repository Secrets）：`NOTION_API_KEY`, `NOTION_DATABASE_ID`, `GH_TOKEN`, `GH_REPO`, `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_SMTP_SERVER`, `EMAIL_SMTP_PORT`。
- 健康检查（Health Check）：进入仓库的 Actions 选项卡，选择 “Health Check” 工作流，点击 “Run workflow”。若缺失 Secrets 或外部连通性异常，步骤会以 “Process completed with exit code 1” 结束并输出 JSON 报告。
- 周期任务（Periodic Learning Tasks）：同样在 Actions 里选择 “Periodic Learning Tasks”，手动运行或等待定时触发。

### 常见问题

- Exit code 1：多由 Secrets 未配置或配置错误导致。请先补齐 Secrets 后再次运行 “Health Check”。
- Notion 404 或权限错误：确认 `NOTION_API_KEY` 有访问目标数据库权限，`NOTION_DATABASE_ID` 正确无空格。
- GitHub 401/404：确认 `GH_TOKEN` 具备 `repo` 权限，`GH_REPO` 形如 `owner/repo`。
- 邮件 TLS/登录失败：检查 `EMAIL_SMTP_SERVER`/`EMAIL_SMTP_PORT` 与账户的应用专用密码是否正确。
