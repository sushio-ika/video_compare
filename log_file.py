import os
from datetime import datetime

def add_log(message, category="INFO"):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{category}] {message}\n"
        
        with open("ml.log", "a", encoding="utf-8") as f:
            f.write(log_message)
            
    except Exception as e:
        print(f"ログの書き込みに失敗: {e}")