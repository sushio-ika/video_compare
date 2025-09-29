import tkinter as tk
from tkinter import messagebox, filedialog
import os

def show_how_to_use(form):
    """使い方を表示"""
    messagebox.showinfo(
        "マルチリンクの使い方",
        "1. 動画を追加するには、ドラッグ&ドロップまたは右下の「追加」ボタンを使用します。\n"
        "2. 左下の再生コントロールで動画を操作します。\n"
        "3. 動画をダブルクリックすると動画が拡大表示されます。"
    )

def show_version(form):
    messagebox.showinfo("バージョン情報",
                        "バージョン\tver.0.0.1\n"
                        "更新日\t2025/09/28")
def show_settings(form):
    """設定メニューを表示"""
    messagebox.showinfo("設定", "設定メニューはまだ実装されていません。")

def put_one_back(form):
    """操作を1つ戻す"""
    messagebox.showinfo("情報", "未実装")

def put_one_forward(form):
    """操作を1つ進める"""
    messagebox.showinfo("情報", "未実装")

def copy_video(form):
    """動画をコピーする"""
    if form.selected_label:
        form.change_control_mode(tk.NORMAL)
        file_path=form.get_file_path()
        try:
            form.clipboard_clear()
            form.clipboard_append(file_path)
        
            print(f"クリップボードにコピーされました: {file_path}")
        
        except tk.TclError as e:
            print(f"クリップボードへのアクセスエラー: {e}")

def paste_video(form):
    """動画を貼り付ける"""
    try:
        # 1. クリップボードの内容を取得
        file_path = form.clipboard_get()
        
        if file_path:
            print(f"クリップボードから取得したテキスト: {file_path}")
            form.add_video(file_path)
        else:
            print("クリップボードが空です。")
            return None
            
    except tk.TclError:
        print("クリップボードから有効なテキストを取得できませんでした。")
        return None

def cut_video(form):
    """動画を切り取る"""
    if form.selected_label:
        form.change_control_mode(tk.NORMAL)
        file_path=form.get_file_path()
        try:
            form.clipboard_clear()
            form.clipboard_append(file_path)
            delete_video(form, widgets=list(form.selected_label.keys()))
        
            print(f"クリップボードにコピーされました: {file_path}")
        
        except tk.TclError as e:
            print(f"クリップボードへのアクセスエラー: {e}")

def delete_video(form, widgets=None):
    """現在選択している動画を削除する"""
    if widgets is None:
        widgets = list(form.selected_label.keys())

    if not widgets:
        messagebox.showerror("エラー","削除する動画を選択してください")

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
        form.change_size(form.set_size)
        form.change_control_mode(tk.DISABLED)
        form.change_widget_mode(tk.DISABLED)

    

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
    form.title("マルチリンク -新規ファイル-")

def copy_video_name(form):
    if len(form.selected_label)==1:
        form.change_control_mode(tk.NORMAL)
        file_path=form.get_file_path()

        file_name = os.path.basename(file_path)

        try:
            form.clipboard_clear()
            form.clipboard_append(file_name)
        
            print(f"クリップボードにコピーされました: {file_name}")
        
        except tk.TclError as e:
            print(f"クリップボードへのアクセスエラー: {e}")
    
