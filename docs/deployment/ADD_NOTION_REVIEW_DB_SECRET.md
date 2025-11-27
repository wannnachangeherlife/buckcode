# 添加 GitHub Secret: NOTION_REVIEW_DB_ID

## 步骤

1. **打开 Heritage-Learning-System 仓库**
   - 访问: https://github.com/wannnachangeherlife/Heritage-Learning-System

2. **进入 Settings**
   - 点击仓库顶部的 `Settings` 标签

3. **找到 Secrets**
   - 左侧菜单: `Secrets and variables` → `Actions`

4. **添加新 Secret**
   - 点击 `New repository secret` 按钮
   
   **Name:**
   ```
   NOTION_REVIEW_DB_ID
   ```
   
   **Secret:**
   ```
   2b865c6c-735f-8173-b91c-f63c35e502b8
   ```

5. **保存**
   - 点击 `Add secret` 完成

## 验证

添加完成后,Heritage-Learning-System 仓库应该有以下 12 个 Secrets:

1. ✅ NOTION_API_KEY
2. ✅ NOTION_DATABASE_ID (任务管理数据库)
3. ✅ **NOTION_REVIEW_DB_ID** (复习数据库 - 新增)
4. ✅ GH_TOKEN
5. ✅ GH_REPO
6. ✅ AI_API_KEY
7. ✅ AI_BASE_URL
8. ✅ AI_MODEL
9. ✅ EMAIL_USER
10. ✅ EMAIL_PASSWORD
11. ✅ EMAIL_SMTP_SERVER
12. ✅ EMAIL_SMTP_PORT

## 下一步

添加完成后,可以手动触发 `Periodic Learning Tasks` workflow 进行测试。
