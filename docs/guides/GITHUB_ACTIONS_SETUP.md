# GitHub Actions Secrets 配置清单

## 📋 访问地址
https://github.com/wannnachangeherlife/Heritage-Learning-System/settings/secrets/actions

---

## 🔑 需要添加的 Secrets

### 1. NOTION_API_KEY
```
ntn_YOUR_NOTION_INTEGRATION_SECRET
```

### 2. NOTION_DATABASE_ID
**使用 TASK_DB_ID 的值：**
```
2b765c6c-735f-81b3-b7cc-c7101f48a952
```

### 3. GH_TOKEN
**⚠️ 注意：不能使用 GITHUB_TOKEN（GitHub 保留名称），改用 GH_TOKEN**
```
ghp_YOUR_GITHUB_PERSONAL_ACCESS_TOKEN
```

### 4. GH_REPO
**⚠️ 注意：不能使用 GITHUB_REPO（GitHub 保留名称），改用 GH_REPO**
```
wannnachangeherlife/Heritage-Learning-System
```

### 5. AI_API_KEY
```
sk-b47011acc56547f2a9639da9f2d2c02c
```

### 6. AI_BASE_URL
```
https://api.deepseek.com
```

### 7. AI_MODEL
```
deepseek-chat
```

### 8. EMAIL_USER
```
ShirleyvsJune@iCloud.com
```

### 9. EMAIL_PASSWORD
**⚠️ 这是你的 iCloud 应用专用密码：**
```
vzfy-nqkk-prrn-eely
```

### 10. EMAIL_SMTP_SERVER
```
smtp.mail.me.com
```

### 11. EMAIL_SMTP_PORT
```
587
```

---

## ✅ 配置步骤

1. **打开 GitHub Secrets 页面**
   ```
   https://github.com/wannnachangeherlife/Heritage-Learning-System/settings/secrets/actions
   ```

2. **对于每个 Secret：**
   - 点击 "New repository secret"
   - Name: 输入上面的 Secret 名称（例如：`NOTION_API_KEY`）
   - Value: 复制对应的值
   - 点击 "Add secret"

3. **重复步骤 2，直到添加完所有 Secrets**

**总共需要添加 11 个 Secrets**（注意 GITHUB_TOKEN 和 GITHUB_REPO 要改名为 GH_TOKEN 和 GH_REPO）

---

## 🔍 验证配置

添加完所有 Secrets 后：

1. 访问 Actions 页面：
   ```
   https://github.com/wannnachangeherlife/Heritage-Learning-System/actions
   ```

2. 手动触发工作流：
   - 点击左侧 "Periodic Learning Tasks"
   - 点击右侧 "Run workflow"
   - 选择 branch: main
   - 点击绿色的 "Run workflow" 按钮

3. 查看运行结果：
   - 等待几分钟
   - 查看是否成功（绿色 ✓）
   - 如果失败，点击查看日志定位问题

---

## 📅 自动运行时间

配置完成后，工作流将在以下时间自动运行：
- **每天 06:30 UTC**（北京时间 14:30）
- **每天 22:00 UTC**（北京时间次日 06:00）

你也可以在 `.github/workflows/periodic_tasks.yml` 中修改 `cron` 表达式来调整时间。

---

## 💡 提示

- ✅ 所有敏感信息（API Keys、Tokens）都安全存储在 GitHub Secrets 中
- ✅ 这些 Secrets 不会出现在日志中
- ✅ 只有仓库管理员可以查看和修改
- ⚠️ 如果需要更新某个 Secret，直接在同一页面修改即可

---

## 🐛 常见问题

**Q: Secret 添加后无法使用？**
A: 确保 Secret 名称完全匹配（区分大小写），且没有多余的空格。

**Q: 工作流运行失败？**
A: 检查 Actions 日志，可能是某个 Secret 的值不正确。

**Q: 如何修改定时运行时间？**
A: 编辑 `.github/workflows/periodic_tasks.yml` 中的 `cron` 值。

**Q: 如何停止自动运行？**
A: 在 Actions 页面禁用工作流，或删除 `.github/workflows/periodic_tasks.yml` 文件。

---

## 📝 下一步

配置完成后：
1. ✅ 手动运行一次工作流验证
2. ✅ 查看运行日志确认无错误
3. ✅ 等待下一次自动运行（北京时间 14:30 或次日 06:00）
4. ✅ 检查 Notion、邮箱、Obsidian 是否正常同步

---

**准备好了吗？现在就可以开始添加 Secrets！**
