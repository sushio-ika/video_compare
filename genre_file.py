import tkinter as tk
from tkinter import messagebox, ttk
import os
from log_file import(add_log)

def show_GenreWindow(form):
    """ジャンル選択メニューを表示"""
    def set_genre(genre_index):
        # genre_indexに対応したチェックボックスが未選択なら0、選択中なら1をリストに保存
        if form.genre_checkedList[genre_index] == 0:
            form.genre_checkedList[genre_index] = 1
        else:
            form.genre_checkedList[genre_index] = 0
        check_Genre(form)

    def add_Genre():
        txt=form.genre_window.txtbox_addgenre.get(1.0,"end-1c")
        if txt==None:
            messagebox.showerror("エラー","新ジャンル名を入力してください")
            return
        
        form.genre_list.append(txt)
        form.genre_checkedList.append(0)
        show_GenreWindow(form)


    if hasattr(form, 'genre_window') and form.genre_window.winfo_exists():
        form.genre_window.lift()  # すでにウィンドウが存在する場合は前面に持ってくる
        return

    form.genre_window = tk.Toplevel(form)
    form.genre_window.configure(bg="#000000")
    form.genre_window.overrideredirect(True)
    form.genre_window.resizable(False,False)
    form.genre_window.focus_set()

    def on_focusout(event):
        if event.widget is form.genre_window:
            return
        form.genre_window.destroy()
        
    form.genre_window.bind("<FocusOut>", on_focusout)
        
    # メインウィンドウのレイアウト情報を確実に取得する
    form.update_idletasks()

    # ヘッダーの高さを取得（存在しない場合は0）
    header_h = form.header.winfo_height()

    # ログウィンドウの幅と高さを計算
    log_w = 400
    log_h = 400

    # 画面上の配置位置を計算（ヘッダーの下、左端）
    pos_x = form.winfo_rootx()
    pos_y = form.winfo_rooty() + header_h

    # 画面外にはみ出さないように調整（必要なら）
    screen_h = form.winfo_screenheight()
    if pos_y + log_h > screen_h:
        log_h = max(100, screen_h - pos_y)

    form.genre_window.geometry(f"{log_w}x{log_h}+{pos_x}+{pos_y}")

    # ここからメイン処理
    # 念のため
    if not hasattr(form, 'var_walk'):
        form.var_walk = tk.IntVar(value=0)
    if not hasattr(form, 'var_run'):
        form.var_run = tk.IntVar(value=0)
    if not hasattr(form, 'var_up'):
        form.var_up = tk.IntVar(value=0)
    if not hasattr(form, 'var_throw'):
        form.var_throw = tk.IntVar(value=0)
    if not hasattr(form, 'var_face'):
        form.var_face = tk.IntVar(value=0)
    if not hasattr(form, 'var_action'):
        form.var_action = tk.IntVar(value=0)
    if not hasattr(form, 'genre_checkedList'):
        form.genre_checkedList = [0, 0, 0, 0, 0, 0]

    chb_frame = tk.Frame(form.genre_window, bg="#000000")
    chb_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    for i in range(3):
        chb_frame.grid_columnconfigure(i, weight=1)

    for i, content in enumerate(form.genre_list):
        row = i // 3  # 行番号
        col = i % 3   # 列番号
        
        chb = tk.Checkbutton(chb_frame, text=content, command=lambda x=i: set_genre(x))
        chb.config(font=("Helvetica", 12),bg="#FFFFFF", fg="#2E2E2E", activebackground="#A7A7A7", activeforeground="#FFFFFF", bd=0)
        chb.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

    # テキストボックスと追加ボタンを下部に配置
    bottom_frame = tk.Frame(form.genre_window, bg="#000000")
    bottom_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)

    form.genre_window.txtbox_addgenre = tk.Text(bottom_frame, height=1, width=30)
    form.genre_window.txtbox_addgenre.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
    
    form.genre_window.btn_addgenre = tk.Button(bottom_frame, text="追加", command=lambda: add_Genre())
    form.genre_window.btn_addgenre.pack(side=tk.RIGHT)
  


def popup_select_genre(form):
    """ジャンル選択の処理"""
    new_window = tk.Toplevel(form)
    new_window.title("ジャンル選択画面")
    new_window.geometry("500x400")
    new_window.resizable(False, False)

    x = (new_window.winfo_screenwidth() - 500) // 2
    y = (new_window.winfo_screenheight() - 400) // 2
    new_window.geometry(f"+{x}+{y}")
   
    def on_confirm():
        set_Genre(form, form.genre_var.get())  # ジャンル設定
        new_window.destroy()  # ウィンドウを閉じる

    def on_clear():
        set_Genre(form, None)  # ジャンル設定解除
        new_window.destroy()  # ウィンドウを閉じる


    # ジャンル選択のラジオボタン
    form.genre_var = tk.StringVar(value=form.genre_list[0])
    for genre in form.genre_list:
        rb = ttk.Radiobutton(new_window, text=genre, variable=form.genre_var, value=genre)
        rb.pack(anchor=tk.W)

    # ジャンル解除ボタンを作成
    btn_cancel = ttk.Button(new_window, text="解除", command=on_clear)
    btn_cancel.pack(pady=10)

    # 確定ボタンを作成
    btn_confirm = ttk.Button(new_window, text="確定", command=on_confirm)
    btn_confirm.pack(pady=10)

    # 閉じるボタンを作成
    btn_close = ttk.Button(new_window, text="閉じる", command=new_window.destroy)
    btn_close.pack(pady=10)
    
    rb_frame = tk.Frame(new_window, bg="#000000")
    rb_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    for i in range(3):
        rb_frame.grid_columnconfigure(i, weight=1)

    form.genre_var = tk.StringVar(value=form.genre_list[0])
    
    for i, content in enumerate(form.genre_list):
        row = i // 3  # 行番号
        col = i % 3   # 列番号
        
        rb = tk.Radiobutton(rb_frame, text=content, variable=form.genre_var, value=genre, command=lambda x=i: set_genre(x))
        rb.config(font=("Helvetica", 12),bg="#FFFFFF", fg="#2E2E2E", activebackground="#A7A7A7", activeforeground="#FFFFFF", bd=0)
        rb.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

    # テキストボックスと追加ボタンを下部に配置
    bottom_frame = tk.Frame(form.genre_window, bg="#000000")
    bottom_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)

    form.genre_window.txtbox_addgenre = tk.Text(bottom_frame, height=1, width=30)
    form.genre_window.txtbox_addgenre.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
    
    form.genre_window.btn_addgenre = tk.Button(bottom_frame, text="追加", command=lambda: add_Genre())
    form.genre_window.btn_addgenre.pack(side=tk.RIGHT)

def set_Genre(form, genre):
    """選択された一つ以上の動画にジャンルを設定する"""
    # 念のため
    if len(form.selected_videos) < 1:
        return

    for label in form.selected_videos.keys():
        # all_videosから対応するファイルパスを探す
        target_filepath = None
        for file_path, info in form.all_videos.items():
            if info['label'] == label:
                target_filepath = file_path
                break
        
        if target_filepath:
            # ジャンルを解除する場合
            if genre is None:
                # ジャンル解除
                form.all_videos[target_filepath]['genre'] = None
                # ログに記録
                add_log(f"動画 {os.path.basename(target_filepath)} のジャンルを解除")

                # ファイル名のみを抽出して表示
                file_name = os.path.basename(target_filepath)
                form.header.lbl_videoName.config(text=f"選択動画： {file_name}")

            # ジャンルを設定する場合
            else:
                form.all_videos[target_filepath]['genre'] = genre
                # ログに記録
                add_log(f"動画 {os.path.basename(target_filepath)} のジャンルを「{genre}」に設定")

                # ファイル名のみを抽出して表示
                file_name = os.path.basename(target_filepath)
                
                form.header.lbl_videoName.config(text=f"選択動画： [{genre}] {file_name}")


def check_Genre(form):
    """genre_checkedList(0または1を格納)を参照し、動画の表示/非表示を切り替える。    """
    # all_videos がなければ何もしない
    if not hasattr(form, "all_videos") or not form.all_videos:
        return

    # いずれも未選択なら全表示（順序を詰める）
    if not any(form.genre_checkedList):
        visible_items = list(form.all_videos.items())
    else:
        # 選択されているジャンル名の集合を作る
        active_genres = {form.genre_list[i] for i, v in enumerate(form.genre_checkedList) if v}
        # 表示対象のみ抽出（ジャンルが設定されていて active_genres に含まれるものを表示）                                   
        visible_items = [
            (path, info) for path, info in form.all_videos.items()
            if info.get('label') and info.get('genre') in active_genres
        ]

    # 非表示にするものは先にすべて隠す
    for path, info in form.all_videos.items():
        widget = info.get('container') or info.get('label')
        if widget:
            widget.grid_remove()

    # 表示対象を左上から詰めて配置
    for idx, (path, info) in enumerate(visible_items):
        widget = info.get('container') or info.get('label')
        if not widget:
            continue
        col = idx % getattr(form, 'col_size', 3)
        row = idx // getattr(form, 'col_size', 3)
        widget.grid(row=row, column=col, padx=5, pady=5)

    if hasattr(form, "mainForm") and hasattr(form, "frm_setVideo"):
        form.frm_setVideo.update_idletasks()
        try:
            form.mainForm.configure(scrollregion=form.mainForm.bbox("all"))
        except Exception:
            pass

def reset_Genre(form):
    """ジャンル選択をリセットする"""
    form.var_walk.set(0)
    form.var_run.set(0)
    form.var_up.set(0)
    form.var_throw.set(0)
    form.var_face.set(0)
    form.var_action.set(0)
    form.genre_checkedList = [0, 0, 0, 0, 0, 0]
    check_Genre(form)
