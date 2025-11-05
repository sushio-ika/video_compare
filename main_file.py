import threading
import os
import subprocess
import shutil
import time

import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD

from click_file import (click_Left, right_clickmenu, scroll_MouseWheel, click_DoubleLeft)
from create_item_file import (create_widgets)
from menu_file import (copy_Video, paste_Video, cut_Video, delete_Video,show_SelectSave,open_File,create_NewFile)
from log_file import(add_log, init_log)
from genre_file import(check_Genre,popup_select_genre)

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
        # グローバル変数の初期化
        form.selected_videos = {}  # 選択中の動画ラベルを管理する辞書
        form.all_videos = {}       # 動画の情報を管理する辞書
        form.col_size = 3          # デフォルトの動画表示の列数(1<=x<=5)
        form.video_state = True    # 動画の再生/一時停止状態
        form.timeorframe = True    # 再生時間表示を秒かフレームかを切り替える変数
        form.undo_list = None      # undo操作をするために使用するリスト
        form.current_file = None  #現在開いているファイルのパス

        # ジャンルを選択するメニュー
        form.var_walk = tk.BooleanVar(form)
        form.var_run = tk.BooleanVar(form)
        form.var_up = tk.BooleanVar(form)
        form.var_throw = tk.BooleanVar(form)
        form.var_face = tk.BooleanVar(form)
        form.var_action = tk.BooleanVar(form)

        form.genre_list = ["歩き","走り","持ち上げる","投げる","表情","アクション"]
        form.genre_checkedList = [0] * len(form.genre_list)  # 選択されているジャンルの有無を保存するリスト（0:未選択, 1:選択中）

        # ウィンドウの基本設定
        form.title("新規ファイル")
        form.geometry(f"{WINDOW_WIDTH_SIZE}x{WINDOW_HEIGHT_SIZE}")
        form.tk_setPalette(background="#2E2E2E", foreground="#FFFFFF")
        form.resizable(False, False)

        # ドラッグ＆ドロップの設定
        form.drop_target_register(1, 'DND_Files')
        form.dnd_bind('<<Drop>>', form.drop_File)

        create_widgets(form)

        form.bind("<Button-3>", lambda event: right_clickmenu(form, event))
        form.bind("<Button-1>", lambda event: click_Left(form, event, False))
        form.bind("<Control-Button-1>", lambda event: click_Left(form, event, True))
        form.bind("<MouseWheel>", lambda event: scroll_MouseWheel(form, event))
        form.bind("<Double-Button-1>",lambda event: click_DoubleLeft(form,event))

        # ショートカットキー
        form.bind(",", lambda event: form.rewind_Flame()) #<
        form.bind(".", lambda event: form.forward_Flame()) #>
        form.bind("k", lambda event: form.change_PlayPause()) #再生/一時停止
        form.bind("j", lambda event: form.rewind_Video()) #5秒巻き戻し
        form.bind("l", lambda event: form.forward_Video()) #5秒早送り
        form.bind("<Control-t>", lambda event: form.select_Video()) #動画追加
        form.bind("<Control-g>", lambda event: popup_select_genre(form)) #ジャンル設定
        form.bind("<Control-a>", lambda event: form.select_AllVideo()) #全選択
        form.bind("<Control-c>", lambda event: copy_Video(form)) #コピー
        form.bind("<Control-x>", lambda event: cut_Video(form)) #カット
        form.bind("<Control-v>", lambda event: paste_Video(form)) #ペースト
        form.bind("<Control-s>", lambda event: show_SelectSave(form,overwrite=True)) #ファイルを保存
        form.bind("<Control-o>", lambda event: open_File(form)) #ファイルを開く
        form.bind("<Control-n>", lambda event: create_NewFile(form)) #ファイルを新規作成
        form.bind("<Delete>", lambda event: delete_Video(form)) #削除

        form.change_VideoSize(form.col_size)
        form.change_VideoState(tk.DISABLED)
        form.change_ExistvideoState(tk.DISABLED)
        
        init_log()

        #ウィンドウを中央に配置
        form.update_idletasks()

        x = (form.winfo_screenwidth() // 2) - (form.winfo_width() // 2)   #(画面の幅 // 2) - (ウィンドウの幅 // 2)
        y = (form.winfo_screenheight() // 2) - (form.winfo_height() // 2) #(画面の高さ // 2) - (ウィンドウの高さ // 2)

        form.geometry(f"+{x}+{y}")

    def close_App(form):
        form.destroy()

    def rewind_Video(form):
        """5秒巻き戻す"""
        # 念のため
        if len(form.selected_videos) != 1:
            messagebox.showinfo("情報", "単一の動画を選択してください。")
            return

        # 選択中の動画から、ファイルパスを取得
        file_path = form.get_Filepath()
        if not file_path:
            return

        info = form.all_videos[file_path]
        capture = info['capture']
        video_label = info['label']

        # 5秒巻き戻し
        frames = int(capture.get(cv2.CAP_PROP_FPS) * -5)
        form.control_Video(capture, video_label, file_path, frames)
    
    def rewind_Flame(form):
        """1フレーム巻き戻す"""
        # 念のため
        if len(form.selected_videos) != 1:
            messagebox.showinfo("情報", "単一の動画を選択してください。")
            return

        # 選択中の動画から、ファイルパスを取得
        file_path = form.get_Filepath()
        if not file_path:
            return

        info = form.all_videos[file_path]
        capture = info['capture']
        video_label = info['label']

        # 1フレーム巻き戻し
        form.control_Video(capture, video_label, file_path, -1)

    def forward_Flame(form):
        """1フレーム早送りする"""
        # 念のため
        if len(form.selected_videos) != 1:
            messagebox.showinfo("情報", "単一の動画を選択してください。")
            return

        # 選択中の動画から、ファイルパスを取得
        file_path = form.get_Filepath()
        if not file_path:
            return

        info = form.all_videos[file_path]
        capture = info['capture']
        video_label = info['label']

        # 1フレーム早送り
        form.control_Video(capture, video_label, file_path, 1)

    def forward_Video(form):
        """5秒早送りする"""
        # 念のため
        if len(form.selected_videos) != 1:
            messagebox.showinfo("情報", "単一の動画を選択してください。")
            return

        # 選択中の動画から、ファイルパスを取得
        file_path = form.get_Filepath()
        if not file_path:
            return

        info = form.all_videos[file_path]
        capture = info['capture']
        video_label = info['label']

        # 5秒早送り
        frames = int(capture.get(cv2.CAP_PROP_FPS) * 5)
        form.control_Video(capture, video_label, file_path, frames)

    def control_Video(form, capture, video_label, file_path, frames):
        """動画を指定されたフレーム分移動する関数"""
        # 再生中なら一時停止
        if not form.video_state:
            form.change_PlayPause()
            time.sleep(0.1)
            form.video_state = True
            form.footer.btn_playPause.config(text="▶")

        # 現在のフレーム位置を取得し、指定されたフレーム数だけ移動
        current_frame = int(capture.get(cv2.CAP_PROP_POS_FRAMES))
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        new_frame = current_frame + frames

        ret, frame = capture.read()
        new_frame = max(0, min(new_frame, total_frames - 1))  # 範囲内に制限
        
        capture.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

        if ret:
            form.all_videos[file_path]['last_frame'] = frame  # 最後に表示したフレームを保存

            # 画面サイズに合わせてリサイズして表示
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_height / frame_width

            new_width = WINDOW_WIDTH_SIZE // form.col_size - 10  # パディングを考慮
            new_height = int(new_width * aspect_ratio)
            
            resized_frame = cv2.resize(frame, (new_width, new_height))
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)

            del frame

            video_label.after(0, lambda: form.update_Image(video_label, img_tk))
            form.after(0, lambda: form.update_Timestamp(file_path))

    def change_PlayPause(form):
        """動画の再生/一時停止を切り替える"""
        # 念のため
        if len(form.selected_videos) != 1:
            messagebox.showinfo("情報", "単一の動画を選択してください。")
            return
        
        # 選択中の動画から、ファイルパスを取得
        file_path = form.get_Filepath()
        if not file_path:
            return
        
        info = form.all_videos[file_path]
        capture = info['capture']
        video_label = info['label']
        stop_flag = info['stop_flag']

        if form.video_state:
            # 再生中でない場合、再生を開始
            form.video_state = False
            form.footer.btn_playPause.config(text="■")
            if info['thread'] is None or not info['thread'].is_alive():
                stop_flag.clear()
                thread = threading.Thread(target=form.play_Video, args=(capture, video_label, stop_flag, file_path))
                thread.start()
                info['thread'] = thread
        else:
            # 再生中の場合、一時停止
            form.video_state = True
            form.footer.btn_playPause.config(text="▶")
            form.stop_Video()

    def drop_File(form, event):
        """ドロップされたファイルを処理する関数"""
        file_paths = form.tk.splitlist(event.data)
        for file_path in file_paths:
            if file_path.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                form.add_Video(file_path)
                # ジャンルチェックと再配置
                form.relocate_Video()
                check_Genre(form)


    def select_Video(form):
        """ファイルダイアログから動画を選択する関数"""
        file_paths = filedialog.askopenfilename(
            title="動画を選択してください",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")],
            multiple=True
        )
        for file_path in file_paths:
            if file_path.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                form.add_Video(file_path)
                
                # ジャンルチェックと再配置
                form.relocate_Video()
                check_Genre(form)



    
    def add_Video(form, file_path):
        """動画をアプリに追加し、再生を準備する関数"""
        # すでに追加されている場合は無視
        if file_path in form.all_videos:
            messagebox.showinfo("情報", "この動画はすでに追加されています。")
            return
        
        try:
            capture = cv2.VideoCapture(file_path)
            if not capture.isOpened():
                messagebox.showerror("エラー", f"動画ファイルを開けませんでした: {file_path}")
                return
        except Exception as e:
            messagebox.showerror("エラー",f"動画ファイルに問題があります:{e}")
            return

        #動画表示用のラベルを作成
        video_label = tk.Label(form.frm_setVideo, width=WINDOW_WIDTH_SIZE // form.col_size - 10, height=int((WINDOW_WIDTH_SIZE // form.col_size - 10) * 9 / 16))
        # 追加前にall_videosへ一時追加
        temp_count = len(form.all_videos)  # 追加前の数
        col = temp_count % form.col_size
        row = temp_count // form.col_size
        video_label.grid(row=row, column=col, padx=5, pady=5)


        #再生用のスレッドを開始
        stop_flag = threading.Event()
        thread = None  # ← 再生スレッドは起動しない

        form.all_videos[file_path] = {
            'videoID': len(form.all_videos),
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
            form.all_videos[file_path]['last_frame'] = frame
            new_width = WINDOW_WIDTH_SIZE // form.col_size - 10  # パディングを考慮
            img_tk=form.get_Image(frame,new_width)
            form.update_Image(video_label, img_tk)
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

        form.change_ExistvideoState(tk.NORMAL)

        # 選択状態にしてラベルに表示
        form.set_VideoHighlight(video_label)
        form.selected_videos[video_label]=True
        form.lbl_timestamp.config(text="00:00/00:00")
        form.set_NameLabel()
        
    def set_NameLabel(form):
        # 一つ選択されていたら動画再生コントロールを有効にしてラベルに動画名を表示
        if len(form.selected_videos)==1:
            form.change_VideoState(tk.NORMAL)
            file_path=form.get_Filepath()

            # ファイル名のみを抽出して表示
            file_name = os.path.basename(file_path)

            # ジャンルが設定されていれば表示
            get_genre = form.all_videos.get(file_path, {}).get('genre')
            if get_genre:
                form.header.lbl_videoName.config(text=f"選択動画： [{get_genre}] {file_name}")
            else:
                form.header.lbl_videoName.config(text=f"選択動画： {file_name}")

            # 動画再生処理の準備
            info = form.all_videos[file_path]
            capture = info['capture']
            capture.set(cv2.CAP_PROP_POS_FRAMES, capture.get(cv2.CAP_PROP_POS_FRAMES))
            form.stop_Video()
        else:
            form.change_VideoState(tk.DISABLED)
            if len(form.selected_videos)>1:
                form.header.lbl_videoName.config(text="選択動画： *")
            else:
                form.header.lbl_videoName.config(text="選択動画： なし")

            form.lbl_timestamp.config(text="00:00/00:00")
            form.stop_Video()


    def relocate_Video(form):
        """動画表示エリアの動画を再配置する関数(並び替え時使用)"""
        # videoID でソート
        sorted_videos = sorted(
            form.all_videos.items(),
            key=lambda x: x[1]['videoID']
        )
        
        # ソートされた順番で再配置
        for idx, (file_path, info) in enumerate(sorted_videos):
            label = info['label']
            col = idx % form.col_size
            row = idx // form.col_size
            label.grid(row=row, column=col, padx=5, pady=5)

    def play_Video(form, capture, video_label, stop_flag, file_path):
        """動画を再生する関数"""
        while not stop_flag.is_set():
            # 一時停止状態なら終了
            if form.video_state:
                break
            
            ret, frame = capture.read()

            # 動画の終端に達した場合、最初のフレームに戻す
            if not ret:
                capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                form.change_PlayPause()  # ←ループ再生する場合は削除
                continue

            form.all_videos[file_path]['last_frame'] = frame  # 最後に表示したフレームを保存

            # 画面サイズに合わせてリサイズして表示
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_height / frame_width

            new_width = WINDOW_WIDTH_SIZE // form.col_size - 10  # パディングを考慮
            new_height = int(new_width * aspect_ratio)
            
            resized_frame = cv2.resize(frame, (new_width, new_height))
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)

            del frame

            video_label.after(0, lambda: form.update_Image(video_label, img_tk))
            form.after(0, lambda: form.update_Timestamp(file_path))

            fps = capture.get(cv2.CAP_PROP_FPS)
            if fps > 0:
                delay = 1.0 / fps
                time.sleep(delay)
            else:
                time.sleep(1/30)

        # スレッドが終了したら、スレッド情報をクリア
        if file_path in form.all_videos:
            form.all_videos[file_path]['thread'] = None
        
    def stop_Video(form):
        """動画の再生を停止する関数"""
        # 念のため
        if len(form.selected_videos) != 1:
            return
        
        # 選択中の動画から、ファイルパスを取得
        file_path = form.get_Filepath()
        if not file_path:
            return
        
        info = form.all_videos[file_path]

        stop_flag = info['stop_flag']
        if stop_flag:
            stop_flag.set()
            
        info['thread'] = None
        form.video_state = True
        form.footer.btn_playPause.config(text="▶")
        form.update_Timestamp(file_path)

    def change_TimeFrame(form):
        """タイム表示/フレーム表示を切り替え、選択動画の表示を更新する"""
        form.timeorframe = not form.timeorframe
        # 選択が単一のときはその動画のタイムスタンプを更新
        if len(form.selected_videos) == 1:
            file_path = form.get_Filepath()
            if file_path:
                form.update_Timestamp(file_path)
        else:
            # 選択が無いか複数選択のときはヘッダのタイム表示をリセット
            form.lbl_timestamp.config(text="00:00/00:00")

    def update_Timestamp(form, file_path):
        """選択中の動画のタイムスタンプを更新する関数"""
        if file_path not in form.all_videos:
            form.lbl_timestamp.config(text="00:00/00:00")
            form.prgbar_videoTime['value']=0
            return

        capture = form.all_videos[file_path]['capture']
        
        # 現在のフレーム位置と総フレーム数、FPSを取得
        current_frame = int(capture.get(cv2.CAP_PROP_POS_FRAMES))
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        form.prgbar_videoTime['maximum'] = total_frames

        # フレーム位置が範囲外にならないように制限
        current_frame = max(0, min(current_frame, total_frames))
        form.prgbar_videoTime['value'] = current_frame


        if form.timeorframe:
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
        else:
            form.lbl_timestamp.config(text=f"{current_frame}/{total_frames}")

        


    def get_VideoTime(form, file_path):
        """指定された動画の再生時間情報を返す"""
        if form.timeorframe:
            # 動画が存在しない場合
            if file_path not in form.all_videos:
                return "00:00/00:00"

            capture = form.all_videos[file_path]['capture']
        
            # 総フレーム数とFPSを取得
            total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = capture.get(cv2.CAP_PROP_FPS)

            if fps == 0:
                return "00:00/00:00"

            # 総再生時間（秒）を計算
            total_time = total_frames / fps
        
            total_minutes = int(total_time // 60)
            total_seconds = int(total_time % 60)
        
            return f"00:00/{total_minutes:02d}:{total_seconds:02d}"
        else:
            # 動画が存在しない場合
            if file_path not in form.all_videos:
                return "0/0"

            capture = form.all_videos[file_path]['capture']
        
            # 総フレーム数とFPSを取得
            total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
                
            return f"0/{total_frames}"


    def change_VideoState(form, vstate):
        """動画再生コントロールの有効/無効を切り替える関数"""
        form.footer.btn_rewind.config(state=vstate)
        form.footer.btn_frameBack.config(state=vstate)
        form.footer.btn_playPause.config(state=vstate)
        form.footer.btn_frameForward.config(state=vstate)
        form.footer.btn_skip.config(state=vstate)
        form.lbl_timestamp.config(state=vstate)

    def change_ExistvideoState(form,vstate):
        """動画が存在しない場合の動画ウィジェットの有効/無効を切り替える関数"""
        form.header.lbl_videoName.config(text="選択動画： なし")
        form.header.lbl_videoName.config(state=vstate)
        form.header.btn_sizeMinus.config(state=vstate)
        form.header.btn_sizePlus.config(state=vstate)
        form.header.btn_genre.config(state=vstate)
        form.header.btn_sort.config(state=vstate)

    def update_Image(form, video_label, img_tk):
        """ラベルの画像を更新する関数"""
        video_label.config(image=img_tk)
        video_label.image = img_tk

    def get_Image(form, frame, width):
        frame_height, frame_width = frame.shape[:2]
        aspect_ratio = frame_height / frame_width
        new_height = int(width * aspect_ratio)
        resized_frame = cv2.resize(frame, (width, new_height))
        frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(img)

        return img_tk
        
    def change_VideoSize(form, s):
        """動画表示の列数を変更する関数"""
        # 列数の範囲を制限
        s = max(1, min(5, s))
        form.col_size = s

        try:
            # 新しい幅を計算
            if s==1:
                new_width = WINDOW_WIDTH_SIZE // form.col_size - 40  # パディングを考慮
            else:
                new_width = WINDOW_WIDTH_SIZE // form.col_size - 5  # パディングを考慮
            new_height = int(new_width * 9 / 16)  # 16:9の比率

            # すべての動画ラベルのサイズを変更
            for idx, info in enumerate(form.all_videos.values()):
                label = info['label']
                label.config(width=new_width, height=new_height)
                last_frame = info.get('last_frame')

                if last_frame is not None:                
                    img_tk = form.get_Image(last_frame,new_width)
                    form.update_Image(label, img_tk)

            # ジャンル設定を反映
            check_Genre(form)
        except Exception as e:
            messagebox.showerror("エラー",f"動画サイズ変更処理でエラーが発生しました:{e}")
        
        # 画面表示サイズが最大または最小のとき、それぞれのボタンを無効化
        if s>=5:
            form.header.btn_sizeMinus.config(state=tk.DISABLED)
            form.header.btn_sizePlus.config(state=tk.NORMAL)
        elif s<=1:
            form.header.btn_sizeMinus.config(state=tk.NORMAL)
            form.header.btn_sizePlus.config(state=tk.DISABLED)
        else:
            form.header.btn_sizeMinus.config(state=tk.NORMAL)
            form.header.btn_sizePlus.config(state=tk.NORMAL)


    def move_Scrollbar(form, point):
        # 任意の位置までスクロールバーを移動
        form.mainForm.yview_moveto(point)

    def get_Videoid(form):
        """現在選択されている単一の動画のリスト内のvideoID（0から始まる）を返す"""
        
        if len(form.selected_videos) != 1:
            return -1

        file_path = form.get_Filepath()

        if file_path in form.all_videos:
            return form.all_videos[file_path]['videoID']
        
        return -1 # 見つからなかった場合
    
    def get_VideoNum(form):
        return len(form.all_videos)
    
    def get_Filepath(form):
        """選択されている動画のファイルパスを取得する"""
        selected_videos = list(form.selected_videos.keys())[0]
        for path, info in form.all_videos.items():
            if info['label'] == selected_videos:
                return path
        
    def get_ClipPath(form):
        """選択されている複数動画のファイルパスリストを取得する"""
        selected_videos = list(form.selected_videos.keys())
        path_list=[]

        for i,sel_video in enumerate(selected_videos):
            for path, info in form.all_videos.items():
                if info['label'] == sel_video:
                    path_list.append(path)
                    break
        return path_list
            
    def copy_VideoName(form):
        if len(form.selected_videos)==1:
            form.change_VideoState(tk.NORMAL)
            file_path=form.get_Filepath()

            file_name = os.path.basename(file_path)

            try:
                form.clipboard_clear()
                form.clipboard_append(file_name)
        
                print(f"クリップボードにコピーされました: {file_name}")
        
            except tk.TclError as e:
                print(f"クリップボードへのアクセスエラー: {e}")

    def change_video_order(form):
        if len(form.selected_videos) != 2:
            messagebox.showinfo("情報", "2つの動画を選択してください。")
            return
        else:
            # 2つの動画の順序を入れ替え
            labels = list(form.selected_videos.keys())
            file_paths = []
            for label in labels:
                for path, info in form.all_videos.items():
                    if info['label'] == label:
                        file_paths.append(path)
            # videoIDを入れ替え
            id1 = form.all_videos[file_paths[0]]['videoID']
            id2 = form.all_videos[file_paths[1]]['videoID']
            form.all_videos[file_paths[0]]['videoID'] = id2
            form.all_videos[file_paths[1]]['videoID'] = id1

        # 動画を再配置
        form.relocate_Video()

    def play_MediaPlayer(form):
        """Windowsメディアプレーヤーで動画を再生する"""
        if len(form.selected_videos)!=1:
            messagebox.showinfo("情報","一つの動画を選択してください")
            return
        
        file_path=form.get_Filepath()
            
        if not os.path.exists(file_path):
            messagebox.showerror("エラー", f"ファイルが見つかりません: {file_path}")
            return

        form.stop_Video()
        
        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("エラー", f"再生に失敗しました: {e}")
    
    def select_AllVideo(form):
        """全ての動画を選択状態にする"""
        for info in form.all_videos.values():
            form.set_VideoHighlight(info["label"])
            form.selected_videos[info["label"]]=True
        form.lbl_timestamp.config(text="00:00/00:00")
        form.set_NameLabel()

    def clear_AllvideoHighlights(form):
        """全ての動画のハイライトをリセットする"""
        for info in form.all_videos.values():
            info['label'].config(bd=0, relief=tk.FLAT)
            info['label'].config(highlightbackground="#2C2C2C", highlightcolor="#2C2C2C", highlightthickness=0)

    def clear_AvideoHighlight(form, label):
        """特定の動画のハイライトをリセットする"""
        label.config(bd=0, relief=tk.FLAT)
        label.config(highlightbackground="#2C2C2C", highlightcolor="#2C2C2C", highlightthickness=0)

    def set_VideoHighlight(form, label):
        """選択された動画に枠線を適用する"""
        label.config(bd=2, relief=tk.RAISED, highlightbackground="#5FB7FF", highlightcolor="#5FB7FF", highlightthickness=2)

if __name__ == '__main__':
    app = main()
    app.mainloop()