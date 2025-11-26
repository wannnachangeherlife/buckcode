
# 自动化脚本与集成指南

## 目录结构
- `learning_system_core.py`：主自动化脚本，支持 Notion↔GitHub 同步、邮件、AI反馈、统计
- `create_notion_schema.py`：自动创建 Notion 数据库结构
- `fill_notion_relations.py`：自动填充 Notion Relation 字段，实现表间关联
- `analytics_engine_demo.py`：Progress 表统计分析，支持 dry-run
- `notion_to_obsidian_sync.py`：Notion 任务/笔记同步到 Obsidian Vault
- `check_env.py`：环境变量检查
- `runner_dryrun.py`：本地 dry-run 测试入口
- `templates/`：Notion CSV 导入模板

## 快速运行流程
1. 激活环境并安装依赖
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r automation_scripts\requirements.txt
```
2. 检查环境变量
```powershell
python automation_scripts\check_env.py
```
3. 自动创建 Notion 数据库
```powershell
python automation_scripts\create_notion_schema.py
```
4. 自动填充 Relation 字段
```powershell
python automation_scripts\fill_notion_relations.py
```
5. Progress 表统计分析
```powershell
python automation_scripts\analytics_engine_demo.py
```
6. Notion→Obsidian 笔记同步
```powershell
python automation_scripts\notion_to_obsidian_sync.py
```
7. Dry-run 测试（安全模式）
```powershell
$env:DRY_RUN='True'
python automation_scripts\runner_dryrun.py
```

## 说明
- 所有脚本均支持 DRY_RUN 环境变量，便于本地安全测试。
- 若遇到 API 权限或字段错误，请贴出终端输出，我会协助排查。
- Obsidian Vault 路径可在 .env 中配置 `OBSIDIAN_VAULT_PATH`。
- Figma 仪表板规范见 `figma_dashboard_spec.md`，iOS Shortcuts 示例见 `ios_shortcuts_calendar_notify.json`。

