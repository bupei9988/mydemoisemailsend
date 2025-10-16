# multi_mailer.py
import json
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# 读取配置文件
CONFIG_FILE = "config.json"

def load_config():
    if not Path(CONFIG_FILE).is_file():
        raise FileNotFoundError(f"配置文件 {CONFIG_FILE} 不存在！")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def setup_logging(log_config):
    logfile = log_config.get("logfile", "multi_mailer.log")
    level_str = log_config.get("level", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    logging.basicConfig(
        filename=logfile,
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def send_email(account, to_email, subject, body):
    """
    发送邮件函数，同时打印控制台和写入日志
    """
    msg = MIMEMultipart()
    msg["From"] = f"{account.get('from_name')} <{account.get('email')}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        if account.get("use_ssl", False):
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(account["smtp_server"], account["smtp_port"], context=context) as server:
                server.login(account["username"], account["password"])
                server.sendmail(account["email"], to_email, msg.as_string())
        else:
            with smtplib.SMTP(account["smtp_server"], account["smtp_port"]) as server:
                if account.get("use_starttls", False):
                    server.starttls()
                server.login(account["username"], account["password"])
                server.sendmail(account["email"], to_email, msg.as_string())

        log_msg = f"[SUCCESS] 邮箱 {account['email']} 发送给 {to_email}"
        logging.info(log_msg)
        print(log_msg)  # 控制台打印成功信息

    except Exception as e:
        log_msg = f"[FAILED] 邮箱 {account['email']} 发送给 {to_email} 失败: {e}"
        logging.error(log_msg)
        print(log_msg)  # 控制台打印失败信息

def main():
    config = load_config()
    setup_logging(config.get("logging", {}))
    to_email = input("请输入收件邮箱地址: ").strip()
    subject = input("请输入邮件主题: ").strip()
    body = input("请输入邮件内容: ").strip()

    accounts = config.get("accounts", [])
    if not accounts:
        logging.warning("配置文件中没有邮箱账号！")
        print("配置文件中没有邮箱账号！")
        return

    for account in accounts:
        send_email(account, to_email, subject, body)

if __name__ == "__main__":
    main()
