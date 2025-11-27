# Notion 到 Obsidian 同步使用指南

## 📋 功能说明

`notion_to_obsidian_sync.py` 自动将 Notion Task Management 数据库中的未完成任务同步到本地 Obsidian Vault，生成 Markdown 格式的笔记文件。

## 🚀 快速开始

### 1. 配置（三选一）

**方式 A：使用环境变量（推荐）**
```bash
# 在 .env 文件中添加
NOTION_DATABASE_ID=<Task Management 数据库 ID>
OBSIDIAN_VAULT_PATH=D:\path\to\your\obsidian\vault
```

**方式 B：自动读取（已配置）**
- 脚本会自动从 `automation_scripts/notion_databases.json` 读取 Task Management ID
- 无需额外配置

**方式 C：使用默认路径**
- Obsidian Vault 默认路径：`./obsidian_vault`
- 如需修改，设置 `OBSIDIAN_VAULT_PATH` 环境变量

### 2. 运行同步

```powershell
# 干运行模式（默认，不写入文件，仅预览）
python automation_scripts\notion_to_obsidian_sync.py

# 实际同步模式（写入 Markdown 文件）
$env:DRY_RUN="false"; python automation_scripts\notion_to_obsidian_sync.py
```

### 3. 生成的 Markdown 格式

```markdown
# 学习 Three.js 光照系统

- 类型: 📺 讲座学习
- 截止日期: 2025-11-29
- 状态: 🔄 进行中
- 优先级: 🟠 P1-高
- 完成度: 30%
- 标签: #考试周, #需AI反馈
- 笔记链接: obsidian://vault/notes/threejs-lighting

---
同步时间: 2025-11-26 22:50
```

## 🔧 高级配置

### 定时自动同步（Windows 任务计划程序）

1. 打开任务计划程序 → 创建基本任务
2. 触发器：每天 8:00 AM
3. 操作：
   - 程序：`powershell.exe`
   - 参数：`-Command "cd D:\path\to\magicalgitzone; $env:DRY_RUN='false'; python automation_scripts\notion_to_obsidian_sync.py"`

### 定时自动同步（Linux/macOS Cron）

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天 8:00）
0 8 * * * cd /path/to/magicalgitzone && DRY_RUN=false python automation_scripts/notion_to_obsidian_sync.py
```

## 📊 同步逻辑

- **过滤条件**：仅同步状态 ≠ "已完成" 的任务
- **文件命名**：使用任务标题，自动替换 `/` `\` `:` 为安全字符
- **更新策略**：每次运行覆盖同名文件（Obsidian 会自动检测文件变化）
- **属性映射**：
  - Title → Markdown H1 标题
  - Type, Due Date, Status, Priority, Progress, Tags → Metadata
  - Note Link → Obsidian 跳转链接

## 🧪 测试脚本

创建示例任务用于测试：
```powershell
python automation_scripts\create_sample_task.py
```

验证同步效果：
```powershell
python automation_scripts\notion_to_obsidian_sync.py
```

## ⚠️ 常见问题

**Q1: 显示 "Could not find database with ID: None"**
- A: 确保 `notion_databases.json` 存在且包含 Task Management 条目
- 或在 `.env` 设置 `NOTION_DATABASE_ID`

**Q2: 生成的文件为空或缺少内容**
- A: 检查 Notion 任务是否包含对应属性（Title、Status 等）
- 确认 Integration 已共享到 Task Management 数据库

**Q3: 中文文件名乱码**
- A: 脚本使用 UTF-8 编码，确保 Obsidian 设置为 UTF-8

**Q4: DRY_RUN 模式如何关闭**
- A: 设置环境变量 `DRY_RUN=false` 或在 `.env` 中添加 `DRY_RUN=false`

## 🔗 相关文件

- `automation_scripts/notion_to_obsidian_sync.py` - 主同步脚本
- `automation_scripts/notion_databases.json` - 数据库 ID 配置
- `automation_scripts/create_sample_task.py` - 测试任务生成器
- `obsidian_templates/` - Obsidian 模板文件夹

## 📈 下一步优化

- [ ] 支持同步 Daily Progress 数据库（学习记录）
- [ ] 添加增量同步（仅更新修改过的任务）
- [ ] 支持双向同步（Obsidian 修改 → Notion）
- [ ] 自动在 Obsidian 中创建 DataView 查询看板
- [ ] 集成 Git 自动提交同步历史

---

**提示**：首次运行建议使用 DRY_RUN 模式预览，确认无误后再实际写入文件。
