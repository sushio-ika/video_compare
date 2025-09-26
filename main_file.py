import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage,ttk
import cv2
from PIL import Image, ImageTk
import threading
import os
from tkinterdnd2 import TkinterDnD
import time

from menu_file import (delete_video)
from click_file import (left_click, right_clickmenu, on_mousewheel)
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
        form.title("マルチリンク")
        form.geometry(f"{WINDOW_MAX_SIZE}x{WINDOW_MIN_SIZE}")
        form.tk_setPalette(background="#2E2E2E", foreground="#FFFFFF")
        form.resizable(True, True)
        form.minsize(WINDOW_MAX_SIZE, WINDOW_MIN_SIZE)

        # ドラッグ＆ドロップの設定
        form.drop_target_register(1, 'DND_Files')
        form.dnd_bind('<<Drop>>', form.on_drop_files)

        create_widgets(form)

        form.bind("<Button-3>", lambda event: right_clickmenu(form, event))
        form.bind("<Button-1>", lambda event: left_click(form, event, False))
        form.bind("<Control-Button-1>", lambda event: left_click(form, event, True))
        form.bind("<MouseWheel>", lambda event: on_mousewheel(form, event))

        form.update_widget(tk.DISABLED)
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
            create_widgets.btn_play_pause.config(text="▶")
        else:
            create_widgets.btn_play_pause.config(text="⏸")
            form.update()

    def update(form):
        if not form.paused:
            start_time = time.time()
            ret, frame = form.vid.read()
            if ret:
                form.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                form.canvas.config(width=form.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=form.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
                form.canvas.create_image(0, 0, image=form.photo, anchor=tk.NW)

                current_frame = int(form.vid.get(cv2.CAP_PROP_POS_FRAMES))
                total_frames = int(form.vid.get(cv2.CAP_PROP_FRAME_COUNT))
                create_widgets.progress_bar["value"] = (current_frame / total_frames) * 100

                current_time = int(form.vid.get(cv2.CAP_PROP_POS_MSEC) / 1000)
                total_time = int(total_frames / form.vid.get(cv2.CAP_PROP_FPS))

                current_time_str = form.format_time(current_time)
                total_time_str = form.format_time(total_time)
                create_widgets.lbl_timestamp.config(text=f"{current_time_str}/{total_time_str}")
                
                fps = form.vid.get(cv2.CAP_PROP_FPS)
                delay = int(1000 / fps)
                elapsed = int((time.time() - start_time) * 1000)
                delay = max(1, delay - elapsed)
                form.window.after(delay, form.update)
            else:
                form.toggle_play()
        else:
            create_widgets.btn_play_pause.config(text="▶")

    def format_time(form, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
        
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

    def update_widget(form, state):
        """動画再生コントロールの有効/無効を切り替える関数"""
        form.footer.btn_rewind.config(state=state)
        form.footer.btn_play_pause.config(state=state)
        form.footer.btn_skip.config(state=state)
        form.lbl_timestamp.config(state=state)
        form.footer.btn_delete.config(state=state)

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
        new_width = WINDOW_MAX_SIZE // form.set_size - 10  # パディングを考慮
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



if __name__ == '__main__':
    app = main()
    app.mainloop()