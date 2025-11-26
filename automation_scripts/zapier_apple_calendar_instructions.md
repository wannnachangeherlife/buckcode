# Zapier: 将 Notion 任务同步到 Apple 日历（操作说明）

说明：Zapier 可将 Notion 中的任务自动创建为 Apple Calendar 事件，适用于 iPhone/iPad 的即时提醒。若您偏向国内自动化工具，也可以使用 IFTTT 或者 n8n。

预置条件：
- 已有 Notion Integration，并将目标数据库（Task Management）共享给该 Integration
- 已有 Zapier 账户（https://zapier.com）
- Apple ID 已在 iCloud 中登录且启用了日历

步骤：

1. 创建 Zap
- 触发器（Trigger）选择：Notion → New Database Item
- 选择您的 Notion 账户并授权
- 选择数据库：Task Management

2. 增加条件（可选）
- 添加 "Filter"：例如只同步 Priority 为 P0/P1 或 Status 不为 已完成 的任务

3. 操作（Action）选择：Apple Calendar → Create Detailed Event
- 事件标题 （Title）：映射 Notion 的 `Title`
- 开始时间（Start Date）：映射 Notion 的 `Due Date` （若无时间，默认全天事件）
- 结束时间（End Date）：可设置为 `Due Date + 1 hour` 或与 `Duration` 映射
- 描述（Description）：映射 Notion 的 `Priority`、`Related Course`、`Notes`
- 提醒（Reminders）：Zapier 的 Apple Calendar 操作不直接允许设置 iOS 本地推送时间，可在描述中包含提醒信息或配合 iOS Shortcuts

4. 测试并打开 Zap
- 创建测试 Notion 记录，观察是否出现在 Apple Calendar 中

示例 Webhook/日志字段（仅供参考）
```json
{
  "title": "建立PyTorch环境并验证GPU",
  "due_date": "2025-12-07",
  "priority": "P1-高",
  "course": "PyTorch深度学习",
  "notes": "在台式机上测试 CUDA 驱动"
}
```

高级整合：
- 若要在事件触发时弹出 iPhone 本地通知，可使用 Shortcuts（捷径）：创建一个 Shortcut，当日历事件被打开或达到时间时发送本地通知；或配合 Pushcut 服务实现更复杂的触发。
- 国内用户：若Zapier受限，可使用 `n8n` 部署到 VPS 或使用 `IFTTT` 的 Notion 触发器（功能可能限制）。

常见问题：
- Zapier 里看不到 Notion 数据库：请确认 Integration 已被添加到相应页面的共享设置。
- Apple Calendar 事件未出现：检查 Zap 是否开启，并确认 Zapier 账户与 Apple ID 已正确授权（部分 Apple Calendar 功能在 Zapier 需借助 iCloud 中继服务）。

建议流程：
1. 在 Notion 中创建一个测试任务（设置 Due Date 为明天）；
2. 在 Zapier 中运行测试触发；
3. 若事件未出现，检查 Zap 日志并按日志提示修正字段映射；
4. 开启 Zap 并在 iPhone/iPad 上确认提醒。
