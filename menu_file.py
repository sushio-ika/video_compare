import os
import json

import tkinter as tk
from tkinter import messagebox, filedialog, ttk

from log_file import(add_log)
from genre_file import(check_Genre)

def show_AppInfo():
    """使い方を表示"""
    messagebox.showinfo(
        "マルチリンクの使い方",
        "1. 動画を追加するには、ドラッグ&ドロップまたは右下の「追加」ボタンを使用します。\n"
        "2. 左下の再生コントロールで動画を操作します。\n"
        "3. 動画をダブルクリックすると動画が拡大表示されます。"
    )

def show_Ver():
    messagebox.showinfo("バージョン情報",
                        "バージョン\tver.0.0.3\n"
                        "更新日\t2025/10/27\n")

def send_Inquiry():
    """お問い合わせメールを送信"""

def show_SettingWindow(form):
    """設定メニューを表示"""
    messagebox.showinfo("設定", "設定メニューはまだ実装されていません。")

def put_Undo(form):
    """操作を1つ戻す"""
    messagebox.showinfo("情報", "未実装")

def put_Redo(form):
    """操作を1つ進める"""
    messagebox.showinfo("情報", "未実装")

def copy_Video(form):
    """動画をコピーする"""
    if form.selected_videos:
        form.change_VideoState(tk.NORMAL)
        copy_list=form.get_ClipPath()

        try:
            edit_list = "\n".join(copy_list)
            form.clipboard_clear()
            form.clipboard_append(edit_list)

            print(f"動画をコピーしました: {edit_list}")
        
        except tk.TclError as e:
            print(f"クリップボードへのアクセスエラー: {e}")

def paste_Video(form):
    """動画を貼り付ける"""
    try:
        paste_list = form.clipboard_get()
        edit_list=paste_list.strip().split('\n')

        for path in edit_list:
            if os.path.isfile(path):
                form.add_Video(path)

                # 選択状態にしてラベルに表示
                for filepath, info in form.all_videos.items():
                    if path==filepath:
                        form.set_VideoHighlight(info["label"])
                        form.selected_videos[info["label"]]=True
                        form.lbl_timestamp.config(text="00:00/00:00")
                        form.set_NameLabel()

                print(f"動画を貼り付けました: {edit_list}")
            else:
                print("クリップボードの内容は有効なファイルパスではありません。")
    except tk.TclError:
        print("クリップボードから有効なテキストを取得できませんでした。")

def cut_Video(form):
    """動画を切り取る"""
    if form.selected_videos:
        form.change_VideoState(tk.NORMAL)
        cut_list=form.get_ClipPath()

        try:
            edit_list = "\n".join(cut_list)
            form.clipboard_clear()
            form.clipboard_append(edit_list)
            
            for path in cut_list:
                for filepath, info in form.all_videos.items():
                    if path==filepath: 
                        widget=info['label']
                        form.selected_videos[widget]=True
            delete_Video(form)

            form.change_VideoSize(form.col_size)

            print(f"動画をカットしました: {cut_list}")
        
        except tk.TclError as e:
            print(f"クリップボードへのアクセスエラー: {e}")

def delete_Video(form):
    """現在選択している動画を削除する"""
    del_Videos = list(form.selected_videos.keys())
    
    if not del_Videos:
        messagebox.showerror("エラー","削除する動画を選択してください")

    # 選択されたすべての動画を削除
    for widget in del_Videos:
        # video_infoから対応するファイルパスを探す
        delete_filepath = None
        for file_path, info in form.all_videos.items():
            if info['label'] == widget:
                delete_filepath = file_path
                break
        
        if delete_filepath:
            info = form.all_videos[delete_filepath]
            if info.get('stop_flag'):
                info['stop_flag'].set()
            if info.get('capture'):
                    info['capture'].release()
            widget.destroy()

            del form.all_videos[delete_filepath]
            
            # 削除後、選択されたラベルリストからも削除
            if widget in form.selected_videos:
                del form.selected_videos[widget]
    
    # videoIDを割り振り直す
    sorted_videos = sorted(
        form.all_videos.items(),
        key=lambda x: x[1]['videoID']
    )
    for idx, (file_path, info) in enumerate(sorted_videos):
        info["videoID"]=idx

    # 動画を再配置
    form.relocate_Video()

    if not form.all_videos:
        form.change_VideoSize(form.col_size)
        form.change_VideoState(tk.DISABLED)
        form.change_ExistvideoState(tk.DISABLED)


def show_SelectSave(form, overwrite=False):
    """ファイルを保存する"""
    #上書き保存か名前を付けて保存（current_filepathの中身が存在しているかどうか）
    if overwrite and form.current_file:
        #上書き保存
        file_path = form.current_file
    else:
        # 名前を付けて保存の処理
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ml",
            filetypes=[("Murti Link Files", "*.ml"), ("All Files", "*.*")]
        )
        #ファイルパスが空の場合は保存しない
        if not file_path:
            return
        
        form.current_file = file_path
        videos=[]
        n=1
        # videoID でソート
        sorted_videos = sorted(
            form.all_videos.items(),
            key=lambda x: x[1]['videoID']
        )
        for path,info in sorted_videos:
            videos.append({f"video{n}":{"filepath":path,"videoid":info["videoID"],"genre":info["genre"]}})
            n+=1

        if (n-1)!=len(form.all_videos):
            messagebox.showerror("エラー","保存操作でエラーが発生しました")

        savedata = {
            "genre":form.genre_list,
            "check":form.genre_checkedList,
            "size": form.col_size,
            "num":n-1,
            "videos": videos 
        }

        with open(form.current_file, "w", encoding="utf-8") as f:
            json.dump(savedata, f, indent=4)#JSON形式で保存

        print("保存完了", "ファイルが正常に保存されました。")

        form.title(os.path.basename(form.current_file))

def open_File(form):
    """ファイルを開く"""
    file_path = filedialog.askopenfilename(
        title="ファイルを開く",
           filetypes=[("Murti Link Files", "*.ml"), ("All Files", "*.*")]
    )

    if not file_path:
        return

    form.current_file = file_path#ファイルパスを更新
    form.title(os.path.basename(form.current_file))

    form.genre_list = []
    form.genre_checkedList = []

    if len(form.all_videos)>0:
        # 追加されている動画を削除するためにselected_videosに追加して疑似選択状態にする
        for info in form.all_videos.values():
            widget=info['label']
            form.selected_videos[widget]=True
        delete_Video(form)

    form.all_videos={}
    form.selected_videos = {}
        
    with open(form.current_file, "r", encoding="utf-8") as f:
        loaddata = json.load(f)

    if "genre" in loaddata:
        for g in loaddata["genre"]:
            form.genre_list.append(g)
    else:
        form.genre_list = ["歩き","走り","持ち上げる","投げる","表情","アクション"]

    if "check" in loaddata:
        for g in loaddata["check"]:
            form.genre_checkedList.append(g)
    else:
        form.genre_checkedList = [0] * len(form.genre_list)
        
    if "size" in loaddata:#フォントサイズが指定されている場合
        form.change_VideoSize(loaddata["size"])
    else:
        form.change_VideoSize(3)#デフォルトサイズ

    if "videos" in loaddata:
        video_list= loaddata["videos"]
        for video_item in video_list:
            for key,video_info in video_item.items():
                file_path=video_info["filepath"]
                genre=video_info["genre"]

                if form.add_Video(file_path):
                    form.header.btn_genre.config(state=tk.NORMAL)
                    form.all_videos[file_path]['genre'] = genre
    
    
    check_Genre(form)

def create_NewFile(form):
    """新しいファイルを作成する"""
    form.current_file = None#ファイルパスを更新
    form.genre_list = ["歩き","走り","持ち上げる","投げる","表情","アクション"]
    form.genre_checkedList = [0] * len(form.genre_list)
    form.change_VideoSize(3)#デフォルトサイズ

    if len(form.all_videos)>0:
        # 追加されている動画を削除するためにselected_videosに追加して疑似選択状態にする
        for info in form.all_videos.values():
            widget=info['label']
            form.selected_videos[widget]=True
        delete_Video(form)

    form.all_videos={}
    form.selected_videos = {}
            
    check_Genre(form)
    form.title(os.path.basename("新規ファイル"))

def show_SelectSave(form,overwrite=False):
    ow=overwrite
    saveselect_window = tk.Toplevel(form)
    saveselect_window.title("保存方法選択画面")
    saveselect_window.geometry("300x300")
    saveselect_window.wm_overrideredirect(True)
    saveselect_window.resizable(False, False)

    x = (saveselect_window.winfo_screenwidth() - 500) // 2
    y = (saveselect_window.winfo_screenheight() - 400) // 2
    saveselect_window.geometry(f"+{x}+{y}")

    btn_close=tk.Button(saveselect_window,text="✕",bg="#2E2E2E",fg="#FFFFFF",command=saveselect_window.destroy)
    btn_savePass=tk.Button(saveselect_window,text="パスのみ保存",width=30,height=3,command=lambda: show_SelectSave(form,ow))
    btn_saveVideo=tk.Button(saveselect_window,text="動画ごと保存",width=30,height=3,command=lambda: messagebox.showinfo("情報","未実装"))

    btn_close.grid(row=0,column=2)
    btn_savePass.grid(row=1,column=1)
    btn_saveVideo.grid(row=2,column=1)

def show_LogWindow(form):
    """ログ表示ウィンドウを表示"""
    if hasattr(form, 'log_window') and form.log_window.winfo_exists():
        form.log_window.lift()  # すでにウィンドウが存在する場合は前面に持ってくる
        return

    form.log_window = tk.Toplevel(form)
    form.log_window.configure(bg="#2E2E2E")
    form.log_window.overrideredirect(True)
    form.log_window.resizable(False,False)
    form.log_window.focus_set()
    
    def on_focusout(event):
        if not event.widget is form.log_window:
            return
        form.log_window.destroy()
    
    form.log_window.bind("<FocusOut>", on_focusout)

    form.update_idletasks()

    # ログウィンドウの幅と高さを計算
    lWindow_width = 400
    lWindow_height = max(100, form.winfo_height() - form.header.winfo_height() - form.footer.winfo_height())

    # 画面上の配置位置を計算
    pos_x = form.winfo_rootx()
    pos_y = form.winfo_rooty() + form.header.winfo_height()

    # 画面外にはみ出さないように調整（必要なら）
    screen_height = form.winfo_screenheight()
    if pos_y + lWindow_height > screen_height:
        lWindow_height = max(100, screen_height - pos_y)

    form.log_window.geometry(f"{lWindow_width}x{lWindow_height}+{pos_x}+{pos_y}")


    # テキストウィジェットを作成してログを表示
    txt_log = tk.Text(form.log_window, wrap=tk.WORD)
    txt_log.pack(expand=True, fill=tk.BOTH)
    
    # ログファイルの内容を読み込んでテキストウィジェットに挿入
    file_path = "ml.log"
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as log_file:
            log_content = log_file.read()
            txt_log.insert(tk.END, log_content)
    else:
        txt_log.insert(tk.END, "ログファイルが見つかりません。")

    # テキストウィジェットを読み取り専用に設定
    txt_log.config(state=tk.DISABLED)

def show_FileWindow(form):
    """ファイル機能選択ウィンドウを表示"""
    if hasattr(form, 'file_window') and form.file_window.winfo_exists():
        form.file_window.destroy()  # すでにウィンドウが存在する場合は前面に持ってくる

    form.file_window = tk.Toplevel(form)
    form.file_window.configure(bg="#2E2E2E")
    form.file_window.overrideredirect(True)
    form.file_window.resizable(False,False)
    form.file_window.focus_set()
    
    def on_focusout(event):
        if not event.widget is form.file_window:
            return
        form.file_window.destroy()
    
    form.file_window.bind("<FocusOut>", on_focusout)
    
    form.update_idletasks()

    fWindow_width = 200
    fWindow_height = 400

    # 画面上の配置位置を計算（ヘッダーの下、左端）
    pos_x = form.winfo_rootx()
    pos_y = form.winfo_rooty() + form.header.winfo_height()

    # 画面外にはみ出さないように調整（必要なら）
    screen_height = form.winfo_screenheight()
    if pos_y + fWindow_height > screen_height:
        fWindow_height = max(100, screen_height - pos_y)

    form.file_window.geometry(f"{fWindow_width}x{fWindow_height}+{pos_x}+{pos_y}")

    # ボタンを表示するフレーム
    frm_menu = tk.Frame(form.file_window)
    frm_menu.config(bg="#2E2E2E")
    frm_menu.pack(fill=tk.X, padx=8, pady=8)

    # 終了ボタン
    form.file_window.btn_closeApp = tk.Button(frm_menu, text="終了", width=20, command=form.close_App)
    form.file_window.btn_closeApp.grid(row=0,column=0)
    form.file_window.btn_closeApp.config(bg="#D9534F", fg="#FFFFFF", activebackground="#C9302C", activeforeground="#FFFFFF", bd=0)

    # ファイル保存、開くボタン
    form.file_window.btn_openFile = tk.Button(frm_menu, text="開く", width=20, command=lambda: open_File(form))
    form.file_window.btn_openFile.grid(row=1,column=0)
    form.file_window.btn_openFile.config(bg="#2E2E2E", fg="#FFFFFF", activebackground="#A7A7A7", activeforeground="#FFFFFF", bd=0)

    form.file_window.btn_saveFile = tk.Button(frm_menu, text="保存", width=20, command=lambda: show_SelectSave(form, overwrite=False))
    form.file_window.btn_saveFile.grid(row=2,column=0)
    form.file_window.btn_saveFile.config(bg="#2E2E2E", fg="#FFFFFF", activebackground="#A7A7A7", activeforeground="#FFFFFF", bd=0)

    form.file_window.btn_newFile = tk.Button(frm_menu, text="新規作成", width=20, command=lambda: create_NewFile(form))
    form.file_window.btn_newFile.grid(row=3,column=0)
    form.file_window.btn_newFile.config(bg="#2E2E2E", fg="#FFFFFF", activebackground="#A7A7A7", activeforeground="#FFFFFF", bd=0)


