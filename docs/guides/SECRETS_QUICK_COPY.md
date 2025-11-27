# 🔑 GitHub Actions Secrets 快速复制清单

⚠️ **重要**: GitHub 不允许 Secret 名称以 `GITHUB_` 开头！

---

## 📝 复制这些值到 GitHub Secrets

访问: https://github.com/wannnachangeherlife/Heritage-Learning-System/settings/secrets/actions

---

### ✅ Secret 1
**Name:**
```
NOTION_API_KEY
```
**Value:**
```
ntn_YOUR_NOTION_INTEGRATION_SECRET_HERE
```

---

### ✅ Secret 2
**Name:**
```
NOTION_DATABASE_ID
```
**Value:**
```
2b765c6c-735f-81b3-b7cc-c7101f48a952
```

---

### ✅ Secret 3 ⚠️ 改名
**Name:** (不能用 GITHUB_TOKEN)
```
GH_TOKEN
```
**Value:**
```
ghp_YOUR_GITHUB_PERSONAL_ACCESS_TOKEN_HERE
```

---

### ✅ Secret 4 ⚠️ 改名
**Name:** (不能用 GITHUB_REPO)
```
GH_REPO
```
**Value:**
```
wannnachangeherlife/Heritage-Learning-System
```

---

### ✅ Secret 5
**Name:**
```
AI_API_KEY
```
**Value:**
```
sk-YOUR_DEEPSEEK_API_KEY_HERE
```

---

### ✅ Secret 6
**Name:**
```
AI_BASE_URL
```
**Value:**
```
https://api.deepseek.com
```

---

### ✅ Secret 7
**Name:**
```
AI_MODEL
```
**Value:**
```
deepseek-chat
```

---

### ✅ Secret 8
**Name:**
```
EMAIL_USER
```
**Value:**
```
ShirleyvsJune@iCloud.com
```

---

### ✅ Secret 9
**Name:**
```
EMAIL_PASSWORD
```
**Value:**
```
xxxx-xxxx-xxxx-xxxx
```

---

### ✅ Secret 10
**Name:**
```
EMAIL_SMTP_SERVER
```
**Value:**
```
smtp.mail.me.com
```

---

### ✅ Secret 11
**Name:**
```
EMAIL_SMTP_PORT
```
**Value:**
```
587
```

---

## ✅ 完成检查清单

添加完所有 Secrets 后：

- [ ] 已添加 NOTION_API_KEY
- [ ] 已添加 NOTION_DATABASE_ID
- [ ] 已添加 GH_TOKEN (不是 GITHUB_TOKEN)
- [ ] 已添加 GH_REPO (不是 GITHUB_REPO)
- [ ] 已添加 AI_API_KEY
- [ ] 已添加 AI_BASE_URL
- [ ] 已添加 AI_MODEL
- [ ] 已添加 EMAIL_USER
- [ ] 已添加 EMAIL_PASSWORD
- [ ] 已添加 EMAIL_SMTP_SERVER
- [ ] 已添加 EMAIL_SMTP_PORT

**总计: 11 个 Secrets**

---

## 🧪 测试运行

1. 访问: https://github.com/wannnachangeherlife/Heritage-Learning-System/actions
2. 点击 "Periodic Learning Tasks"
3. 点击 "Run workflow" → "Run workflow"
4. 等待 2-3 分钟查看结果

---

## 💡 提示

- 复制时不要包含反引号 ` ``` `
- 确保没有多余的空格
- GH_TOKEN 和 GH_REPO 是必须的改名（GitHub 限制）
