import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
import cv2
from PIL import Image, ImageTk
import threading
import os
from tkinterdnd2 import TkinterDnD

PICTURE_WIDTH = 320  #動画表示の横幅を固定
current_file = None  #現在開いているファイルのパス

#DPI設定（Windowsでの高解像度対応）
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

#VideoAppはメインウィンドウを定義
class videocompare(TkinterDnD.Tk):
    def __init__(form):
        super().__init__()
        
        form.title("動画比較アプリ")
        form.geometry("800x600")
        form.tk_setPalette(background="#2E2E2E", foreground="#FFFFFF")

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
        form.select_button = tk.Button(form, text="動画を選択", command=form.select_video_file)
        form.select_button.pack(pady=5)
        form.select_button.config(bg="#3D94CE", fg="#FFFFFF")

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

        #ドラッグアンドドロップエリアと選択ボタンを非表示
        form.drop_area.pack_forget()
        form.select_button.pack_forget()

    def play_video(form, capture, video_label, stop_flag):
        """動画を再生する関数（別スレッドで実行）"""
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
                form.apply_image_highlight(widget)
            else:#Ctrlキーが押されていない場合
                form.reset_all_highlights()
                form.apply_image_highlight(widget)
        else:#動画以外をクリックした場合
            form.reset_all_highlights()

    def reset_all_highlights(form):
        """全ての動画のハイライトをリセットする"""
        for label in form.video_labels:
            label.config(bd=0, relief=tk.FLAT)
            label.config(highlightbackground="#2C2C2C", highlightcolor="#2C2C2C", highlightthickness=0)

    def apply_image_highlight(form, label):
        """選択された動画に青い枠線を適用する"""
        label.config(bd=2, relief=tk.RAISED, highlightbackground="blue", highlightcolor="blue", highlightthickness=2)

    def right_clickmenu(form, event):
        """右クリックメニューを表示する関数"""
        menu = tk.Menu(form, tearoff=0)
        
        menu.add_command(label="ヘルプ", command=form.show_how_to_use)
        menu.add_command(label="設定", command=form.show_settings) 
        menu.add_separator()
        menu.add_command(label="一つ戻す", command=form.put_one_back)
        menu.add_command(label="一つ進める", command=form.put_one_forward)
        menu.add_separator()
        menu.add_command(label="コピー", command=form.copy_video)
        menu.add_command(label="貼り付け", command=form.paste_video)
        menu.add_command(label="切り取り", command=form.cut_video)
        menu.add_command(label="削除", command=form.delete_video)
        menu.add_separator()

        save_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="保存", menu=save_menu)
        save_menu.add_command(label="上書き保存", command=lambda: form.save_file(overwrite=True))
        save_menu.add_command(label="名前を付けて保存", command=lambda: form.save_file(overwrite=False))
        
        open_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="開く", menu=open_menu)
        open_menu.add_command(label="ファイルを開く", command=form.open_file)
        open_menu.add_command(label="動画を開く", command=form.select_video_file)
        
        menu.add_command(label="新規作成", command=form.new_file)
        menu.add_separator()
        menu.add_command(label="終了", command=form.quit)
        
        menu.post(event.x_root, event.y_root)

    def show_how_to_use(form):
        """使い方を表示"""
        messagebox.showinfo(
            "動画比較アプリの使い方",
            "1. 動画を選択するには、「動画を選択」ボタンをクリックします。\n"
            "2. 動画が再生されます。左クリックで動画を選択し、右クリックでメニューを表示します。\n"
        )

    def show_settings():
        """設定メニューを表示"""
    
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
            form.title(current_file)
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

if __name__ == '__main__':
    app = videocompare()
    app.mainloop()