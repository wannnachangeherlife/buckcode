# buckcode
just for my heritage

## GitHub Actions

- 必需 Secrets（Repository Secrets）：`NOTION_API_KEY`, `NOTION_DATABASE_ID`, `GH_TOKEN`, `GH_REPO`, `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_SMTP_SERVER`, `EMAIL_SMTP_PORT`。
- 健康检查（Health Check）：进入仓库的 Actions 选项卡，选择 “Health Check” 工作流，点击 “Run workflow”。若缺失 Secrets 或外部连通性异常，步骤会以 “Process completed with exit code 1” 结束并输出 JSON 报告。
- 周期任务（Periodic Learning Tasks）：同样在 Actions 里选择 “Periodic Learning Tasks”，手动运行或等待定时触发。

### 常见问题

- Exit code 1：多由 Secrets 未配置或配置错误导致。请先补齐 Secrets 后再次运行 “Health Check”。
- Notion 404 或权限错误：确认 `NOTION_API_KEY` 有访问目标数据库权限，`NOTION_DATABASE_ID` 正确无空格。
- GitHub 401/404：确认 `GH_TOKEN` 具备 `repo` 权限，`GH_REPO` 形如 `owner/repo`。
- 邮件 TLS/登录失败：检查 `EMAIL_SMTP_SERVER`/`EMAIL_SMTP_PORT` 与账户的应用专用密码是否正确。
