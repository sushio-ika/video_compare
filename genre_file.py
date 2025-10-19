import tkinter as tk
from tkinter import messagebox, ttk
import os
from log_file import(add_log)

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
        selected_genre(form, form.genre_var.get())  # ジャンル設定
        new_window.destroy()  # ウィンドウを閉じる

    def on_clear():
        selected_genre(form, None)  # ジャンル設定解除
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

def selected_genre(form, genre):
    """選択された一つ以上の動画にジャンルを設定する"""
    # 念のため
    if len(form.selected_label) < 1:
        return

    for label in form.selected_label.keys():
        # video_infoから対応するファイルパスを探す
        target_filepath = None
        for file_path, info in form.video_info.items():
            if info['label'] == label:
                target_filepath = file_path
                break
        
        if target_filepath:
            # ジャンルを解除する場合
            if genre is None:
                # ジャンル解除
                form.video_info[target_filepath]['genre'] = None
                # ログに記録
                add_log(f"動画 {os.path.basename(target_filepath)} のジャンルを解除")

                # ファイル名のみを抽出して表示
                file_name = os.path.basename(target_filepath)
                form.header.lbl_video_name.config(text=f"選択動画： {file_name}")

            # ジャンルを設定する場合
            else:
                form.video_info[target_filepath]['genre'] = genre
                # ログに記録
                add_log(f"動画 {os.path.basename(target_filepath)} のジャンルを「{genre}」に設定")

                # ファイル名のみを抽出して表示
                file_name = os.path.basename(target_filepath)
                form.header.lbl_video_name.config(text=f"選択動画： [{genre}] {file_name}")


def check_genre(form):
    """check_genre_list(0または1を格納)を参照し、動画の表示/非表示を切り替える。
    表示するものは左上から順に詰めて grid 配置する。
    """
    # video_info がなければ何もしない
    if not hasattr(form, "video_info") or not form.video_info:
        return

    # いずれも未選択なら全表示（順序を詰める）
    if not any(form.check_genre_list):
        visible_items = list(form.video_info.items())
    else:
        # 選択されているジャンル名の集合を作る
        active_genres = {form.genre_list[i] for i, v in enumerate(form.check_genre_list) if v}
        # 表示対象のみ抽出（ジャンルが設定されていて active_genres に含まれるものを表示）                                   
        visible_items = [
            (path, info) for path, info in form.video_info.items()
            if info.get('label') and info.get('genre') in active_genres
        ]

    # 非表示にするものは先にすべて隠す（透明扱い）
    for path, info in form.video_info.items():
        widget = info.get('container') or info.get('label')
        if widget:
            widget.grid_remove()

    # 表示対象を左上から詰めて配置
    for idx, (path, info) in enumerate(visible_items):
        widget = info.get('container') or info.get('label')
        if not widget:
            continue
        col = idx % getattr(form, 'set_size', 3)
        row = idx // getattr(form, 'set_size', 3)
        widget.grid(row=row, column=col, padx=5, pady=5)

    # 更新（必要ならスクロール領域などを更新）
    if hasattr(form, "canvas") and hasattr(form, "video_frame"):
        form.video_frame.update_idletasks()
        try:
            form.canvas.configure(scrollregion=form.canvas.bbox("all"))
        except Exception:
            pass

def reset_genre(form):
    """ジャンル選択をリセットする"""
    form.var_walk.set(0)
    form.var_run.set(0)
    form.var_up.set(0)
    form.var_throw.set(0)
    form.var_face.set(0)
    form.var_action.set(0)
    form.check_genre_list = [0, 0, 0, 0, 0, 0]
    check_genre(form)
