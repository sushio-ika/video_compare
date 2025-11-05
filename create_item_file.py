import tkinter as tk
from tkinter import ttk

from menu_file import(delete_Video,show_LogWindow,show_FileWindow)
from genre_file import(show_GenreWindow)
from log_file import(add_log)

def create_widgets(form):
    """UI部品の配置""" 
    # ヘッダーを作成
    form.header = tk.Frame(form)
    form.header.pack(side=tk.TOP, fill=tk.X)
    form.header.config(bg="#282828")
    form.header.pack_propagate(False)
    form.header.config(height=50)
    form.header.pack(pady=5)

    # ファイル選択ボタン
    form.header.btn_log = tk.Button(form.header, text="≣", width=3, command=lambda: show_FileWindow(form))
    form.header.btn_log.pack(side=tk.LEFT, padx=5, pady=5)
    form.header.btn_log.config(bg="#282828", fg="#FFFFFF", activebackground="#A7A7A7", activeforeground="#FFFFFF", bd=0)

    # ログ表示ボタン
    #form.header.btn_log = tk.Button(form.header, text="ログ", width=3, command=lambda: show_LogWindow(form))
    #form.header.btn_log.pack(side=tk.LEFT, padx=5, pady=5)
    #form.header.btn_log.config(bg="#2E2E2E", fg="#FFFFFF", activebackground="#7A7A7A", activeforeground="#FFFFFF", bd=0)

    # ジャンル選択ボタン
    form.header.btn_genre = tk.Button(form.header, text="ジャンル", command=lambda: show_GenreWindow(form))
    form.header.btn_genre.pack(side=tk.LEFT,padx=5, pady=5)
    form.header.btn_genre.config(bg="#282828", fg="#FFFFFF", activebackground="#7A7A7A", activeforeground="#FFFFFF", bd=0)

    # 動画順序入れ替えボタン
    form.header.btn_sort = tk.Button(form.header, text="並び替え", width=6, command=lambda: form.change_video_order())
    form.header.btn_sort.pack(side=tk.LEFT, padx=5, pady=5)
    form.header.btn_sort.config(bg="#282828", fg="#FFFFFF", activebackground="#7A7A7A", activeforeground="#FFFFFF", bd=0)

    # 選択中の動画名を画面中央に表示するラベル
    form.header.lbl_videoName=tk.Label(form.header,text="選択動画： なし", width=50, anchor="w")
    form.header.lbl_videoName.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)
    form.header.lbl_videoName.config(bg="#FFFFFF",fg="#000000")


    # 画面サイズを変更するボタン
    form.header.btn_sizeMinus = tk.Button(form.header, text="－", width=3, command=lambda: form.change_VideoSize(form.col_size + 1))
    form.header.btn_sizeMinus.pack(side=tk.RIGHT, padx=5, pady=5)
    form.header.btn_sizeMinus.config(font=("bold"),bg="#4A90E2", fg="#FFFFFF", activebackground="#A5D2FF", activeforeground="#FFFFFF", bd=0)

    form.header.btn_sizePlus = tk.Button(form.header, text="＋", width=3, command=lambda: form.change_VideoSize(form.col_size - 1))
    form.header.btn_sizePlus.pack(side=tk.RIGHT, padx=5, pady=5)
    form.header.btn_sizePlus.config(font=("bold"),bg="#4A90E2", fg="#FFFFFF", activebackground="#A5D2FF", activeforeground="#FFFFFF", bd=0)



    # ここからフッター部分の作成
    # 動画再生コントロールを設置するフッターを作成
    form.footer = tk.Frame(form)
    form.footer.pack(side=tk.BOTTOM, fill=tk.X)
    form.footer.config(bg="#282828")
    form.footer.pack_propagate(False)
    form.footer.config(height=100)
    form.footer.pack(pady=5)

    # 巻き戻し
    form.footer.btn_rewind = tk.Button(form.footer, text="<< 5s", width=5, command=form.rewind_Video)
    form.footer.btn_rewind.pack(side=tk.LEFT, padx=5, pady=5)

    # 一コマ戻す
    form.footer.btn_frameBack = tk.Button(form.footer, text="|<", width=5, command=form.rewind_Flame)
    form.footer.btn_frameBack.pack(side=tk.LEFT, padx=5, pady=5)

    # 再生/一時停止
    form.footer.btn_playPause = tk.Button(form.footer, text="▶", width=10, command=form.change_PlayPause)
    form.footer.btn_playPause.pack(side=tk.LEFT, padx=5, pady=5)

    # 一コマ進む
    form.footer.btn_frameForward = tk.Button(form.footer, text=">|", width=5, command=form.forward_Flame)
    form.footer.btn_frameForward.pack(side=tk.LEFT, padx=5, pady=5)

    # 早送り
    form.footer.btn_skip = tk.Button(form.footer, text="5s >>", width=5, command=form.forward_Video)
    form.footer.btn_skip.pack(side=tk.LEFT, padx=5, pady=5)

    # 進捗バーとタイムスタンプ
    form.prgbar_videoTime = ttk.Progressbar(form.footer, orient="horizontal", length=300, mode="determinate")
    form.prgbar_videoTime.pack(side=tk.LEFT, padx=5, pady=5)

    form.lbl_timestamp = tk.Label(form.footer, text="00:00/00:00")
    form.lbl_timestamp.config(font=("Helvetica", 16))
    form.lbl_timestamp.pack(side=tk.LEFT, padx=5, pady=5)
        
    # 追加・削除ボタン
    form.footer.btn_addVideo = tk.Button(form.footer, text="追加", width=20, command=form.select_Video)
    form.footer.btn_addVideo.pack(side=tk.RIGHT, padx=5, pady=5)
    form.footer.btn_addVideo.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#A5D2FF", activeforeground="#FFFFFF", bd=0)

    form.footer.btn_deleteVideo = tk.Button(form.footer, text="削除", width=20, command=lambda: delete_Video(form))
    form.footer.btn_deleteVideo.pack(side=tk.RIGHT, padx=5, pady=5)
    form.footer.btn_deleteVideo.config(bg="#D9534F", fg="#FFFFFF", activebackground="#FF938F", activeforeground="#FFFFFF", bd=0)
        
    # 動画表示用のスクロール可能フレーム
    form.mainForm = tk.Canvas(form, bg="#2E2E2E")
    form.scrbar_mainForm = tk.Scrollbar(form, orient="vertical", command=form.mainForm.yview)
    form.mainForm.configure(yscrollcommand=form.scrbar_mainForm.set)

    form.mainForm.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    form.scrbar_mainForm.pack(side=tk.RIGHT, fill=tk.Y)

    # mainFormに各動画表示フレームを作成
    form.frm_setVideo = tk.Frame(form.mainForm, bg="#2E2E2E")
    form.mainForm.create_window((0, 0), window=form.frm_setVideo, anchor="nw")

    # mainFormサイズに合わせてスクロール領域を更新
    def updateScroll(event):
        form.mainForm.configure(scrollregion=form.mainForm.bbox("all"))
    form.frm_setVideo.bind("<Configure>", updateScroll)
