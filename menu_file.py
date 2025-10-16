import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os

from log_file import(add_log)

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
                        "更新日\t2025/09/28\n")
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
        file_path = form.clipboard_get()
        if os.path.isfile(file_path):
            form.add_video(file_path)
            print(f"クリップボードから貼り付けました: {file_path}")
            return file_path
        else:
            print("クリップボードの内容は有効なファイルパスではありません。")
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
            form.change_size(form.set_size)
        
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
    
def log_box(form):
    """ログ表示ウィンドウを表示"""
    if hasattr(form, 'log_window') and form.log_window.winfo_exists():
        form.log_window.lift()  # すでにウィンドウが存在する場合は前面に持ってくる
        return

    form.log_window = tk.Toplevel(form)
    form.log_window.configure(bg="#000000")
    form.log_window.overrideredirect(True)
    form.log_window.resizable(False,False)
    form.log_window.focus_set()
    form.log_window.bind("<FocusOut>", lambda event:form.log_window.destroy())
    
    # メインウィンドウのレイアウト情報を確実に取得する
    form.update_idletasks()

    # ヘッダーとフッターの高さを取得（存在しない場合は0）
    header_h = form.header.winfo_height()
    footer_h = form.footer.winfo_height()

    # ログウィンドウの幅と高さを計算
    log_w = 400
    log_h = max(100, form.winfo_height() - header_h - footer_h)  # 最低高さを確保

    # 画面上の配置位置を計算（ヘッダーの下、左端）
    pos_x = form.winfo_rootx()
    pos_y = form.winfo_rooty() + header_h

    # 画面外にはみ出さないように調整（必要なら）
    screen_h = form.winfo_screenheight()
    if pos_y + log_h > screen_h:
        log_h = max(100, screen_h - pos_y)

    form.log_window.geometry(f"{log_w}x{log_h}+{pos_x}+{pos_y}")


    # テキストウィジェットを作成してログを表示
    text_widget = tk.Text(form.log_window, wrap=tk.WORD)
    text_widget.pack(expand=True, fill=tk.BOTH)
    
    # ログファイルの内容を読み込んでテキストウィジェットに挿入
    log_file_path = "ml.log"  # ログファイルのパスを指定
    if os.path.isfile(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as log_file:
            log_content = log_file.read()
            text_widget.insert(tk.END, log_content)
    else:
        text_widget.insert(tk.END, "ログファイルが見つかりません。")

    # テキストウィジェットを読み取り専用に設定
    text_widget.config(state=tk.DISABLED)

def file_box(form):
    """ファイル機能選択ウィンドウを表示"""
    if hasattr(form, 'file_window') and form.file_window.winfo_exists():
        form.file_window.lift()  # すでにウィンドウが存在する場合は前面に持ってくる
        return

    form.file_window = tk.Toplevel(form)
    form.file_window.configure(bg="#000000")
    form.file_window.overrideredirect(True)
    form.file_window.resizable(False,False)
    form.file_window.focus_set()
    form.file_window.bind("<FocusOut>", lambda event:form.file_window.destroy())

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

    form.file_window.geometry(f"{log_w}x{log_h}+{pos_x}+{pos_y}")

    # ファイル保存、開くボタン
    form.file_window.btn_open = tk.Button(form.file_window, text="開く", width=10, command=lambda: messagebox.showinfo("情報", "保存機能は未実装です。"))
    form.file_window.btn_open.pack(side=tk.LEFT, padx=5, pady=5)
    form.file_window.btn_open.config(bg="#2E2E2E", fg="#FFFFFF", activebackground="#A7A7A7", activeforeground="#FFFFFF", bd=0)

    form.file_window.btn_save = tk.Button(form.file_window, text="保存", width=10, command=lambda: messagebox.showinfo("情報", "保存機能は未実装です。"))
    form.file_window.btn_save.pack(side=tk.LEFT, padx=5, pady=5)
    form.file_window.btn_save.config(bg="#2E2E2E", fg="#FFFFFF", activebackground="#A7A7A7", activeforeground="#FFFFFF", bd=0)

    form.file_window.btn_new = tk.Button(form.file_window, text="新規作成", width=10, command=lambda: messagebox.showinfo("情報", "新規作成機能は未実装です。"))
    form.file_window.btn_new.pack(side=tk.LEFT, padx=5, pady=5)
    form.file_window.btn_new.config(bg="#2E2E2E", fg="#FFFFFF", activebackground="#A7A7A7", activeforeground="#FFFFFF", bd=0)

    def on_closing():
        add_log("END\n\n")
        form.destroy()

    # 終了ボタン
    form.file_window.btn_exit = tk.Button(form.file_window, text="終了", width=10, command=on_closing)
    form.file_window.btn_exit.pack(side=tk.LEFT, padx=5, pady=5)
    form.file_window.btn_exit.config(bg="#D9534F", fg="#FFFFFF", activebackground="#C9302C", activeforeground="#FFFFFF", bd=0)

