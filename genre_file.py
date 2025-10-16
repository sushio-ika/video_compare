import tkinter as tk
from tkinter import messagebox, ttk

def popup_select_genre(form):
    """ジャンル選択の処理"""
    new_window = tk.Toplevel(form)
    new_window.title("ジャンル選択画面")
    new_window.geometry("500x400")
    new_window.resizable(False, False)

    x = (new_window.winfo_screenwidth() - 500) // 2
    y = (new_window.winfo_screenheight() - 400) // 2
    new_window.geometry(f"+{x}+{y}")

    # ジャンル選択のラジオボタン
    form.genre_var = tk.StringVar(value=form.genre_list[0])
    for genre in form.genre_list:
        rb = ttk.Radiobutton(new_window, text=genre, variable=form.genre_var, value=genre)
        rb.pack(anchor=tk.W)

    # 確定ボタンを作成
    btn_confirm = ttk.Button(new_window, text="確定", command=lambda: selected_genre(form, form.genre_var.get()))
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
            form.video_info[target_filepath]['genre'] = genre


def check_genre(form):
    # いずれも未選択なら全表示
    if not any(form.check_genre_list):
        for path, info in form.video_info.items():
            label = info.get('label')
            if label:
                label.grid()
        return

    # 選択されているジャンル名の集合を作る
    active_genres = {form.genre_list[i] for i, v in enumerate(form.check_genre_list) if v}

    # 各動画をチェックし、ジャンルが active_genres に含まれれば表示、そうでなければ非表示
    for path, info in form.video_info.items():
        label = info.get('label')
        genre = info.get('genre')

        # 動画が存在しない場合
        if not label:
            continue

        # ジャンルが設定されていない場合は非表示
        if genre is not None and genre in active_genres:
            label.grid()
        else:
            label.grid_remove()

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
