import tkinter as tk
from tkinter import messagebox, filedialog

def show_how_to_use(form):
    """使い方を表示"""
    messagebox.showinfo(
        "マルチリンクの使い方",
        "1. 動画を選択するには、「動画を選択」ボタンをクリックします。\n"
        "2. 動画が再生されます。左クリックで動画を選択し、右クリックでメニューを表示します。\n"
    )

def show_settings(form):
    """設定メニューを表示"""
    messagebox.showinfo("設定", "設定メニューはまだ実装されていません。")

def put_one_back(form):
    """操作を1つ戻す"""
    form.edit_undo()

def put_one_forward(form):
    """操作を1つ進める"""
    form.edit_redo()

def copy_video(form):
    """動画をコピーする"""
    form.event_generate("<<Copy>>")

def paste_video(form):
    """動画を貼り付ける"""
    form.event_generate("<<Paste>>")

def cut_video(form):
    """動画を切り取る"""
    form.event_generate("<<Cut>>")

def delete_video(form):
    """動画を削除する"""
    form.event_generate("<<Delete>>")

def save_file(form, overwrite=False):
    """ファイルを保存する"""
    if overwrite:
        form.title(form.current_file)
    else:
        # 名前を付けて保存の処理
        file_path = filedialog.asksaveasfilename(
            defaultextension=".vcmp",
            filetypes=[("Video Compare Files", "*.vcmp"), ("All Files", "*.*")]
        )
        if file_path:
            form.current_file = file_path
            form.title(form.current_file)

def open_file(form):
    """ファイルを開く"""
    file_path = filedialog.askopenfilename(
        title="ファイルを開く",
           filetypes=[("Video Compare Files", "*.vcmp"), ("All Files", "*.*")]
    )
    if file_path:
        form.current_file = file_path
        form.title(form.current_file)

def new_file(form):
    """新しいファイルを作成する"""
    form.current_file = None
    form.title("新規ファイル")