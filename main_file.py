import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage,ttk
import cv2
from PIL import Image, ImageTk
import threading
import os
from tkinterdnd2 import TkinterDnD

from menu_file import (delete_video)
from click_file import (left_click, right_clickmenu)

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
        form.selected_label = None  #現在選択中の動画ラベル
        form.video_info = {}      # 動画の情報を管理する辞書

        form.set_size = 3 #動画をいくつ横に並べるか

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

        


        form.create_widgets()

        form.bind("<Button-3>", lambda event: right_clickmenu(form, event))
        form.bind("<Button-1>", lambda event: left_click(form, event, False))
        form.bind("<Control-Button-1>", lambda event: left_click(form, event, True))

        form.update_widget(tk.DISABLED)
        form.change_size(form.set_size)

        #ウィンドウを中央に配置
        form.update_idletasks()

        x = (form.winfo_screenwidth() // 2) - (form.winfo_width() // 2)   #(画面の幅 // 2) - (ウィンドウの幅 // 2)
        y = (form.winfo_screenheight() // 2) - (form.winfo_height() // 2) #(画面の高さ // 2) - (ウィンドウの高さ // 2)

        form.geometry(f"+{x}+{y}")

    def create_widgets(form):
        """UI部品の配置""" 
        # ヘッダーを作成
        form.header = tk.Frame(form)
        form.header.pack(side=tk.TOP, fill=tk.X)
        form.header.config(bg="#2E2E2E")
        form.header.pack_propagate(False)
        form.header.config(height=50)
        form.header.pack(pady=5)

        # 画面サイズを変更するボタン
        form.header.btn_size_minus = tk.Button(form.header, text="－", width=3, command=lambda: form.change_size(form.set_size + 1))
        form.header.btn_size_minus.pack(side=tk.RIGHT, padx=5, pady=5)
        form.header.btn_size_minus.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)
        
        form.header.btn_size_plus = tk.Button(form.header, text="＋", width=3, command=lambda: form.change_size(form.set_size - 1))
        form.header.btn_size_plus.pack(side=tk.RIGHT, padx=5, pady=5)
        form.header.btn_size_plus.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)

        # 画面中央にドラッグアンドドロップのヒントを表示
        form.lbl_hint = tk.Label(form, text="ここに動画ファイルをドラッグ＆ドロップしてください", bg="#2E2E2E", fg="#AAAAAA")
        form.lbl_hint.pack(pady=20)

        # 動画再生コントロールを設置するフッターを作成
        form.footer = tk.Frame(form)
        form.footer.pack(side=tk.BOTTOM, fill=tk.X)
        form.footer.config(bg="#2E2E2E")
        form.footer.pack_propagate(False)
        form.footer.config(height=100)
        form.footer.pack(pady=5)

        # 巻き戻し
        form.footer.btn_rewind = tk.Button(form.footer, text="<< 5s", width=10, command=form.back)
        form.footer.btn_rewind.pack(side=tk.LEFT, padx=5, pady=5)

        # 再生/一時停止
        form.footer.btn_play_pause = tk.Button(form.footer, text="▶", width=10, command=form.toggle_play)
        form.footer.btn_play_pause.pack(side=tk.LEFT, padx=5, pady=5)

        # 早送り
        form.footer.btn_skip = tk.Button(form.footer, text="5s >>", width=10, command=form.front)
        form.footer.btn_skip.pack(side=tk.LEFT, padx=5, pady=5)

        # 進捗バーとタイムスタンプ
        form.progress_bar = ttk.Progressbar(form.footer, orient="horizontal", length=200, mode="determinate")
        form.progress_bar.pack(side=tk.LEFT, padx=5, pady=5)

        form.lbl_timestamp = tk.Label(form.footer, text="00:00/00:00")
        form.lbl_timestamp.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 追加・削除ボタン
        form.footer.mini_select_button = tk.Button(form.footer, text="追加", width=10, command=form.select_video)
        form.footer.mini_select_button.pack(side=tk.RIGHT, padx=5, pady=5)
        form.footer.mini_select_button.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)

        form.footer.btn_delete = tk.Button(form.footer, text="削除", width=10, command=lambda: delete_video(form, widget=form.selected_label))
        form.footer.btn_delete.pack(side=tk.RIGHT, padx=5, pady=5)
        form.footer.btn_delete.config(bg="#D9534F", fg="#FFFFFF", activebackground="#C9302C", activeforeground="#FFFFFF", bd=0)
        
        #動画表示用のフレーム
        form.video_frame = tk.Frame(form)
        form.video_frame.pack(fill=tk.BOTH, expand=True)

    def back(form):
        """5秒巻き戻す"""

    def front(form):
        """5秒早送りする"""

    def toggle_play(form):
        """動画の再生/一時停止を切り替える"""
        if form.thread and form.thread.is_alive():
            form.stop_flag.set()
            form.footer.btn_play_pause.config(text="▶")
        else:
            if form.selected_label is None:
                messagebox.showwarning("警告", "再生する動画が選択されていません。")
                return
            for file_path, info in form.video_info.items():
                if info['label'] == form.selected_label:
                    capture = info['capture']
                    video_label = info['label']
                    stop_flag = threading.Event()
                    form.stop_flag = stop_flag
                    thread = threading.Thread(target=form.play_video, args=(capture, video_label, stop_flag, file_path))
                    form.thread = thread
                    info['thread'] = thread
                    info['stop_flag'] = stop_flag
                    thread.start()
                    form.footer.btn_play_pause.config(text="⏸")
                    break

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
        if file_path in [info['capture'] for info in form.video_info.values()]:
            messagebox.showinfo("情報", "この動画はすでに追加されています。")
            return
        
        capture = cv2.VideoCapture(file_path)
        if not capture.isOpened():
            messagebox.showerror("エラー", f"動画ファイルを開けませんでした: {file_path}")
            return
            
        #動画表示用のラベルを作成
        video_label = tk.Label(form.video_frame, width=PICTURE_WIDTH, height=int(PICTURE_WIDTH * 9 / 16))
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
            new_width = PICTURE_WIDTH
            new_height = int(new_width * aspect_ratio)
            resized_frame = cv2.resize(frame, (new_width, new_height))
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)
            form.update_label_image(video_label, img_tk)

        # ヒントラベルを非表示にする
        if form.lbl_hint.winfo_ismapped():
            form.lbl_hint.pack_forget()

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