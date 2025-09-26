import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage,ttk,Menu

from menu_file import(delete_video)

def create_widgets(form):
    """UI部品の配置""" 
    # ヘッダーを作成
    form.header = tk.Frame(form)
    form.header.pack(side=tk.TOP, fill=tk.X)
    form.header.config(bg="#2E2E2E")
    form.header.pack_propagate(False)
    form.header.config(height=50)
    form.header.pack(pady=5)

    form.header.btn_exit = tk.Button(form.header, text="終了", width=10, command=lambda: form.destroy())
    form.header.btn_exit.pack(side=tk.LEFT, padx=5, pady=5)
    form.header.btn_exit.config(bg="#D9534F", fg="#FFFFFF", activebackground="#C9302C", activeforeground="#FFFFFF", bd=0)

    # ファイル保存、開くボタン
    form.header.btn_open = tk.Button(form.header, text="開く", width=10, command=lambda: messagebox.showinfo("情報", "保存機能は未実装です。"))
    form.header.btn_open.pack(side=tk.LEFT, padx=5, pady=5)
    form.header.btn_open.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)
        
    form.header.btn_save = tk.Button(form.header, text="保存", width=10, command=lambda: messagebox.showinfo("情報", "保存機能は未実装です。"))
    form.header.btn_save.pack(side=tk.LEFT, padx=5, pady=5)
    form.header.btn_save.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)

    form.header.btn_new = tk.Button(form.header, text="新規作成", width=10, command=lambda: messagebox.showinfo("情報", "新規作成機能は未実装です。"))
    form.header.btn_new.pack(side=tk.LEFT, padx=5, pady=5)
    form.header.btn_new.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)

    # 選択中の動画名を表示するラベル
    form.header.lbl_video_name=tk.Label(form.header,text="選択動画：",width=100 )
    form.header.lbl_video_name.pack(side=tk.LEFT,padx=5,pady=5)
    form.header.lbl_video_name.config(bg="#FFFFFF",fg="#000000")

    # 画面サイズを変更するボタン
    form.header.btn_size_minus = tk.Button(form.header, text="－", width=3, command=lambda: form.change_size(form.set_size + 1))
    form.header.btn_size_minus.pack(side=tk.RIGHT, padx=5, pady=5)
    form.header.btn_size_minus.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)
        
    form.header.btn_size_plus = tk.Button(form.header, text="＋", width=3, command=lambda: form.change_size(form.set_size - 1))
    form.header.btn_size_plus.pack(side=tk.RIGHT, padx=5, pady=5)
    form.header.btn_size_plus.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)

    # 動画再生コントロールを設置するフッターを作成
    form.footer = tk.Frame(form)
    form.footer.pack(side=tk.BOTTOM, fill=tk.X)
    form.footer.config(bg="#2E2E2E")
    form.footer.pack_propagate(False)
    form.footer.config(height=100)
    form.footer.pack(pady=5)

    # 巻き戻し
    form.footer.btn_rewind = tk.Button(form.footer, text="<< 5s", width=10, command=form.back)
    form.footer.btn_rewind.pack(side=tk.LEFT, padx=5, pady=5)

    # 再生/一時停止
    form.footer.btn_play_pause = tk.Button(form.footer, text="▶", width=10, command=lambda: form.toggle_play)
    form.footer.btn_play_pause.pack(side=tk.LEFT, padx=5, pady=5)

    # 早送り
    form.footer.btn_skip = tk.Button(form.footer, text="5s >>", width=10, command=form.front)
    form.footer.btn_skip.pack(side=tk.LEFT, padx=5, pady=5)

    # 進捗バーとタイムスタンプ
    form.progress_bar = ttk.Progressbar(form.footer, orient="horizontal", length=300, mode="determinate")
    form.progress_bar.pack(side=tk.LEFT, padx=5, pady=5)

    form.lbl_timestamp = tk.Label(form.footer, text="00:00/00:00")
    form.lbl_timestamp.config(font=("Helvetica", 16))
    form.lbl_timestamp.pack(side=tk.LEFT, padx=5, pady=5)
        
    # 追加・削除ボタン
    form.footer.mini_select_button = tk.Button(form.footer, text="追加", width=20, command=form.select_video)
    form.footer.mini_select_button.pack(side=tk.RIGHT, padx=5, pady=5)
    form.footer.mini_select_button.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)

    form.footer.btn_delete = tk.Button(form.footer, text="削除", width=20, command=lambda: delete_video(form, widgets=list(form.selected_label.keys())))
    form.footer.btn_delete.pack(side=tk.RIGHT, padx=5, pady=5)
    form.footer.btn_delete.config(bg="#D9534F", fg="#FFFFFF", activebackground="#C9302C", activeforeground="#FFFFFF", bd=0)
        
    # 動画表示用のスクロール可能フレーム
    form.canvas = tk.Canvas(form, bg="#2E2E2E")
    form.scrollbar = tk.Scrollbar(form, orient="vertical", command=form.canvas.yview)
    form.canvas.configure(yscrollcommand=form.scrollbar.set)

    form.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    form.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Canvas内にFrameを作成
    form.video_frame = tk.Frame(form.canvas, bg="#2E2E2E")
    form.canvas.create_window((0, 0), window=form.video_frame, anchor="nw")

    # Canvasサイズに合わせてスクロール領域を更新
    def on_frame_configure(event):
        form.canvas.configure(scrollregion=form.canvas.bbox("all"))
    form.video_frame.bind("<Configure>", on_frame_configure)

