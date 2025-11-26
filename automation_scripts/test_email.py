"""
test_email.py

快速测试邮件发送配置是否正确
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))

def send_test_email():
    """发送测试邮件"""
    print(f"📧 邮件配置信息：")
    print(f"  服务器: {EMAIL_SMTP_SERVER}:{EMAIL_SMTP_PORT}")
    print(f"  发件人: {EMAIL_USER}")
    print(f"  密码长度: {len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 0} 字符")
    print()
    
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("❌ 错误：EMAIL_USER 或 EMAIL_PASSWORD 未配置")
        return
    
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER  # 发给自己测试
        msg['Subject'] = '🎉 学习系统邮件测试 - 配置成功！'
        
        body = """
        <html>
        <body>
            <h2>✅ 邮件配置成功！</h2>
            <p>你的学习管理系统邮件功能已正常工作。</p>
            <p>接下来你将收到：</p>
            <ul>
                <li>每日学习摘要</li>
                <li>任务截止提醒</li>
                <li>周学习报告</li>
                <li>AI 反馈通知</li>
            </ul>
            <hr>
            <p><small>发送时间: {}</small></p>
        </body>
        </html>
        """.format(os.popen('powershell -Command "Get-Date -Format \'yyyy-MM-dd HH:mm:ss\'"').read().strip())
        
        msg.attach(MIMEText(body, 'html'))
        
        # 发送邮件
        print("🔄 正在连接 SMTP 服务器...")
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            print("🔄 正在登录...")
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            print("🔄 正在发送邮件...")
            server.send_message(msg)
        
        print(f"\n✅ 测试邮件发送成功！")
        print(f"📬 请检查你的邮箱：{EMAIL_USER}")
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ 认证失败！")
        print("\n可能的原因：")
        print("1. 密码错误")
        print("2. 未使用应用专用密码（Gmail/iCloud 需要）")
        print("3. 账户安全设置阻止了登录")
        print("\n解决方案：")
        print("📖 请查看 EMAIL_SETUP_GUIDE.md 获取详细配置指南")
        
    except Exception as e:
        print(f"\n❌ 发送失败：{e}")
        print("\n请检查：")
        print("1. SMTP 服务器地址和端口是否正确")
        print("2. 网络连接是否正常")
        print("3. 防火墙是否阻止了连接")

if __name__ == '__main__':
    send_test_email()
