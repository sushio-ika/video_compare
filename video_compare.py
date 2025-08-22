import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
import cv2
from PIL import Image, ImageTk
import threading
import os
from tkinterdnd2 import TkinterDnD

PICTURE_WIDTH = 320  #動画表示の横幅を固定

#DPI設定（Windowsでの高解像度対応）
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

#VideoAppはメインウィンドウを定義
class videocompare(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("動画比較アプリ")
        self.geometry("800x600")
        self.tk_setPalette(background="#2E2E2E", foreground="#FFFFFF")

        #複数の動画を管理するリスト
        self.video_captures = {}  # {ファイルパス: cv2.VideoCaptureオブジェクト}
        self.video_labels = []    # 動画を表示するLabelウィジェットのリスト
        
        self.create_widgets()

        self.bind("<Button-3>", lambda event: self.right_clickmenu(event))
        self.bind("<Button-1>", lambda event: self.left_clickmovie(event, None, None))

    def create_widgets(self):
        """UI部品の配置""" 
        #ドロップエリア（Labelウィジェットとして作成）
        self.drop_area = tk.Label(self, text="ここに動画をドラッグ＆ドロップ",relief="solid", bd=1, width=60, height=20)
        self.drop_area.pack(pady=10, fill=tk.BOTH, expand=True)
        self.drop_area.config(bg="#3C3F41", fg="#FFFFFF")

        #ファイル選択ボタン
        self.select_button = tk.Button(self, text="動画を選択", command=self.select_video_file)
        self.select_button.pack(pady=5)
        self.select_button.config(bg="#3D94CE", fg="#FFFFFF")

        # tkinterdnd2を使ってドラッグ＆ドロップ機能を有効化
        self.drop_area.drop_target_register(1, 'DND_Files')
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop_files)
        
        # 動画表示用のフレーム
        self.video_frame = tk.Frame(self)
        self.video_frame.pack(fill=tk.BOTH, expand=True)

    def on_drop_files(self, event):
        """ドロップされたファイルを処理する関数"""
        files = self.tk.splitlist(event.data)
        for file_path in files:
            if file_path.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                self.add_video_to_app(file_path)

    def select_video_file(self):
        """ファイルダイアログから動画を選択する関数"""
        filepath = filedialog.askopenfilename(
            title="動画を選択してください",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if filepath:
            self.add_video_to_app(filepath)
    
    def add_video_to_app(self, file_path):
        """動画をアプリに追加し、再生を準備する関数"""
        if file_path in self.video_captures:
            messagebox.showinfo("情報", "この動画はすでに追加されています。")
            return
        
        capture = cv2.VideoCapture(file_path)
        if not capture.isOpened():
            messagebox.showerror("エラー", f"動画ファイルを開けませんでした: {file_path}")
            return
            
        #新しい動画表示用のラベルを作成し、フレームに追加
        video_label = tk.Label(self.video_frame)
        video_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        #ラベルのサイズ変更
        width = PICTURE_WIDTH  #横幅固定
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) * (PICTURE_WIDTH / capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
        video_label.config(width=width, height=height)

        self.video_labels.append(video_label)
        self.video_captures[file_path] = capture
        
        #再生用のスレッドを開始
        thread = threading.Thread(target=self.play_video, args=(capture, video_label))
        thread.daemon = True#メインウィンドウが閉じたらスレッドも終了
        thread.start()

        #動画追加ボタンとドラッグアンドドロップの枠を非表示
        self.drop_area.pack_forget()
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        self.select_button.pack_forget()

    def play_video(self, capture, video_label):
        """動画を再生する関数"""
        while capture.isOpened():
            ret, frame = capture.read()
            if not ret:
                break
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = ImageTk.PhotoImage(img)
            
            # Tkinterの更新
            video_label.config(image=img)
            video_label.image = img
            
            # 適切な再生速度に調整
            delay = 1000 // int(capture.get(cv2.CAP_PROP_FPS))
            cv2.waitKey(delay)

        capture.release()

    def left_clickmovie(self, event, img_path, img_name):
        """動画がクリックされたときの処理"""
        # クリックされた動画の画像をハイライトする
        self.apply_image_highlight(img_name, True)

    def apply_image_highlight(self,image_name, highlight_on):
        """動画に枠線を適用する関数"""
        for label in self.video_labels:
            if label.image == image_name:
                if highlight_on:
                    label.config(bd=2, relief=tk.RAISED)
                else:
                    label.config(bd=0)

    def edit_undo(self):
        """操作を1つ戻す"""
        self.event_generate("<<Undo>>")

    def right_clickmenu(self, event):
        """右クリックメニューを表示する関数"""
        menu = tk.Menu(self, tearoff=0)
        
        menu.add_command(label="ヘルプ", command=self.show_how_to_use)
        menu.add_command(label="設定", command=self.show_settings) 
        menu.add_separator()
        menu.add_command(label="一つ戻す", command=self.put_one_back)
        menu.add_command(label="一つ進める", command=self.put_one_forward)
        menu.add_separator()
        menu.add_command(label="コピー", command=self.copy_video)
        menu.add_command(label="貼り付け", command=self.paste_video)
        menu.add_command(label="切り取り", command=self.cut_video)
        menu.add_command(label="削除", command=self.delete_video)
        menu.add_separator()

        save_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="保存", menu=save_menu)
        save_menu.add_command(label="上書き保存", command=lambda: self.save_file(overwrite=True))
        save_menu.add_command(label="名前を付けて保存", command=lambda: self.save_file(overwrite=False))
        
        open_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="開く", menu=open_menu)
        open_menu.add_command(label="ファイルを開く", command=self.open_file)
        open_menu.add_command(label="動画を開く", command=self.select_video_file)
        
        menu.add_command(label="新規作成", command=self.new_file)
        menu.add_separator()
        menu.add_command(label="終了", command=self.quit)
        
        menu.post(event.x_root, event.y_root)

    def show_how_to_use(self):
        """使い方を表示"""
        messagebox.showinfo(
            "動画比較アプリの使い方",
            "1. 動画を選択するには、「動画を選択」ボタンをクリックします。\n"
            "2. 動画が再生されます。左クリックで動画を選択し、右クリックでメニューを表示します。\n"
        )

    def show_settings():
        """設定メニューを表示"""
    
    def put_one_back(self):
        """操作を1つ戻す"""
        self.edit_undo()

    def put_one_forward(self):
        """操作を1つ進める"""
        self.edit_redo()

    def copy_video(self):
        """動画をコピーする"""
        self.event_generate("<<Copy>>")

    def paste_video(self):
        """動画を貼り付ける"""
        self.event_generate("<<Paste>>")

    def cut_video(self):
        """動画を切り取る"""
        self.event_generate("<<Cut>>")

    def delete_video(self):
        """動画を削除する"""
        self.event_generate("<<Delete>>")

    def save_file(self, overwrite=False):
        """動画を保存する"""

    def open_file(self):
        """動画を開く"""

    def new_file(self):
        """新しい動画を作成する"""


if __name__ == '__main__':
    app = videocompare()
    app.mainloop()