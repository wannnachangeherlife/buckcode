# 🎓 学习管理系统架构 v2.0

> 四端协作：VSCode学习 + Obsidian笔记 + Notion复习 + AI搜索

## 📐 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    学习管理生态系统                           │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   VSCode     │───▶│  Obsidian    │───▶│   Notion     │
│   学习端     │    │   笔记端     │    │   复习端     │
│              │    │              │    │              │
│ • 任务管理   │    │ • 知识沉淀   │    │ • 间隔复习   │
│ • 代码学习   │    │ • 双链笔记   │    │ • 知识库     │
│ • GitHub同步 │    │ • 灵感记录   │    │ • 统计分析   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                    ┌──────▼───────┐
                    │  DeepSeek AI │
                    │   搜索引擎   │
                    │              │
                    │ • 问题解答   │
                    │ • 学习反馈   │
                    │ • 复习建议   │
                    └──────────────┘
```

## 🔄 数据流转

### 1️⃣ 学习阶段 (VSCode → Obsidian)
```
任务创建 (VSCode)
    ↓
学习执行 (代码/阅读)
    ↓
笔记记录 (Obsidian)
    ├─ 添加 #publish 标签
    ├─ 使用双链 [[关联内容]]
    └─ 打上分类标签 #技术 #理论
```

### 2️⃣ 知识沉淀 (Obsidian → Notion)
```
Obsidian 笔记整理
    ↓
自动同步到 Notion 复习数据库
    ├─ 保留双链关系
    ├─ 提取标签
    ├─ 初始化复习计划
    └─ 设置首次复习时间
```

### 3️⃣ 复习强化 (Notion + AI)
```
艾宾浩斯遗忘曲线
    ↓
自动生成每日复习计划
    ↓
推送到 Obsidian/VSCode
    ↓
AI 辅助复习
    ├─ 生成测试题
    ├─ 解答疑问
    └─ 提供记忆技巧
    ↓
记录复习质量 (1-5分)
    ↓
动态调整下次复习时间
```

## 🛠️ 核心脚本

### Obsidian → Notion 同步
```bash
python automation_scripts/obsidian_to_notion_sync.py
```
- 扫描 Obsidian vault 中带 `#publish` 标签的笔记
- 同步到 Notion 复习数据库
- 保留双链和标签关系

### 间隔复习引擎
```bash
python automation_scripts/spaced_repetition.py
```
- 基于艾宾浩斯遗忘曲线
- 生成每日复习计划
- 导出到 Obsidian

### VSCode 任务管理
```bash
python automation_scripts/learning_system_core.py
```
- Notion ↔ GitHub 双向同步
- 任务提醒与截止日期
- 学习统计与分析

## ⚙️ 环境配置

### 必需环境变量
```env
# Notion
NOTION_API_KEY=ntn_xxx
NOTION_DATABASE_ID=xxx  # 任务管理数据库
NOTION_REVIEW_DB_ID=xxx # 复习数据库

# GitHub
GH_TOKEN=ghp_xxx
GH_REPO=owner/repo

# AI (DeepSeek 等)
AI_API_KEY=sk-xxx
AI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat

# Obsidian
OBSIDIAN_VAULT_PATH=./obsidian_vault

# Email (可选)
EMAIL_USER=you@example.com
EMAIL_PASSWORD=app-password
EMAIL_SMTP_SERVER=smtp.mail.me.com
EMAIL_SMTP_PORT=587

# 运行模式
DRY_RUN=0  # 设为 1 开启测试模式
```

## 📝 使用流程

### 每日工作流

#### 1. 晨间计划 (VSCode)
```bash
# 查看今日任务
git pull  # 同步最新任务
# 在 Notion 中查看今日计划
```

#### 2. 学习与记录 (VSCode + Obsidian)
- 在 VSCode 中完成任务
- 学习过程中实时记录到 Obsidian
- 使用双链关联相关知识点
- 添加 `#publish` 标签标记重要内容

#### 3. 知识整理 (Obsidian)
- 整理今日笔记
- 补充双链和标签
- 确保重要内容带 `#publish` 标签

#### 4. 自动同步 (自动化)
```bash
# 手动触发或定时运行
python automation_scripts/obsidian_to_notion_sync.py
```

#### 5. 复习计划 (Notion + Obsidian)
```bash
# 生成今日复习计划
python automation_scripts/spaced_repetition.py
# 在 Obsidian 中查看复习计划
```

#### 6. AI 辅助复习
- 使用 DeepSeek 等 AI 工具
- 提问不理解的知识点
- 生成测试题自测
- 获取记忆技巧建议

### 复习质量评分标准
- **5分**: 完美记忆，能详细讲解
- **4分**: 正确但有犹豫
- **3分**: 正确但费力回忆
- **2分**: 错误但能想起部分
- **1分**: 完全忘记

## 🎯 Notion 数据库设计

### 任务管理数据库 (Task Management)
| 字段 | 类型 | 说明 |
|------|------|------|
| Title | 标题 | 任务名称 |
| Status | 单选 | 未开始/进行中/已完成 |
| Due Date | 日期 | 截止日期 |
| Priority | 单选 | P0/P1/P2/P3 |
| Type | 单选 | 编程/理论/项目/其他 |
| GitHub Issue | URL | 关联的 Issue |

### 复习数据库 (Review Database)
| 字段 | 类型 | 说明 |
|------|------|------|
| Title | 标题 | 知识点名称 |
| Source | 文本 | 来源 (Obsidian文件名) |
| Tags | 多选 | 分类标签 |
| Related Notes | 文本 | 关联笔记(双链) |
| Review Count | 数字 | 已复习次数 |
| Next Review | 日期 | 下次复习时间 |
| Last Review | 日期 | 最后复习时间 |
| Last Quality | 数字 | 最后复习质量(1-5) |
| Status | 单选 | 学习中/已掌握 |

## 🚀 GitHub Actions 自动化

### 定时任务
- 每天 22:30 自动运行
- Notion ↔ GitHub 同步
- 发送每日学习摘要邮件
- 生成学习统计报告

### 手动触发
- Health Check: 验证配置
- Periodic Tasks: 立即执行同步

## 📚 扩展功能

### AI 集成增强
- 自动生成复习测试题
- 根据遗忘曲线推荐复习内容
- 学习路径个性化建议
- 知识图谱可视化

### 多端协同
- iOS Shortcuts 快速添加任务
- Apple Calendar 日程同步
- Figma Dashboard 数据可视化
- WPS 报告导出

## 🔧 故障排查

### Obsidian 同步失败
- 检查 `OBSIDIAN_VAULT_PATH` 路径
- 确认笔记包含 `#publish` 标签
- 查看 `obsidian_sync.log` 日志

### Notion 连接问题
- 验证 `NOTION_API_KEY` 有效性
- 确认数据库已共享给集成
- 检查数据库 ID 是否正确

### 复习计划不生成
- 确认 `NOTION_REVIEW_DB_ID` 已设置
- 检查数据库是否有 Next Review 字段
- 查看 `spaced_repetition.log` 日志

## 📖 参考文档

- [Notion API 文档](https://developers.notion.com/)
- [Obsidian 插件开发](https://docs.obsidian.md/)
- [艾宾浩斯遗忘曲线](https://zh.wikipedia.org/wiki/遗忘曲线)
- [DeepSeek API](https://platform.deepseek.com/)

---

**版本**: v2.0  
**更新时间**: 2025-11-27  
**作者**: Heritage Learning System
