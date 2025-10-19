import os
from datetime import datetime

def init_log():
    """ログファイルの初期化"""
    # ログファイルの内容をすべて消去
    try:
        with open("ml.log", "w", encoding="utf-8") as f:
            f.write("")  # 空の内容で上書き
    except Exception as e:
        print(f"ログファイルの初期化に失敗: {e}")


def add_log(message, category="INFO"):
    """ログファイルにメッセージを追加"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{category}] {message}\n"
        
        with open("ml.log", "a", encoding="utf-8") as f:
            f.write(log_message)
            
    except Exception as e:
        print(f"ログの書き込みに失敗: {e}")