import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage,ttk
import cv2
from PIL import Image, ImageTk
import threading
import os
from tkinterdnd2 import TkinterDnD
import time

from menu_file import (delete_video)
from click_file import (left_click, right_clickmenu, on_mousewheel,double_left_click)
from create_item_file import (create_widgets)

#定数
WINDOW_MAX_SIZE=1280
WINDOW_MIN_SIZE=900
PICTURE_WIDTH = 400  #動画表示の横幅を固定

#DPI設定（Windowsでの高解像度対応）
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

#メインウィンドウを定義
class main(TkinterDnD.Tk):
    def __init__(form):
        super().__init__()
        # 変数の初期化
        form.current_file = None  #現在開いているファイルのパス
        form.resize_info = None  #サイズ変更の情報を保存する辞書
        form.selected_label = {}  #選択中の動画ラベルを管理する辞書
        form.video_info = {}      # 動画の情報を管理する辞書

        form.set_size = 3 # 動画の列数

        form.thread = None
        form.stop_flag = None

        # ウィンドウの基本設定
        form.title("マルチリンク -新規ファイル-")
        form.geometry(f"{WINDOW_MAX_SIZE}x{WINDOW_MIN_SIZE}")
        form.tk_setPalette(background="#2E2E2E", foreground="#FFFFFF")
        form.resizable(False, False)

        # ドラッグ＆ドロップの設定
        form.drop_target_register(1, 'DND_Files')
        form.dnd_bind('<<Drop>>', form.on_drop_files)

        create_widgets(form)

        form.bind("<Button-3>", lambda event: right_clickmenu(form, event))
        form.bind("<Button-1>", lambda event: left_click(form, event, False))
        form.bind("<Control-Button-1>", lambda event: left_click(form, event, True))
        form.bind("<MouseWheel>", lambda event: on_mousewheel(form, event))
        form.bind("<Double-Button-1>",lambda event: double_left_click(form,event))

        form.change_control_mode(tk.DISABLED)
        form.change_widget_mode(tk.DISABLED)
        form.change_size(form.set_size)

        #ウィンドウを中央に配置
        form.update_idletasks()

        x = (form.winfo_screenwidth() // 2) - (form.winfo_width() // 2)   #(画面の幅 // 2) - (ウィンドウの幅 // 2)
        y = (form.winfo_screenheight() // 2) - (form.winfo_height() // 2) #(画面の高さ // 2) - (ウィンドウの高さ // 2)

        form.geometry(f"+{x}+{y}")


    def back(form):
        """5秒巻き戻す"""

    def front(form):
        """5秒早送りする"""

    def toggle_play(form):
        """動画の再生/一時停止を切り替える"""
        form.paused = not form.paused
        if form.paused:
            form.btn_play_pause.config(text="▶")
        else:
            form.btn_play_pause.config(text="⏸")
            form.update()

        
    def on_drop_files(form, event):
        """ドロップされたファイルを処理する関数"""
        files = form.tk.splitlist(event.data)
        for file_path in files:
            if file_path.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                form.add_video(file_path)

    def select_video(form):
        """ファイルダイアログから動画を選択する関数"""
        filepath = filedialog.askopenfilename(
            title="動画を選択してください",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if filepath:
            form.add_video(filepath)
    
    def add_video(form, file_path):
        """動画をアプリに追加し、再生を準備する関数"""
        # すでに追加されている場合は無視
        if file_path in form.video_info:
            messagebox.showinfo("情報", "この動画はすでに追加されています。")
            return
        
        capture = cv2.VideoCapture(file_path)
        if not capture.isOpened():
            messagebox.showerror("エラー", f"動画ファイルを開けませんでした: {file_path}")
            return
            
        #動画表示用のラベルを作成
        video_label = tk.Label(form.video_frame, width=WINDOW_MAX_SIZE // form.set_size - 10, height=int((WINDOW_MAX_SIZE // form.set_size - 10) * 9 / 16))
        # 追加前にvideo_infoへ一時追加
        temp_count = len(form.video_info)  # 追加前の数
        col = temp_count % form.set_size
        row = temp_count // form.set_size
        video_label.grid(row=row, column=col, padx=5, pady=5)


        #再生用のスレッドを開始
        stop_flag = threading.Event()
        thread = None  # ← 再生スレッドは起動しない

        form.video_info[file_path] = {
            'capture': capture,
            'label': video_label, 
            'thread': thread, 
            'stop_flag': stop_flag,
            'last_frame': None
        }

        # 最初のフレームだけ表示
        ret, frame = capture.read()
        if ret:
            form.video_info[file_path]['last_frame'] = frame
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_height / frame_width
            new_width = WINDOW_MAX_SIZE // form.set_size - 10  # パディングを考慮
            new_height = int(new_width * aspect_ratio)
            resized_frame = cv2.resize(frame, (new_width, new_height))
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)
            form.update_label_image(video_label, img_tk)

        form.change_widget_mode(tk.NORMAL)
        
        # ヒントラベルを非表示にする
        # if form.lbl_hint.winfo_ismapped():
        #    form.lbl_hint.pack_forget()

    def play_video(form, capture, video_label, stop_flag, file_path):
        """動画を再生する関数"""
        while capture.isOpened() and not stop_flag.is_set():
            ret, frame = capture.read()
            if not ret:
                break
            form.video_info[file_path]['last_frame'] = frame  # 最後のフレームを保存

            #動画のサイズを調整
            label_width = max(50, min(80, video_label.winfo_width()))
            label_height = max(50, video_label.winfo_height())
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_height / frame_width

            # ラベルの幅を基準にアスペクト比を維持して高さを計算
            new_width = max(50, min(800, int(video_label.winfo_width())))
            new_height = int(new_width * aspect_ratio)

            # ラベルの高さを超えないように調整（必要なら）
            if new_height > label_height:
                new_height = label_height
                new_width = int(new_height / aspect_ratio)

            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)
            video_label.after(1, lambda: form.update_label_image(video_label, img_tk))

            delay_ms = int(1000 / capture.get(cv2.CAP_PROP_FPS))
            
            cv2.waitKey(delay_ms)

        capture.release()
        cv2.destroyAllWindows()

    def get_video_time_info(form, file_path):
        """指定された動画の再生時間情報を返す"""
        if file_path not in form.video_info:
            return "00:00/00:00"

        capture = form.video_info[file_path]['capture']
        
        # 総フレーム数とFPSを取得
        frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = capture.get(cv2.CAP_PROP_FPS)

        if fps == 0:
            return "00:00/00:00"

        # 総再生時間（秒）を計算
        total_time = frames / fps
        
        total_minutes = int(total_time // 60)
        total_seconds = int(total_time % 60)
        
        return f"00:00/{total_minutes:02d}:{total_seconds:02d}"
    
    def change_control_mode(form, state):
        """動画再生コントロールの有効/無効を切り替える関数"""
        form.footer.btn_rewind.config(state=state)
        form.footer.btn_play_pause.config(state=state)
        form.footer.btn_skip.config(state=state)
        form.lbl_timestamp.config(state=state)
        form.lbl_timestamp.config(text="00:00/00:00")
        
    def change_widget_mode(form,state):
        form.header.lbl_video_name.config(text="選択動画： なし")
        form.header.lbl_video_name.config(state=state)
        form.header.btn_size_minus.config(state=state)
        form.header.btn_size_plus.config(state=state)


    def update_label_image(form, video_label, img_tk):
        """ラベルの画像を更新する関数"""
        video_label.config(image=img_tk)
        video_label.image = img_tk

    def change_size(form, s):
        """動画表示の列数を変更する関数"""
        # 列数の範囲を制限
        s = max(1, min(5, s))
        form.set_size = s

        # 新しい幅を計算
        if s==1:
            new_width = WINDOW_MAX_SIZE // form.set_size - 40  # パディングを考慮
        else:
            new_width = WINDOW_MAX_SIZE // form.set_size - 5  # パディングを考慮
        new_height = int(new_width * 9 / 16)  # 16:9の比率

        # すべての動画ラベルのサイズを変更
        for idx, info in enumerate(form.video_info.values()):
            label = info['label']
            label.config(width=new_width, height=new_height)
            col = idx % form.set_size
            row = idx // form.set_size
            label.grid(row=row, column=col, padx=5, pady=5)
            last_frame = info.get('last_frame')
            if last_frame is not None:
                frame_height, frame_width = last_frame.shape[:2]
                aspect_ratio = frame_height / frame_width
                disp_height = int(new_width * aspect_ratio)
                resized_frame = cv2.resize(last_frame, (new_width, disp_height))
                frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(img)
                form.update_label_image(label, img_tk)
        
        # 画面表示サイズが最大または最小のとき、それぞれのボタンを無効化
        if s>=5:
            form.header.btn_size_minus.config(state=tk.DISABLED)
            form.header.btn_size_plus.config(state=tk.NORMAL)
        elif s<=1:
            form.header.btn_size_minus.config(state=tk.NORMAL)
            form.header.btn_size_plus.config(state=tk.DISABLED)
        else:
            form.header.btn_size_minus.config(state=tk.NORMAL)
            form.header.btn_size_plus.config(state=tk.NORMAL)

        
        form.scrollbar_set(0.0) # 最大サイズから画面サイズを小さくした際、画面外に置いて行かれないようにするため
        form.update_idletasks()

    def scrollbar_set(form, point):
        # 任意の位置までスクロールバーを移動
        form.canvas.yview_moveto(point)

    def get_video_index(form):
        """現在選択されている単一の動画のリスト内のインデックス（0から始まる）を返す"""
        
        if len(form.selected_label) != 1:
            return -1 
        
        selected_file_path=form.get_file_path()

        if selected_file_path:
            video_paths = list(form.video_info.keys())
            return video_paths.index(selected_file_path)
        
        return -1 # 見つからなかった場合
    
    def get_video_num(form):
        return len(form.video_info)
    
    def get_file_path(form):
        selected_label = list(form.selected_label.keys())[0]
        file_path = ""
        for path, info in form.video_info.items():
            if info['label'] == selected_label:
                file_path = path
                break
        return file_path
    
if __name__ == '__main__':
    app = main()
    app.mainloop()