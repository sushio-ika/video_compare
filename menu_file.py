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

def delete_video(form, widgets=None):
    """現在選択している動画を削除する"""
    if widgets is None:
        widgets = list(form.selected_label.keys())

    # 選択されたすべての動画を削除
    for widget in widgets:
        # video_infoから対応するファイルパスを探す
        delete_filepath = None
        for file_path, info in form.video_info.items():
            if info['label'] == widget:
                delete_filepath = file_path
                break
        
        if delete_filepath:
            info = form.video_info[delete_filepath]
            if info.get('stop_flag'):
                info['stop_flag'].set()
            if info.get('capture'):
                info['capture'].release()
            widget.destroy()

            del form.video_info[delete_filepath]
            
            # 削除後、選択されたラベルリストからも削除
            if widget in form.selected_label:
                del form.selected_label[widget]
    
    if not form.video_info:
        form.update_widget(tk.DISABLED)

    form.change_size(form.set_size)

def save_file(form, overwrite=False):
    """ファイルを保存する"""
    if overwrite:
        form.title(form.current_file)
    else:
        # 名前を付けて保存の処理
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mlk",
            filetypes=[("Murti Link Files", "*.mlk"), ("All Files", "*.*")]
        )
        if file_path:
            form.current_file = file_path
            form.title(form.current_file)

def open_file(form):
    """ファイルを開く"""
    file_path = filedialog.askopenfilename(
        title="ファイルを開く",
           filetypes=[("Murti Link Files", "*.mlk"), ("All Files", "*.*")]
    )
    if file_path:
        form.current_file = file_path
        form.title(form.current_file)

def new_file(form):
    """新しいファイルを作成する"""
    form.current_file = None
    form.title("新規ファイル")