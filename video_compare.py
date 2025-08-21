import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

#メインウィンドウの作成
form = tk.Tk()
form.title("動画比較アプリ")
form.geometry("800x600")

def select_video_file():
    """動画を選択する関数"""
    filepath = filedialog.askopenfilename(
        title="動画を選択してください",
        filetypes=[("Video files","*.mp4 *.avi *.mov *.mkv")]
    )
    if filepath:
        capture = cv2.VideoCapture(filepath)
        play_video(capture)

def play_video(capture):
    """動画を再生する関数"""
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break
        #OpenCVのBGR形式からPILのRGB形式に変換
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(img)
        video_label.config(image=img)
        video_label.image = img
        video_label.update()
    capture.release()

def left_clickmovie(event, img_path, img_name):
    """動画がクリックされたときの処理"""

def apply_image_highlight(image_name, highlight_on):
    """動画に枠線を適用する関数"""

def right_clickmenu(event):
    """右クリックメニューを表示する関数"""
    menu = tk.Menu(form, tearoff=0)
    menu.add_command(label="ヘルプ", command=show_how_to_use)
    menu.add_command(label="設定", command=show_settings)
    menu.add_separator()
    menu.add_command(label="一つ戻す", command=put_one_back)
    menu.add_command(label="一つ進める", command=put_one_forward)
    menu.add_separator()
    menu.add_command(label="コピー", command=copy_video)
    menu.add_command(label="貼り付け", command=paste_video)
    menu.add_command(label="切り取り", command=cut_video)
    menu.add_command(label="削除", command=delete_video)
    menu.add_separator()

    save_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="保存", menu=save_menu)
    save_menu.add_command(label="上書き保存", command=save_file(overwrite=True))
    save_menu.add_command(label="名前を付けて保存", command=save_file(overwrite=False))

    open_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="開く", menu=open_menu)
    open_menu.add_command(label="ファイルを開く", command=open_file)
    open_menu.add_command(label="動画を開く", command=select_video_file)
    
    menu.add_command(label="新規作成", command=new_file)
    menu.add_separator()
    menu.add_command(label="終了", command=form.quit)
    menu.post(event.x_root, event.y_root)

def show_how_to_use():
    """使い方を表示"""
    messagebox.showinfo(
        "動画比較アプリの使い方",
        "1. 動画を選択するには、「動画を選択」ボタンをクリックします。\n"
        "2. 動画が再生されます。左クリックで動画を選択し、右クリックでメニューを表示します。\n"
    )

def show_settings():
    """設定メニューを表示"""
    
def put_one_back():
    """操作を1つ戻す"""
    form.edit_undo()

def put_one_forward():
    """操作を1つ進める"""
    form.edit_redo()

def copy_video():
    """動画をコピーする"""
    form.event_generate("<<Copy>>")

def paste_video():
    """動画を貼り付ける"""
    form.event_generate("<<Paste>>")

def cut_video():
    """動画を切り取る"""
    form.event_generate("<<Cut>>")

def delete_video():
    """動画を削除する"""
    form.event_generate("<<Delete>>")

def save_file(overwrite=False):
    """動画を保存する"""

def open_file():
    """動画を開く"""

def new_file():
    """新しい動画を作成する"""
    

#UI部品の配置
select_button = tk.Button(form, text="動画を選択", command=select_video_file)
select_button.pack()

#動画表示用のラベル
video_label = tk.Label(form)
video_label.pack()

form.bind("<Button-1>", lambda event: left_clickmovie(event, None, None))
form.bind("<Button-3>", lambda event: right_clickmenu(event))
#ウィンドウを中央に配置
form.update_idletasks()

x = (form.winfo_screenwidth() // 2) - (form.winfo_width() // 2)   #(画面の幅 // 2) - (ウィンドウの幅 // 2)
y = (form.winfo_screenheight() // 2) - (form.winfo_height() // 2) #(画面の高さ // 2) - (ウィンドウの高さ // 2)

form.geometry(f"+{x}+{y}")

form.mainloop()