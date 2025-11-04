import os

from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv()

# メール送信処理
def send_mail(form, body):
    # 送信に必要な情報を定数で定義
    ID = "murtilink1104@gmail.com"
    PASS = os.environ.get("APPLI_PASSWD")
    TO="rik1104business@gmail.com"
    HOST = "smtp.gmail.com"
    PORT = 587

    # メール本文を設定
    msg = MIMEMultipart()
    msg.attach(MIMEText(body, "html"))

    # 件名、送信元アドレス、送信先アドレスを設定
    msg["Subject"] = "マルチリンク問い合わせ"
    msg["From"] = ID
    msg["To"] = TO
    
    # SMTPサーバへ接続し、TLS通信開始
    server=SMTP(HOST, PORT)
    server.starttls()

    server.login(ID, PASS) # ログイン認証処理

    server.send_message(msg)    # メール送信処理

    server.quit()       # TLS通信終了
