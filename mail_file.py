import tkinter as tk
import os

from tkinter import messagebox
from smtplib import SMTP,SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv()

# メール送信処理
def send_mail(form, body):
    # 送信に必要な情報を定数で定義
    ID = "murtilink1104@gmail.com"
    PASS = os.environ.get("APPLI_PASSWD")
    if PASS == None:
        messagebox.showerror("エラー","パスワードが環境変数に設定されていません")
        return
    
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
    
    try:
        # SMTPサーバへ接続し、TLS通信開始
        server=SMTP(HOST, PORT)
        server.starttls()
        server.login(ID, PASS) # ログイン認証処理
        server.send_message(msg)    # メール送信処理
    except SMTPException as e:
        messagebox.showerror("エラー","メールサーバー接続または送信処理でエラーが発生しました:{e}")
    except Exception as e:
        messagebox.showerror("エラー",f"予期せぬエラーが発生しました:{e}")
    else:
        server.quit()       # TLS通信終了
        messagebox.showinfo("情報","メールが送信されました")
