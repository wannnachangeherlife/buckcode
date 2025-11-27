# 🎓 文化遗产数字化学习系统 v2.0

> 一个结合 Obsidian、Notion、GitHub 和 AI 的四端协作学习系统,专注于文化遗产数字化领域的全栈技能学习。

## 📁 项目结构

```
magicalgitzone/
├── 📚 notes/                    # Obsidian笔记端
│   ├── vault/                   # 知识库
│   │   ├── 三维重建基础.md
│   │   ├── 点云处理技术.md
│   │   ├── 深度学习在文化遗产中的应用.md
│   │   └── 文化遗产学习计划-项目管理.md
│   └── templates/               # 笔记模板
│       ├── 每日学习日志.md
│       ├── 每周总结.md
│       └── 知识笔记.md
│
├── 📋 planning/                 # VSCode学习端 - 学习计划
│   ├── PLAN_SUMMARY.md          # 32周总览
│   └── WEEKLY_TASKS.md          # 周度任务
│
├── 🤖 automation/               # 四端协作自动化
│   ├── workflows/               # 主工作流
│   │   ├── workflow.py          # morning/evening
│   │   └── learning_system_core.py
│   ├── sync/                    # Obsidian ↔ Notion
│   │   ├── obsidian_to_notion_sync.py
│   │   └── notion_to_obsidian_sync.py
│   ├── review/                  # 艾宾浩斯复习
│   │   └── spaced_repetition.py
│   └── utils/                   # 工具集
│       ├── check_env.py
│       └── system_diagnosis.py
│
├── 💻 projects/                 # 实践项目
│   └── heritage-showcase/       # 文化遗产展示
│
├── 📖 docs/                     # 项目文档
│   ├── guides/                  # 配置指南
│   ├── architecture/            # 系统架构
│   └── deployment/              # 部署文档
│
└── 📝 logs/                     # 系统日志
```

## 🌟 系统定位

四端协作的智能学习生态：

- **📝 VSCode** = 学习端 (任务管理、代码学习、GitHub 同步)
- **📚 Obsidian** = 笔记端 (知识沉淀、双链笔记、灵感捕捉)
- **📋 Notion** = 复习端 (间隔复习、知识库管理、统计分析)
- **🤖 AI (Kimi/DeepSeek)** = 搜索引擎 (智能问答、学习反馈、复习建议)

## 🚀 快速开始

### 1️⃣ 环境配置

```powershell
# 克隆仓库
git clone <repo-url>
cd magicalgitzone

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r automation/requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件,填入你的 API keys
```

**必需配置**：
- `NOTION_TOKEN` - Notion Integration Token
- `NOTION_TASK_DB_ID` - 任务管理数据库 ID
- `NOTION_REVIEW_DB_ID` - 复习数据库 ID
- `OBSIDIAN_VAULT_PATH` - Obsidian vault 路径
- `DRY_RUN` - 0=真实执行, 1=测试模式

### 2️⃣ Notion 配置

参考 `docs/guides/NOTION_DATABASE_SETUP.md`:
1. 创建任务管理数据库
2. 创建复习数据库
3. 获取 Integration Token
4. 配置数据库 ID

### 3️⃣ 运行工作流

```powershell
# 早晨工作流 (获取今日复习任务)
python automation/workflows/workflow.py morning

# 晚间工作流 (同步笔记到Notion)
python automation/workflows/workflow.py evening
```

## 🎯 核心功能

### 自动化工作流

**早晨流程**: 
- 从 Notion 拉取今日复习任务
- 检查 GitHub Actions 运行状态
- 生成每日任务清单

**晚间流程**:
- 同步 Obsidian 笔记到 Notion
- 计算艾宾浩斯复习时间
- 生成学习数据分析

### 艾宾浩斯间隔复习

| 间隔 | 时间点 | 复习方式 |
|------|--------|----------|
| 第1次 | 5分钟 | 快速回顾 |
| 第2次 | 30分钟 | 完成练习 |
| 第3次 | 12小时 | 费曼讲解 |
| 第4次 | 1天 | 完整复习 |
| 第5次 | 2天 | 应用实践 |
| 第6次 | 4天 | 知识串联 |
| 第7次 | 7天 | 录制视频 |
| 第8次 | 15天 | 综合项目 |
| 第9次 | 30天 | 教授他人 |

### 间隔复习调度脚本集成 (Spaced Repetition Scheduler)

新增 `automation/utils/spaced_repetition.py` 与工作流脚本 `automation/workflows/review_scheduler.py` 用于根据复习质量 (quality 0~5) 动态更新卡片的 `阶段 Stage`、`Ease`、`Interval` 与下一次复习日期。

属性要求 (Notion 复习数据库)：
- `卡片标题` (Title)
- `关联知识点` (Relation → 知识数据库)
- `阶段 Stage` (Number)
- `Ease` (Number, 初始建议 2.5)
- `Interval` (Number, 天数)
- `上次复习日期` (Date)
- `下次复习日期` (Date)
- `状态` (Select: 新建/复习/重置/完成)

算法 (SM-2 变体)：
- quality < 3: 重置 stage=0, interval=1, ease -=0.20, 状态=重置
- quality ≥ 3: stage+=1; stage=1→interval=1; stage=2→6; else interval=round(prev_interval * ease)
- ease 更新: ease = ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)), 下限 1.3
- stage ≥ 8 且 quality ≥4 → 状态=完成

快速示例 (PowerShell)：
```powershell
$env:NOTION_TOKEN = "secret_xxx"
python automation/workflows/review_scheduler.py --config automation/utils/notion_migration_config.json --only-due --dry-run
python automation/workflows/review_scheduler.py --config automation/utils/notion_migration_config.json --quality 5 --max 50
```

交互评分模式：
```powershell
python automation/workflows/review_scheduler.py --config automation/utils/notion_migration_config.json --interactive --only-due
```

自定义日期回填 (补录历史复习)：
```powershell
python automation/workflows/review_scheduler.py --config automation/utils/notion_migration_config.json --today 2025-11-26 --quality 4
```

注意：`--dry-run` 会打印计划更新而不真正 PATCH；去掉后才会写入 Notion。

#### 高级功能扩展

调度脚本 `review_scheduler.py` 额外支持：

- 批量质量来源：`--quality-file data/qualities.csv` （列: `title,quality,latency` 或 JSON `{ "标题": {"quality":4,"latency":2.1} }`）
- 延迟 (latency) 惩罚 / 快速奖励：延迟>12s 视为最大惩罚，完美且 <3s 获得微增益。
- 标签过滤：`--tag 计算机视觉,三维重建` 仅处理包含全部标签的卡片。
- 阶段范围：`--stage-min 2 --stage-max 6` 聚焦中段复习。
- 任务同步：`--tasks-sync` 在卡片完成时在任务数据库创建关联任务 (需要配置 `tasks_db_id`)。
- 统计输出：`--stats` 写入 `automation/analytics/review_stats.json`（处理数、Ease前后均值、Stage分布、到期数量等）。
- 仪表板生成：`--generate-dashboard` 写入 `docs/analytics/REVIEW_DASHBOARD.md`。
- 备份与回滚：`--backup` 生成 `automation/analytics/review_backup_YYYY-MM-DD.json`；使用 `review_rollback.py` 可恢复。

示例：
```powershell
python automation/workflows/review_scheduler.py --config automation/utils/notion_migration_config.json `
	--only-due --quality-file data/qualities.csv --stats --generate-dashboard --backup --tasks-sync
```

回滚示例：
```powershell
python automation/workflows/review_rollback.py --backup automation/analytics/review_backup_2025-11-27.json --dry-run
python automation/workflows/review_rollback.py --backup automation/analytics/review_backup_2025-11-27.json
```

GitHub Actions 已提供 `.github/workflows/review_schedule.yml` 每日定时执行（UTC 01:00 ≈ 北京时间 09:00）。

生成 SVG 图表并嵌入仪表板：
```powershell
python automation/workflows/review_scheduler.py --config automation/utils/notion_migration_config.json --only-due --stats --generate-dashboard
```
输出位置：
- `docs/analytics/REVIEW_DASHBOARD.md`
- `docs/analytics/stage_distribution.svg`
- `docs/analytics/ease_compare.svg`

### 交互采集工具 (TUI)

新增 `automation/workflows/review_tui.py` 支持逐条卡片交互复习并采集 `quality` 与 `latency`（回忆耗时秒）。生成的 CSV 可直接作为 `--quality-file` 输入批量调度。

示例：
```powershell
python automation/workflows/review_tui.py --config automation/utils/notion_migration_config.json --out data/qualities.csv --limit 25
python automation/workflows/review_scheduler.py --config automation/utils/notion_migration_config.json --quality-file data/qualities.csv --stats --generate-dashboard
```

CSV 格式示例：
```csv
title,quality,latency
三维重建基础-关键点提取,5,2.13
点云处理技术-滤波流程,4,5.92
深度学习在文化遗产中的应用-数据增强策略,3,11.40
```

工作流增强：调度脚本已内置速率限制与指数重试；任务数据库属性自动探测（Title/状态/Relation）减少硬编码风险；仪表板包含 Stage 分布与 Ease 比例条可视化。

### Analytics 仪表板 & GitHub Pages

已生成静态分析页面：`docs/analytics/index.html`，包含：
- 动态加载最新 `review_stats.json`
- 内联条形图与基础 SVG 图 (`stage_distribution.svg`, `ease_compare.svg`)
- 历史趋势折线图（Ease & Processed）来自 `history.json`
- 主题切换（浅色 / 深色，记忆于 `localStorage`）
- 原始统计与历史 JSON 查看

历史数据文件：`docs/analytics/history.json`（每日调度自动追加）字段说明：
| 字段 | 描述 |
| ---- | ---- |
| date | ISO 日期 YYYY-MM-DD |
| avg_ease_before | 当日调度前易度平均值 |
| avg_ease_after | 调度更新后易度平均值 |
| processed | 当日处理复习卡片数量 |
| due_count | 当日到期未处理卡片数 |

前端折线图要点：
- 最多抽样 12 个日期刻度避免拥挤
- 悬浮 tooltip 使用 `<title>` 元素纯 SVG 实现
- 绿色：Ease After；橙色：Processed 数量

主题切换实现：
- 使用 `:root` CSS 变量与 `.dark` 类
- 按钮 id=`theme-toggle` 切换并写入 `analytics-theme`
- 首次加载读取本地偏好自动应用

发布方式：
1. 启用 GitHub Pages 并选择 `gh-pages` 分支（工作流自动创建）。
2. 工作流 `.github/workflows/review_schedule.yml` 每日运行自动部署。
3. 手动部署：运行 `Deploy Analytics Dashboard` Action 或直接推送对 `docs/analytics/` 修改。

访问：启用后浏览 `https://<your-username>.github.io/<repo-name>/` (或子路径) 查看最新仪表板。

### 一键体检 Doctor

- 脚本：`automation/workflows/doctor.py`
- 能力：加载 `.env`、验证 Notion、补齐数据库属性、可选初始化、调用调度（干跑或全链路）、可选输出 HTML 报告。

示例：
```powershell
# 体检+补齐属性+初始化（预演）
python automation/workflows/doctor.py --fix --init --seed data/review_seed.csv --tags "三维,文化遗产" --dry-run --max 5

# 全链路（统计+仪表板+备份），并输出报告
python automation/workflows/doctor.py --fix --full --report docs/analytics/doctor_report.html --max 10
```

VS Code 任务：
- 任务名：`Doctor: 一键体检与验证`
- 等价命令：
```powershell
python automation/workflows/doctor.py --fix --init --seed data/review_seed.csv --tags "三维,文化遗产" --dry-run --max 5
```

CI（已提供）：`.github/workflows/ci_doctor.yml`
- Push/手动触发运行 Doctor（dry-run），并产出 `docs/analytics/doctor_report.html` 作为构建工件。





## 📚 学习路径

### 阶段一: 环境搭建 (第1-4周)
- Conda、Docker、Node.js 配置
- Python 与 OpenCV 基础
- Three.js 3D 场景搭建
- 数学基础复习

### 阶段二: 图像AI与前端 (第5-17周)
- 深度学习基础 (PyTorch)
- 计算机视觉 (三维重建、SLAM)
- React 高级特性
- WebGL 性能优化

### 阶段三: 后端与区块链 (第18-27周)
- FastAPI RESTful API
- 数据库设计 (MySQL/MongoDB)
- 区块链与 NFT 技术
- 智能合约开发

### 阶段四: 项目整合 (第28-32周)
- 系统集成与联调
- 单元测试与部署
- 项目文档与展示

详见 `planning/PLAN_SUMMARY.md`

## 🛠️ 技术栈

### 前端
- **框架**: React 18+ with TypeScript
- **3D渲染**: Three.js / React Three Fiber
- **构建工具**: Vite

### 后端
- **语言**: Python 3.13
- **框架**: FastAPI
- **ORM**: SQLAlchemy / Motor
- **认证**: JWT

### AI/ML
- **深度学习**: PyTorch
- **计算机视觉**: OpenCV, Open3D
- **目标检测**: YOLO, Detectron2
- **三维重建**: OpenMVG, NeRF

### 区块链
- **智能合约**: Solidity
- **开发框架**: Hardhat
- **前端交互**: Ethers.js
- **存储**: IPFS

### DevOps
- **容器化**: Docker
- **CI/CD**: GitHub Actions
- **部署**: Vercel, Railway

## 📖 文档指南

| 文档 | 说明 |
|------|------|
| [系统架构 V2](docs/architecture/SYSTEM_ARCHITECTURE_V2.md) | 四端系统设计详解 |
| [Notion配置](docs/guides/NOTION_DATABASE_SETUP.md) | 数据库Schema配置 |
| [Obsidian同步](docs/guides/OBSIDIAN_SYNC_GUIDE.md) | 双向同步设置 |
| [GitHub Actions](docs/guides/GITHUB_ACTIONS_SETUP.md) | 自动化工作流配置 |
| [部署指南](docs/deployment/DEPLOYMENT_COMPLETE.md) | 完整部署流程 |
| [AI API配置](docs/guides/AI_API_FREE_GUIDE.md) | Kimi/DeepSeek设置 |

## 🔧 配置文件说明

### .env (环境变量)
```bash
NOTION_TOKEN=secret_xxx          # Notion Integration Token
NOTION_TASK_DB_ID=xxx            # 任务管理数据库ID
NOTION_REVIEW_DB_ID=xxx          # 复习数据库ID
OBSIDIAN_VAULT_PATH=./notes/vault
DRY_RUN=0                        # 0=真实执行, 1=测试模式
```

### automation/utils/notion_databases.json
存储 Notion 数据库的详细 Schema 信息

### automation/utils/analytics_data.json
学习数据分析结果

## 🤝 工作流最佳实践

### 每日流程

**上午 (9:00)**
1. 运行 `python automation/workflows/workflow.py morning`
2. 查看今日复习任务  
3. 在 Obsidian 中完成复习

**学习中**
1. 在 VSCode 中实践代码  
2. 在 Obsidian 中记录笔记  
3. 使用模板保持格式统一

**晚上 (22:00)**
1. 运行 `python automation/workflows/workflow.py evening`
2. 同步笔记到 Notion  
3. 查看学习统计分析

### 笔记规范

- 使用 YAML frontmatter 标记元数据
- 添加 `#publish` 标签同步到 Notion
- 添加 `#to-notion` 标签触发同步
- 使用 `[[双向链接]]` 关联知识点
- 每周进行周总结 (使用模板)

## 📊 进度追踪

### 当前状态
- ✅ 系统架构搭建完成
- ✅ Obsidian-Notion 双向同步正常
- ✅ 艾宾浩斯复习系统运行中
- ✅ 8个学习模板创建完成
- ✅ 4个知识笔记增强完成
- 📝 准备开始第1周学习 (2025-12-01)

### 项目管理
在 Obsidian 中查看 `notes/vault/文化遗产学习计划-项目管理.md` 获取:
- 32周详细任务清单
- 4个阶段里程碑
- Dataview 进度可视化
- 问题追踪表

## 🐛 故障排查

### Obsidian 同步失败
```powershell
# 检查环境变量
python automation/utils/check_env.py

# 查看同步日志
cat logs/obsidian_sync.log
```

### Notion API 错误
```powershell
# 验证 Notion 连接
python automation/utils/secrets_check.py
```

### GitHub Actions 未运行
1. 确保添加了 `NOTION_REVIEW_DB_ID` Secret
2. 参考 `docs/deployment/ADD_NOTION_REVIEW_DB_SECRET.md`

## GitHub Actions

### 必需 Secrets
- `NOTION_TOKEN` - Notion API Token
- `NOTION_TASK_DB_ID` - 任务数据库
- `NOTION_REVIEW_DB_ID` - 复习数据库
- `GH_TOKEN` - GitHub Personal Access Token
- `AI_API_KEY` - AI API密钥

### 工作流
- **Health Check**: 系统健康检查
- **Periodic Tasks**: 定期学习任务

详见 `docs/guides/GITHUB_ACTIONS_SETUP.md`

## 📮 联系方式

- GitHub Issues: 项目问题反馈
- 学习笔记: 见 `notes/vault/`
- 项目文档: 见 `docs/`

## 📄 许可证

MIT License

---

**开始日期**: 2025-11-27  
**预计完成**: 2026-07-31 (32周学习计划)  
**当前版本**: v2.0  
**维护状态**: 🟢 活跃开发中

Happy Learning! 🎓✨
