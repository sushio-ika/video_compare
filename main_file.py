import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage,ttk
import cv2
from PIL import Image, ImageTk
import threading
import os
from tkinterdnd2 import TkinterDnD
import time

from click_file import (left_click, right_clickmenu, on_mousewheel,double_left_click)
from create_item_file import (create_widgets)
from menu_file import (copy_video, paste_video, cut_video, delete_video)

#定数
WINDOW_WIDTH_SIZE=1280
WINDOW_HEIGHT_SIZE=900
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
        form.copied_video = None # コピー/カットした動画の情報を保存する辞書

        form.set_size = 3 # デフォルトの動画の列数

            # ジャンルを選択するメニュー
        form.var_walk = tk.BooleanVar(form)
        form.var_run = tk.BooleanVar(form)
        form.var_up = tk.BooleanVar(form)
        form.var_throw = tk.BooleanVar(form)
        form.var_face = tk.BooleanVar(form)
        form.var_action = tk.BooleanVar(form)

        form.genre_list = ["歩き","走り","持ち上げる","投げる","表情","アクション"]
        form.check_genre_list = [] # 選択されているジャンルの有無を保存するリスト（0:未選択, 1:選択中）
        for _ in form.genre_list:
            form.check_genre_list.append(0)
        form.thread = None
        form.stop_flag = None
        form.paused = True  # 動画の再生/一時停止状態

        # ウィンドウの基本設定
        form.title("マルチリンク -新規ファイル-")
        form.geometry(f"{WINDOW_WIDTH_SIZE}x{WINDOW_HEIGHT_SIZE}")
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

        # ショートカットキー
        form.bind_all("-", lambda event: form.change_size(form.set_size + 1)) #-
        form.bind_all(";", lambda event: form.change_size(form.set_size - 1)) #+
        form.bind_all(",", lambda event: form.frame_back()) #<
        form.bind_all(".", lambda event: form.frame_forward()) #>
        form.bind_all("k", lambda event: form.toggle_play()) #再生/一時停止
        form.bind_all("j", lambda event: form.back()) #5秒巻き戻し
        form.bind_all("l", lambda event: form.forward()) #5秒早送り
        form.bind_all("<Control-c>", lambda event: copy_video(form)) #コピー
        form.bind_all("<Control-x>", lambda event: cut_video(form)) #カット
        form.bind_all("<Control-v>", lambda event: paste_video(form)) #ペースト
        form.bind_all("<BackSpace>", lambda event: delete_video(form)) #削除

        form.change_size(form.set_size)
        form.change_control_mode(tk.DISABLED)
        form.change_widget_mode(tk.DISABLED)

        #ウィンドウを中央に配置
        form.update_idletasks()

        x = (form.winfo_screenwidth() // 2) - (form.winfo_width() // 2)   #(画面の幅 // 2) - (ウィンドウの幅 // 2)
        y = (form.winfo_screenheight() // 2) - (form.winfo_height() // 2) #(画面の高さ // 2) - (ウィンドウの高さ // 2)

        form.geometry(f"+{x}+{y}")


    def back(form):
        """5秒巻き戻す"""
        # 念のため
        if len(form.selected_label) != 1:
            messagebox.showinfo("情報", "単一の動画を選択してください。")
            return

        # 選択中の動画から、ファイルパスを取得
        selected_file_path = form.get_file_path()
        if not selected_file_path:
            return

        info = form.video_info[selected_file_path]
        capture = info['capture']
        video_label = info['label']
        stop_flag = info['stop_flag']

        # 5秒巻き戻し
        frames_to_advance = int(capture.get(cv2.CAP_PROP_FPS) * -5)
        form.control_video(capture, video_label, stop_flag, selected_file_path, frames_to_advance)
    
    def frame_back(form):
        """1フレーム巻き戻す"""
        # 念のため
        if len(form.selected_label) != 1:
            messagebox.showinfo("情報", "単一の動画を選択してください。")
            return

        # 選択中の動画から、ファイルパスを取得
        selected_file_path = form.get_file_path()
        if not selected_file_path:
            return

        info = form.video_info[selected_file_path]
        capture = info['capture']
        video_label = info['label']
        stop_flag = info['stop_flag']

        # 1フレーム巻き戻し
        form.control_video(capture, video_label, stop_flag, selected_file_path, -1)

    def frame_forward(form):
        """1フレーム早送りする"""
        # 念のため
        if len(form.selected_label) != 1:
            messagebox.showinfo("情報", "単一の動画を選択してください。")
            return

        # 選択中の動画から、ファイルパスを取得
        selected_file_path = form.get_file_path()
        if not selected_file_path:
            return

        info = form.video_info[selected_file_path]
        capture = info['capture']
        video_label = info['label']
        stop_flag = info['stop_flag']

        # 1フレーム早送り
        form.control_video(capture, video_label, stop_flag, selected_file_path, 1)

    def forward(form):
        """5秒早送りする"""
        # 念のため
        if len(form.selected_label) != 1:
            messagebox.showinfo("情報", "単一の動画を選択してください。")
            return

        # 選択中の動画から、ファイルパスを取得
        selected_file_path = form.get_file_path()
        if not selected_file_path:
            return

        info = form.video_info[selected_file_path]
        capture = info['capture']
        video_label = info['label']
        stop_flag = info['stop_flag']

        # 5秒早送り
        frames_to_advance = int(capture.get(cv2.CAP_PROP_FPS) * 5)
        form.control_video(capture, video_label, stop_flag, selected_file_path, frames_to_advance)

    def control_video(form, capture, video_label, stop_flag, file_path, frames):
        """動画を指定されたフレーム分移動する関数"""
        # 再生中なら一時停止
        if not form.paused:
            form.toggle_play()
            time.sleep(0.1)
            form.paused = True
            form.footer.btn_play_pause.config(text="▶")

        # 現在のフレーム位置を取得し、指定されたフレーム数だけ移動
        current_frame = int(capture.get(cv2.CAP_PROP_POS_FRAMES))
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        new_frame = current_frame + frames

        ret, frame = capture.read()
        new_frame = max(0, min(new_frame, total_frames - 1))  # 範囲内に制限
        
        capture.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

        if ret:
            form.video_info[file_path]['last_frame'] = frame  # 最後に表示したフレームを保存

            # 画面サイズに合わせてリサイズして表示
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_height / frame_width

            new_width = WINDOW_WIDTH_SIZE // form.set_size - 10  # パディングを考慮
            new_height = int(new_width * aspect_ratio)
            
            resized_frame = cv2.resize(frame, (new_width, new_height))
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)

            del frame

            video_label.after(0, lambda: form.update_label_image(video_label, img_tk))
            form.after(0, lambda: form.update_lbl_timestamp(file_path))

    def toggle_play(form):
        """動画の再生/一時停止を切り替える"""
        # 念のため
        if len(form.selected_label) != 1:
            messagebox.showinfo("情報", "単一の動画を選択してください。")
            return
        
        # 選択中の動画から、ファイルパスを取得
        selected_file_path = form.get_file_path()
        if not selected_file_path:
            return
        
        info = form.video_info[selected_file_path]
        capture = info['capture']
        video_label = info['label']
        stop_flag = info['stop_flag']

        if form.paused:
            # 再生中でない場合、再生を開始
            form.paused = False
            form.footer.btn_play_pause.config(text="⏸")
            if info['thread'] is None or not info['thread'].is_alive():
                stop_flag.clear()
                thread = threading.Thread(target=form.play_video, args=(capture, video_label, stop_flag, selected_file_path))
                thread.start()
                info['thread'] = thread
        else:
            # 再生中の場合、一時停止
            form.paused = True
            form.footer.btn_play_pause.config(text="▶")
            form.stop_video()

    def update_lbl_timestamp(form, file_path):
        """選択中の動画のタイムスタンプを更新する関数"""
        if file_path not in form.video_info:
            form.lbl_timestamp.config(text="00:00/00:00")
            return

        capture = form.video_info[file_path]['capture']
        
        # 現在のフレーム位置と総フレーム数、FPSを取得
        current_frame = int(capture.get(cv2.CAP_PROP_POS_FRAMES))
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = capture.get(cv2.CAP_PROP_FPS)

        if fps == 0:
            form.lbl_timestamp.config(text="00:00/00:00")
            return

        # 現在の再生時間（秒）を計算
        current_time = current_frame / fps
        total_time = total_frames / fps
        
        current_minutes = int(current_time // 60)
        current_seconds = int(current_time % 60)
        total_minutes = int(total_time // 60)
        total_seconds = int(total_time % 60)
        
        form.lbl_timestamp.config(text=f"{current_minutes:02d}:{current_seconds:02d}/{total_minutes:02d}:{total_seconds:02d}")
        form.progress_bar['maximum'] = total_frames
        form.progress_bar['value'] = current_frame
        

    def on_drop_files(form, event):
        """ドロップされたファイルを処理する関数"""
        files = form.tk.splitlist(event.data)
        for file_path in files:
            if file_path.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                form.add_video(file_path)

    def select_video(form):
        """ファイルダイアログから動画を選択する関数"""
        filepaths = filedialog.askopenfilename(
            title="動画を選択してください",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")],
            multiple=True
        )
        for file_path in filepaths:
            if file_path.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                form.add_video(file_path)
    
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
        video_label = tk.Label(form.video_frame, width=WINDOW_WIDTH_SIZE // form.set_size - 10, height=int((WINDOW_WIDTH_SIZE // form.set_size - 10) * 9 / 16))
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
            'last_frame': None,
            'genre': None
        }

        # 最初のフレームだけ表示
        ret, frame = capture.read()
        if ret:
            form.video_info[file_path]['last_frame'] = frame
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_height / frame_width
            new_width = WINDOW_WIDTH_SIZE // form.set_size - 10  # パディングを考慮
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
        while not stop_flag.is_set():
            # 一時停止状態なら終了
            if form.paused:
                break
            
            ret, frame = capture.read()

            # 動画の終端に達した場合、最初のフレームに戻す
            if not ret:
                capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                form.toggle_play()  # ←ループ再生する場合は削除
                continue

            form.video_info[file_path]['last_frame'] = frame  # 最後に表示したフレームを保存

            # 画面サイズに合わせてリサイズして表示
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_height / frame_width

            new_width = WINDOW_WIDTH_SIZE // form.set_size - 10  # パディングを考慮
            new_height = int(new_width * aspect_ratio)
            
            resized_frame = cv2.resize(frame, (new_width, new_height))
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)

            del frame

            video_label.after(0, lambda: form.update_label_image(video_label, img_tk))
            form.after(0, lambda: form.update_lbl_timestamp(file_path))

            fps = capture.get(cv2.CAP_PROP_FPS)
            if fps > 0:
                delay = 1.0 / fps
                time.sleep(delay)
            else:
                time.sleep(1/30)

        # スレッドが終了したら、スレッド情報をクリア
        if file_path in form.video_info:
            form.video_info[file_path]['thread'] = None
        
    def stop_video(form):
        """動画の再生を停止する関数"""
        # 念のため
        if len(form.selected_label) != 1:
            return
        
        # 選択中の動画から、ファイルパスを取得
        selected_file_path = form.get_file_path()
        if not selected_file_path:
            return
        
        info = form.video_info[selected_file_path]

        stop_flag = info['stop_flag']
        if stop_flag:
            stop_flag.set()
            
        info['thread'] = None
        form.paused = True
        form.footer.btn_play_pause.config(text="▶")
        form.update_lbl_timestamp(selected_file_path)


    def get_video_time_info(form, file_path):
        """指定された動画の再生時間情報を返す"""
        # 動画が存在しない場合
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
        form.footer.btn_frame_back.config(state=state)
        form.footer.btn_play_pause.config(state=state)
        form.footer.btn_frame_forward.config(state=state)
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
            new_width = WINDOW_WIDTH_SIZE // form.set_size - 40  # パディングを考慮
        else:
            new_width = WINDOW_WIDTH_SIZE // form.set_size - 5  # パディングを考慮
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
                file_path += path
        return file_path
        

                        
if __name__ == '__main__':
    app = main()
    app.mainloop()