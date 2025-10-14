import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage,ttk,Menu

from menu_file import(delete_video,new_file)

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
    form.header.lbl_video_name=tk.Label(form.header,text="選択動画： なし", width=50, anchor="w")
    form.header.lbl_video_name.pack(side=tk.LEFT,padx=5,pady=5)
    form.header.lbl_video_name.config(bg="#FFFFFF",fg="#000000")

    # 画面サイズを変更するボタン
    form.header.btn_size_minus = tk.Button(form.header, text="－", width=3, command=lambda: form.change_size(form.set_size + 1))
    form.header.btn_size_minus.pack(side=tk.RIGHT, padx=5, pady=5)
    form.header.btn_size_minus.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)
        
    form.header.btn_size_plus = tk.Button(form.header, text="＋", width=3, command=lambda: form.change_size(form.set_size - 1))
    form.header.btn_size_plus.pack(side=tk.RIGHT, padx=5, pady=5)
    form.header.btn_size_plus.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD", activeforeground="#FFFFFF", bd=0)

    form.menubar=Menu(form)
    form.genre_menu = Menu(form, tearoff=0)
    form.genre_menu.add_checkbutton(label=form.genre_list[0], variable=form.var_walk, command=lambda: set_genre(0))
    form.genre_menu.add_checkbutton(label=form.genre_list[1], variable=form.var_run, command=lambda: set_genre(1))
    form.genre_menu.add_checkbutton(label=form.genre_list[2], variable=form.var_up, command=lambda: set_genre(2))
    form.genre_menu.add_checkbutton(label=form.genre_list[3], variable=form.var_throw, command=lambda: set_genre(3))
    form.genre_menu.add_checkbutton(label=form.genre_list[4], variable=form.var_face, command=lambda: set_genre(4))
    form.genre_menu.add_checkbutton(label=form.genre_list[5], variable=form.var_action, command=lambda: set_genre(5))

    def set_genre(genre_index):
        # genre_indexに対応したチェックボックスが未選択なら0、選択中なら1をリストに保存
        if form.check_genre_list[genre_index] == 0:
            form.check_genre_list[genre_index] = 1
        else:
            form.check_genre_list[genre_index] = 0
        form.check_genre(genre_index)

    def show_menu():
        try:
            x_pos = form.header.genre_btn.winfo_rootx()
            y_pos = form.header.genre_btn.winfo_rooty() + form.header.genre_btn.winfo_height()
            form.genre_menu.tk_popup(x_pos, y_pos) 
        finally:
            form.genre_menu.grab_release()
    def add_menu():
        return

    # ボタンを作成
    form.header.genre_btn = tk.Button(form.header, text="ジャンル", command=lambda: show_menu())
    form.header.genre_btn.pack(side=tk.LEFT,padx=5, pady=5)

    # 動画再生コントロールを設置するフッターを作成
    form.footer = tk.Frame(form)
    form.footer.pack(side=tk.BOTTOM, fill=tk.X)
    form.footer.config(bg="#2E2E2E")
    form.footer.pack_propagate(False)
    form.footer.config(height=100)
    form.footer.pack(pady=5)

    # 巻き戻し
    form.footer.btn_rewind = tk.Button(form.footer, text="<< 5s", width=5, command=form.back)
    form.footer.btn_rewind.pack(side=tk.LEFT, padx=5, pady=5)

    # 一コマ戻す
    form.footer.btn_frame_back = tk.Button(form.footer, text="|<", width=5, command=form.frame_back)
    form.footer.btn_frame_back.pack(side=tk.LEFT, padx=5, pady=5)

    # 再生/一時停止
    form.footer.btn_play_pause = tk.Button(form.footer, text="▶", width=10, command=form.toggle_play)
    form.footer.btn_play_pause.pack(side=tk.LEFT, padx=5, pady=5)

    # 一コマ進む
    form.footer.btn_frame_forward = tk.Button(form.footer, text=">|", width=5, command=form.frame_forward)
    form.footer.btn_frame_forward.pack(side=tk.LEFT, padx=5, pady=5)

    # 早送り
    form.footer.btn_skip = tk.Button(form.footer, text="5s >>", width=5, command=form.forward)
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
