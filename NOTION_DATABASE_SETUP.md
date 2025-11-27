# Notion 数据库快速配置指南

> 此文档包含快速建立Notion学习管理数据库的所有步骤

## 📝 前置准备

### 1. 获取Notion API密钥

1. 访问 https://www.notion.so/my-integrations
2. 点击 "New integration" → 创建新集成
3. 命名为 "Heritage Learning System"
4. 复制 **Internal Integration Token**（需妥善保管）
5. 在集成设置中添加"能力": 
   - `read`
   - `update`
   - `insert`

### 2. 共享数据库给集成

1. 在Notion中创建工作区或打开现有工作区
2. 创建根页面，命名为 "🎓 学习管理系统"
3. 在该页面中右上角 "Share" → 选择刚才创建的Integration → 确认

### 3. 获取Database ID

- 打开任意Notion数据库（如Course Table）
- URL格式：`https://www.notion.so/YOUR_WORKSPACE_ID/DATABASE_ID?v=...`
- 复制 `DATABASE_ID`（32个字符，无连接符）

---

## 🗂️ 数据库表结构详细说明

### 表1: 课程管理 (Course Table)

**数据库名**: `Course Management`

| 属性名 | 类型 | 是否必需 | 说明 |
|-------|------|--------|------|
| **Title** | Title | ✅ | 课程名称（如"PyTorch深度学习"） |
| **Category** | Select | ✅ | 学科分类选项：AI算法、3D建模、前端、后端、数学、英语、考试、工作 |
| **Start Date** | Date | ✅ | 课程开始日期 |
| **End Date** | Date | ⭕ | 课程结束日期 |
| **Weekly Hours** | Number | ⭕ | 每周计划学习小时数 |
| **Priority** | Select | ✅ | 优先级：P0极高/P1高/P2中/P3低 |
| **Status** | Select | ✅ | 状态：未开始/进行中/已完成/暂停 |
| **Resources** | URL | ⭕ | 学习资源链接（支持多个，用`,`分隔） |
| **Notes** | Rich Text | ⭕ | 课程备注 |
| **Related Tasks** | Relation | ⭕ | 双向关联Task表（自动反向属性：Related Course） |
| **Progress Items** | Relation | ⭕ | 双向关联Daily Progress（自动生成） |
| **Related Events** | Relation | ⭕ | 双向关联Important Events（自动生成） |
| **Related Resources** | Relation | ⭕ | 双向关联Learning Resources（自动生成） |
| **Progress** | Rollup | ⭕ | 自动计算任务完成率 |

**Select选项预设**:
```
Category:
- 🤖 AI算法
- 🎨 3D建模
- 🌐 前端开发
- ⚙️ 后端开发
- 📐 数学基础
- 🇬🇧 英语
- 📖 考试准备
- 💼 工作任务

Priority:
- 🔴 P0-极高
- 🟠 P1-高
- 🟡 P2-中
- 🟢 P3-低

Status:
- ⏳ 未开始
- 🔄 进行中
- ✅ 已完成
- ⏸️ 暂停
```

---

### 表2: 任务清单 (Task Table) ⭐ 最重要

**数据库名**: `Task Management`

| 属性名 | 类型 | 是否必需 | 说明 |
|-------|------|--------|------|
| **Title** | Title | ✅ | 任务标题 |
| **Type** | Select | ✅ | 任务类型：讲座/作业/项目/复习/考试/阅读/其他 |
| **Due Date** | Date | ✅ | ⭐ 截止日期（用于提醒） |
| **Estimated Hours** | Number | ⭕ | 预计耗时（小时） |
| **Actual Hours** | Number | ⭕ | 实际耗时（小时） |
| **Priority** | Select | ✅ | 优先级 P0-P3 |
| **Status** | Select | ✅ | 状态：未开始/进行中/已完成/延期/取消 |
| **Related Course** | Relation | ✅ | 双向关联课程（自动反向属性：Related Tasks） |
| **Progress** | Percentage | ✅ | 完成百分比 0-100% |
| **Deliverable** | Select | ⭕ | 提交物类型：代码/笔记/报告/视频/截图/其他 |
| **Submission Link** | URL | ⭕ | GitHub Gist、文件链接等 |
| **Need AI Feedback** | Checkbox | ⭕ | 是否需要AI反馈 |
| **Review Schedule** | Multi-select | ⭕ | 复习周期：D+1/D+3/D+7/D+14/D+30 |
| **Note Link** | URL | ⭕ | Obsidian笔记链接 |
| **Tags** | Multi-select | ⭕ | 标签：#考试周/#突发/#延期/#加急/#优质成果 |
| **GitHub Issue** | Text | ⭕ | 自动填充的GitHub Issue号 |
| **Last Modified** | Last edited time | ⭕ | 自动记录最后修改时间 |

**Select选项预设**:
```
Type:
- 📺 讲座学习
- 📝 作业实践
- 🛠️ 项目开发
- 🔄 复习巩固
- 📚 考试准备
- 📖 论文阅读
- 🔬 实验验证
- 📊 数据分析

Status:
- ⏳ 未开始
- 🔄 进行中
- ✅ 已完成
- 📅 延期
- ❌ 取消

Priority:
- 🔴 P0-极高
- 🟠 P1-高
- 🟡 P2-中
- 🟢 P3-低

Deliverable:
- 💻 代码/脚本
- 📄 笔记/文档
- 📊 报告
- 🎥 视频
- 📸 截图
- 🔗 链接
- 📦 其他

Tags:
- #考试周
- #突发任务
- #需延期
- #加急处理
- #优质成果
- #需AI反馈
```

---

### 表3: 学习进度追踪 (Progress Tracking)

**数据库名**: `Daily Progress`

| 属性名 | 类型 | 是否必需 | 说明 |
|-------|------|--------|------|
| **Date** | Date | ✅ | 学习日期 |
| **Duration Hours** | Number | ✅ | 学习时长（小时） |
| **Course** | Relation | ✅ | 双向关联课程（自动反向属性：Progress Items） |
| **Learning Content** | Rich Text | ✅ | 学习内容简述 |
| **Efficiency Score** | Number | ✅ | 效率评分 1-10 |
| **Learning Method** | Select | ✅ | 学习形式：视频/阅读/编码/讨论/实验 |
| **Notes Count** | Number | ⭕ | 笔记数量 |
| **Questions** | Rich Text | ⭕ | 遇到的问题 |
| **Completed Tasks** | Number | ⭕ | 当日完成任务数 |
| **Reflection** | Rich Text | ⭕ | 学习反思与心得 |
| **Evidence** | URL | ⭕ | 证明链接（代码提交、截图等） |
| **Tags** | Multi-select | ⭕ | 标签 |

---

### 表4: 模板库 (Template Library)

**数据库名**: `Learning Templates`

| 属性名 | 类型 | 是否必需 | 说明 |
|-------|------|--------|------|
| **Title** | Title | ✅ | 模板名称 |
| **Type** | Select | ✅ | 模板类型：周计划/日计划/笔记/费曼讲解/复习卡片/项目提案 |
| **Content** | Rich Text | ✅ | 模板内容（Markdown格式） |
| **Last Used** | Date | ⭕ | 最后使用日期 |
| **Usage Count** | Number | ⭕ | 使用频率 |
| **Tags** | Multi-select | ⭕ | 标签 |

**预设模板示例**:

#### 周计划模板
```markdown
# 📅 第X周学习计划 (YYYY-MM-DD ~ YYYY-MM-DD)

## 本周目标
- [ ] 目标1
- [ ] 目标2
- [ ] 目标3

## 课程安排
| 课程 | 周一 | 周二 | 周三 | 周四 | 周五 | 周六 | 周日 |
|-----|------|------|------|------|------|------|------|
| 课程1 | 2h | - | 2h | - | 1h | - | - |
| 课程2 | - | 2h | - | 2h | - | - | - |

## 关键任务
- [ ] [P0] 任务1 - 截止XX日
- [ ] [P1] 任务2 - 截止XX日

## 复习安排（艾宾浩斯）
- [ ] D+1: 上周课程回顾
- [ ] D+3: 做相关练习题
- [ ] D+7: 讲解视频记录

## 预期产出物
1. 代码提交：链接
2. 笔记完成：链接
3. 视频总结：(可选)

## 周末总结（Friday 20:00 填写）
- 本周完成度：__%
- 遇到的主要难题：
- 下周改进方向：
```

#### 费曼讲解卡片模板
```markdown
# 费曼讲解卡片

**学习内容**: [具体内容]  
**学习时间**: YYYY-MM-DD  
**复习周期**: D+1 ☐ | D+3 ☐ | D+7 ☐

## 概念理解
用你自己的语言解释这个概念，假设你在教一个5年级的小孩：

---

## 关键步骤
1.
2.
3.

## 常见错误
- 错误1：
- 错误2：

## 应用例子
举一个实际的使用例子：

---

## 相关资源
- 视频：
- 论文：
- 代码：
```

---

### 表5: 考试与重要事件 (Events Calendar)

**数据库名**: `Important Events`

| 属性名 | 类型 | 是否必需 | 说明 |
|-------|------|--------|------|
| **Title** | Title | ✅ | 事件名称 |
| **Type** | Select | ✅ | 事件类型：考试/工作截止/会议/假期/纪念日 |
| **Date** | Date | ✅ | 事件日期 |
| **Duration** | Number | ⭕ | 持续时间（小时） |
| **Priority** | Select | ✅ | 优先级 |
| **Related Courses** | Relation | ⭕ | 双向关联课程（自动反向属性：Related Events） |
| **Prep Progress** | Percentage | ⭕ | 准备进度 |
| **Reminders** | Multi-select | ⭕ | 提醒时机：-7天/-3天/-1天/当天上午/当天 |
| **Notes** | Rich Text | ⭕ | 备注 |

---

### 表6: 学习资源库 (Resource Repository)

**数据库名**: `Learning Resources`

| 属性名 | 类型 | 是否必需 | 说明 |
|-------|------|--------|------|
| **Title** | Title | ✅ | 资源名称 |
| **Type** | Select | ✅ | 资源类型：教程/论文/代码/工具/数据集/视频 |
| **URL** | URL | ✅ | 资源链接 |
| **Related Courses** | Relation | ⭕ | 双向关联课程（自动反向属性：Related Resources） |
| **Priority** | Select | ⭕ | 优先级 |
| **Status** | Select | ⭕ | 阅读状态：未读/阅读中/已读/已归档 |
| **Notes** | Rich Text | ⭕ | 个人笔记 |
| **Tags** | Multi-select | ⭕ | 标签 |

---

## 🔗 集成配置

### Notion-GitHub集成

1. **GitHub密钥获取**:
   - 访问 https://github.com/settings/tokens
   - 创建 Personal Access Token (classic)
   - 权限勾选：repo、gist、workflow
   - 保存密钥

2. **创建学习仓库**:
   ```bash
   git init heritage-learning
   cd heritage-learning
   echo "# 文化遗产数字化学习仓库" > README.md
   git add .
   git commit -m "init: 初始化学习仓库"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/heritage-learning.git
   git push -u origin main
   ```

3. **配置.env文件**:
   ```
   NOTION_API_KEY=your_notion_api_key_here
   NOTION_DATABASE_ID=your_course_database_id
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO=your_username/heritage-learning
   CHATGPT_API_KEY=your_openai_api_key
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   ```

---

## 📱 Apple日历集成 (Zapier方案)

1. **注册Zapier账户**: https://zapier.com/
2. **创建Zap**:
   - 触发器: Notion - Database (new item)
   - 操作: Apple Calendar - Create Event
3. **映射字段**:
   - Notion的"Due Date" → Apple日历的"开始日期"
   - Notion的"Title" → Apple日历的"标题"
   - Notion的"Priority" → Apple日历的"描述"

---

## 🚀 快速开始

### 第1步: 创建所有表（5分钟）

在Notion中按照上述结构创建6个数据库表：

1. Course Management
2. Task Management
3. Daily Progress
4. Learning Templates
5. Important Events
6. Learning Resources

### 第2步: 初始化Python环境（10分钟）

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 第3步: 配置环境变量（5分钟）

创建 `.env` 文件，填入所有API密钥

### 第4步: 第一次运行（5分钟）

```bash
python automation_scripts/learning_system_core.py
```

### 第5步: 配置定时任务

**Windows (Task Scheduler)**:
```
创建任务 → 触发器: 每天 6:30 AM
操作: 运行程序 → 选择 python.exe
参数: D:\path\to\learning_system_core.py
```

**macOS/Linux (Cron)**:
```bash
crontab -e
# 添加行: 30 6 * * * /path/to/venv/bin/python /path/to/learning_system_core.py
```

---

## ✅ 验证清单

- [ ] 所有6个Notion表已创建
- [ ] API密钥已保存到.env文件
- [ ] Python脚本可成功运行
- [ ] GitHub Issues已同步创建
- [ ] 至少一封测试邮件已发送
- [ ] Apple日历已收到测试事件
- [ ] Obsidian已同步笔记

---

## 📞 故障排除

### 问题1: Notion API返回403错误
**解决**: 检查Integration是否已添加到工作区，Database ID是否正确

### 问题2: GitHub Issue创建失败
**解决**: 验证GitHub Token权限，确保repo可写

### 问题3: 邮件发送失败
**解决**: 
- Gmail用户: 使用"应用专用密码"而非账户密码
- 其他邮箱: 检查SMTP配置和端口

### 问题4: Apple日历事件未出现
**解决**: 确认Zapier已激活，检查映射字段是否正确

### 问题5: Obsidian同步脚本报 "Could not find database" 错误
**解决**: 
- 确保 `notion_databases.json` 存在且包含 Task Management ID
- 或在 `.env` 中设置 `NOTION_DATABASE_ID=<Task Management DB ID>`
- 运行 `python automation_scripts\create_notion_schema.py` 重新生成数据库

---

## 📚 参考资源

- [Notion API 官方文档](https://developers.notion.com/)
- [GitHub API 文档](https://docs.github.com/en/rest)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Zapier 集成指南](https://zapier.com/help/connect/integrations)

