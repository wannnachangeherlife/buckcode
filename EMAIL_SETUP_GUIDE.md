# 📧 Gmail 应用专用密码配置指南

## 问题说明

你遇到的错误：
```
邮件发送失败: (535, b'5.7.8 Username and Password not accepted.')
```

这是因为 Gmail 不再支持直接使用账户密码通过 SMTP 发送邮件，需要使用"应用专用密码"。

---

## ✅ 解决方案：生成应用专用密码

### 步骤 1：启用两步验证

1. 访问：https://myaccount.google.com/security
2. 找到"两步验证"（2-Step Verification）
3. 如未启用，点击启用并完成设置

### 步骤 2：生成应用专用密码

1. 访问：https://myaccount.google.com/apppasswords
   - 或在"两步验证"页面底部找到"应用专用密码"
2. 选择应用：**邮件**
3. 选择设备：**Windows 电脑** 或 **其他**
4. 点击"生成"
5. **复制生成的 16 位密码**（格式：`xxxx xxxx xxxx xxxx`）

### 步骤 3：更新 .env 文件

将生成的应用专用密码（去掉空格）替换到 `.env`：

```env
EMAIL_USER=ShirleyvsJune@iCloud.com
EMAIL_PASSWORD=<你的16位应用专用密码>
```

**示例**：
```env
EMAIL_PASSWORD=abcdwxyzefgh1234
```

---

## 🔄 替代方案：使用 iCloud 邮箱

如果你使用的是 iCloud 邮箱，配置如下：

### iCloud SMTP 设置

```env
EMAIL_USER=ShirleyvsJune@iCloud.com
EMAIL_PASSWORD=<iCloud应用专用密码>
EMAIL_SMTP_SERVER=smtp.mail.me.com
EMAIL_SMTP_PORT=587
```

### 生成 iCloud 应用专用密码

1. 访问：https://appleid.apple.com/
2. 登录后，在"安全"部分找到"应用专用密码"
3. 点击"生成密码"
4. 输入标签（如"学习系统邮件"）
5. 复制生成的密码到 `.env`

---

## 🧪 测试邮件发送

更新密码后，运行测试脚本：

```powershell
# 测试邮件发送
python automation_scripts\test_email.py
```

---

## 📝 更新 learning_system_core.py

如果你使用 iCloud 邮箱，需要修改 SMTP 服务器配置：

在 `.env` 中添加：
```env
EMAIL_SMTP_SERVER=smtp.mail.me.com  # iCloud SMTP
EMAIL_SMTP_PORT=587                  # TLS 端口
```

或者保持 Gmail（推荐）：
```env
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

---

## ✅ 当前推荐配置

**选项 A：Gmail（推荐）**
```env
EMAIL_USER=你的Gmail地址@gmail.com
EMAIL_PASSWORD=<16位应用专用密码>
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

**选项 B：iCloud（你当前的邮箱）**
```env
EMAIL_USER=ShirleyvsJune@iCloud.com
EMAIL_PASSWORD=<iCloud应用专用密码>
EMAIL_SMTP_SERVER=smtp.mail.me.com
EMAIL_SMTP_PORT=587
```

---

## 🔗 参考链接

- [Gmail 应用专用密码](https://support.google.com/accounts/answer/185833)
- [iCloud 应用专用密码](https://support.apple.com/zh-cn/102654)
