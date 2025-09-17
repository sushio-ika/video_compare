import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
import cv2
from PIL import Image, ImageTk
import threading
import os
from tkinterdnd2 import TkinterDnD
from menu_file import (
    show_how_to_use,
    show_settings,
    put_one_back,
    put_one_forward,
    copy_video,
    paste_video,
    cut_video,
    delete_video,
    save_file,
    open_file,
    new_file
)
from videosize_file import (
    update_video_frame,
    resize_start,
    resize_video,
    resize_end
)

PICTURE_WIDTH = 320  #動画表示の横幅を固定

#DPI設定（Windowsでの高解像度対応）
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

#メインウィンドウを定義
class videocompare(TkinterDnD.Tk):
    def __init__(form):
        super().__init__()
        
        form.title("マルチリンク")
        form.geometry("800x600")
        form.tk_setPalette(background="#2E2E2E", foreground="#FFFFFF")
        form.current_file = None  #現在開いているファイルのパス
        form.resize_info = None  #サイズ変更の情報を保存する辞書

        #複数の動画を管理するリスト
        form.video_captures = {}  # {ファイルパス: cv2.VideoCaptureオブジェクト}
        form.video_labels = []    # 動画を表示するLabelウィジェットのリスト
        form.video_info = {}      # 動画の情報を管理する辞書
        
        form.create_widgets()

        form.bind("<Button-3>", lambda event: form.right_clickmenu(event))
        form.bind("<Button-1>", lambda event: form.left_click(event, False))
        form.bind("<Control-Button-1>", lambda event: form.left_click(event, True))
        

        #ウィンドウを中央に配置
        form.update_idletasks()

        x = (form.winfo_screenwidth() // 2) - (form.winfo_width() // 2)   #(画面の幅 // 2) - (ウィンドウの幅 // 2)
        y = (form.winfo_screenheight() // 2) - (form.winfo_height() // 2) #(画面の高さ // 2) - (ウィンドウの高さ // 2)

        form.geometry(f"+{x}+{y}")

    def create_widgets(form):
        """UI部品の配置""" 
        #ドロップエリア（Labelウィジェットとして作成）
        form.drop_area = tk.Label(form, text="ここに動画をドラッグ＆ドロップ",relief="solid", bd=1, width=60, height=20)
        form.drop_area.pack(pady=10, fill=tk.BOTH, expand=True)
        form.drop_area.config(bg="#3C3F41", fg="#FFFFFF")

        #ファイル選択ボタン
        form.select_button = tk.Button(form, text="＋", command=form.select_video_file)
        form.select_button.pack(pady=5)
        form.select_button.config(font=("Arial", 24), width=3, height=1)
        form.select_button.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)
        
        #tkinterdnd2を使ってドラッグ＆ドロップ機能を有効化
        form.drop_area.drop_target_register(1, 'DND_Files')
        form.drop_area.dnd_bind('<<Drop>>', form.on_drop_files)
        
        #動画表示用のフレーム
        form.video_frame = tk.Frame(form)
        form.video_frame.pack(fill=tk.BOTH, expand=True)

    def on_drop_files(form, event):
        """ドロップされたファイルを処理する関数"""
        files = form.tk.splitlist(event.data)
        for file_path in files:
            if file_path.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                form.add_video_to_app(file_path)

    def select_video_file(form):
        """ファイルダイアログから動画を選択する関数"""
        filepath = filedialog.askopenfilename(
            title="動画を選択してください",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if filepath:
            form.add_video_to_app(filepath)
    
    def add_video_to_app(form, file_path):
        """動画をアプリに追加し、再生を準備する関数"""
        if file_path in form.video_captures:
            messagebox.showinfo("情報", "この動画はすでに追加されています。")
            return
        
        capture = cv2.VideoCapture(file_path)
        if not capture.isOpened():
            messagebox.showerror("エラー", f"動画ファイルを開けませんでした: {file_path}")
            return
            
        #動画表示用のラベルを作成
        video_label = tk.Label(form.video_frame)
        video_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        form.video_labels.append(video_label)
        form.video_captures[file_path] = capture
        
        #再生用のスレッドを開始
        stop_flag = threading.Event()
        thread = threading.Thread(target=form.play_video, args=(capture, video_label, stop_flag))
        thread.daemon = True
        thread.start()

        form.video_info[file_path] = {'label': video_label, 'thread': thread, 'stop_flag': stop_flag}

        #ドラッグアンドドロップエリアを透明化
        form.drop_area.pack_forget()

    def play_video(form, capture, video_label, stop_flag):
        """動画を再生する関数"""
        while capture.isOpened() and not stop_flag.is_set():
            ret, frame = capture.read()
            if not ret:
                break
            
            #動画のサイズを調整
            frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            aspect_ratio = frame_height / frame_width
            new_width = PICTURE_WIDTH
            new_height = int(new_width * aspect_ratio)

            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)
            
            video_label.after(1, lambda: form.update_label_image(video_label, img_tk))

            delay_ms = int(1000 / capture.get(cv2.CAP_PROP_FPS))
            cv2.waitKey(delay_ms)

        capture.release()

    def update_label_image(form, video_label, img_tk):
        """ラベルの画像を更新する関数"""
        video_label.config(image=img_tk)
        video_label.image = img_tk

    def left_click(form, event, ctrl_click):
        """マウスの左クリックを処理する"""
        widget = event.widget
        if widget in form.video_labels:#動画をクリックした場合
            if ctrl_click:#Ctrlキーが押されている場合
                if form.selected_label == widget:#すでに選択されている動画をクリックした場合
                    form.reset_video_highlight(widget)
                    form.selected_label = None
                else:#新たに選択された動画をクリックした場合
                    form.apply_image_highlight(widget)
            else:#Ctrlキーが押されていない場合
                form.reset_all_highlights()
                form.apply_image_highlight(widget)
            form.selected_label = widget  # 現在選択中のラベルを保存

            # サイズ変更イベントをバインド
            widget.bind("<Button-1>", lambda event: resize_start(form, event))#左クリックでサイズ変更開始
            widget.bind("<B1-Motion>", lambda event: resize_video(form, event))#ドラッグでサイズ変更
            widget.bind("<ButtonRelease-1>", lambda event: resize_end(form, event))#左クリックを離したらサイズ変更終了
        else:#動画以外をクリックした場合
            form.reset_all_highlights()
            form.selected_label = None

    def reset_all_highlights(form):
        """全ての動画のハイライトをリセットする"""
        for label in form.video_labels:
            label.config(bd=0, relief=tk.FLAT)
            label.config(highlightbackground="#2C2C2C", highlightcolor="#2C2C2C", highlightthickness=0)

    def reset_video_highlight(form, label):
        """特定の動画のハイライトをリセットする"""
        label.config(bd=0, relief=tk.FLAT)
        label.config(highlightbackground="#2C2C2C", highlightcolor="#2C2C2C", highlightthickness=0)

    def apply_image_highlight(form, label):
        """選択された動画に青い枠線を適用する"""
        label.config(bd=2, relief=tk.RAISED, highlightbackground="blue", highlightcolor="blue", highlightthickness=2)

    
    def right_clickmenu(form, event):
        """右クリックメニューを表示する関数"""
        menu = tk.Menu(form, tearoff=0)
        menu.add_command(label="ヘルプ", command=lambda: show_how_to_use(form))
        menu.add_command(label="設定", command=lambda: show_settings(form))
        menu.add_separator()
        menu.add_command(label="一つ戻す", command=lambda: put_one_back(form))
        menu.add_command(label="一つ進める", command=lambda: put_one_forward(form))
        menu.add_separator()
        menu.add_command(label="コピー", command=lambda: copy_video(form))
        menu.add_command(label="貼り付け", command=lambda: paste_video(form))
        menu.add_command(label="切り取り", command=lambda: cut_video(form))
        menu.add_command(label="削除", command=lambda: delete_video(form))
        menu.add_separator()

        save_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="保存", menu=save_menu)
        save_menu.add_command(label="上書き保存", command=lambda: save_file(form, overwrite=True))
        save_menu.add_command(label="名前を付けて保存", command=lambda: save_file(form, overwrite=False))

        open_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="開く", menu=open_menu)
        open_menu.add_command(label="ファイルを開く", command=lambda: open_file(form))
        open_menu.add_command(label="動画を開く", command=form.select_video_file)
        menu.add_command(label="新規作成", command=lambda: new_file(form))
        menu.add_separator()
        menu.add_command(label="終了", command=form.quit)
        
        menu.post(event.x_root, event.y_root)

    

if __name__ == '__main__':
    app = videocompare()
    app.mainloop()