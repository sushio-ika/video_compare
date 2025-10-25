import tkinter as tk
from tkinter import messagebox, ttk
import os
from log_file import(add_log)

MAX_GENRE=30

def set_genre(form, genre_index):
    # genre_indexに対応したチェックボックスが未選択なら0、選択中なら1をリストに保存
    if form.genre_checkedList[genre_index] == 0:
        form.genre_checkedList[genre_index] = 1
    else:
        form.genre_checkedList[genre_index] = 0
    check_Genre(form)

def add_Genre(form,listbox):
    txt = form.new_window.txtbox_addgenre.get().strip()

    if not txt:
        messagebox.showinfo("情報", "追加するジャンル名を入力してください。")
        return
    
    if len(form.genre_list)>=MAX_GENRE:
        messagebox.showinfo("情報","ジャンル数が最大に達しました。\n追加するには、いずれかを削除してください")
        return
    
    if txt in form.genre_list:
        messagebox.showinfo("情報", "既に同名のジャンルが存在します。")
        return
    
    form.genre_list.append(txt)
    form.genre_checkedList.append(0)

    # リストを更新
    listbox.insert(tk.END, txt)
    form.new_window.txtbox_addgenre.delete(0, tk.END)


def show_GenreWindow(form):
    """ジャンル選択メニューを表示"""
    def on_focusout(event):
        if event.widget is form.genre_window:
            return
        form.genre_window.destroy()

    # 全選択・全解除の処理をする関数
    def check_all(form, chflg):
        if chflg:
            if all(x==1 for x in form.genre_checkedList):
                return
        else:
            if all(x==0 for x in form.genre_checkedList):
                return
            
        for i in range(len(form.genre_checkedList)):
            form.genre_checkedList[i] = 1 if chflg else 0
        form.genre_window.destroy()
        show_GenreWindow(form)
        check_Genre(form)

    if hasattr(form, 'genre_window') and form.genre_window.winfo_exists():
        form.genre_window.lift()  # すでにウィンドウが存在する場合は前面に持ってくる
        return

    genre_sum=[0]* len(form.genre_list) # ジャンルごとの設定個数をカウントする

    form.genre_window = tk.Toplevel(form)
    form.genre_window.configure(bg="#2E2E2E")
    form.genre_window.overrideredirect(True)
    form.genre_window.resizable(False,False)
    form.genre_window.bind("<FocusOut>", on_focusout)
        
    form.update_idletasks()
    header_h = form.header.winfo_height()

    log_w = 400
    log_h = 400

    pos_x = form.winfo_rootx()
    pos_y = form.winfo_rooty() + header_h

    screen_h = form.winfo_screenheight()

    if pos_y + log_h > screen_h:
        log_h = max(100, screen_h - pos_y)

    form.genre_window.geometry(f"{log_w}x{log_h}+{pos_x}+{pos_y}")


    # ここからメイン処理
    btn_frame=tk.Frame(form.genre_window,bg="#2E2E2E")
    btn_frame.pack(fill=tk.X,padx=5,pady=5)

    btn_allCheck=tk.Button(btn_frame,text="全選択", width=8, command=lambda: check_all(form, True))
    btn_allCheck.config(bg="#2E2E2E", fg="#FFFFFF", activebackground="#7A7A7A", activeforeground="#FFFFFF", bd=0)
    btn_allCheck.pack(side=tk.LEFT,padx=5)
    btn_allRemove=tk.Button(btn_frame,text="全解除", width=8, command=lambda: check_all(form, False))
    btn_allRemove.config(bg="#2E2E2E", fg="#FFFFFF", activebackground="#7A7A7A", activeforeground="#FFFFFF", bd=0)
    btn_allRemove.pack(side=tk.LEFT,padx=5)

    chb_frame = tk.Frame(form.genre_window, bg="#2E2E2E")
    chb_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    chb_frame.focus_set()

    # 各ジャンルの設定個数をカウント
    for idx, info in enumerate(form.all_videos.values()):
            genre = info['genre']
            for i, content in enumerate(form.genre_list):
                if genre==content:
                    genre_sum[i]+=1

    # フレームを3列に設定
    for i in range(3):
        chb_frame.grid_columnconfigure(i, weight=1)

    # 左上から順にジャンルを設置
    for i, content in enumerate(form.genre_list):
        row = i // 3  # 行番号
        col = i % 3   # 列番号
        
        chb = tk.Checkbutton(chb_frame, text=content+f"({str(genre_sum[i])})",variable=content, command=lambda x=i: set_genre(form, x))
        chb.config(font=("Helvetica", 8),bg="#FFFFFF", fg="#2E2E2E", activebackground="#A7A7A7", activeforeground="#FFFFFF", bd=0)
        chb.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

        if form.genre_checkedList[i]==1:
            chb.select()
        else:
            chb.deselect()



def popup_select_genre(form):
    """ジャンル選択の処理"""
    def delete_Genre(form,genre):
        if genre in form.genre_list:  
            result=messagebox.askyesno("確認",f"ジャンル「{genre}」を本当に削除しますか？")
            
            if result:
                index = form.genre_list.index(genre)
                form.genre_list.pop(index)
                form.genre_checkedList.pop(index)
                lb.delete(lb.curselection())
                popup_select_genre(form)
            else:
                return
    
    def click_RightMenu(form,event=None):
        widget=event.widget
        select_list=widget.curselection()
        
        # 何も選択しなかった場合
        if not select_list:
            return
        
        selected_genre = widget.get(widget.curselection())

        menu=tk.Menu(form,tearoff=0)
        menu.add_command(label="このジャンルを削除", command=lambda: delete_Genre(form,selected_genre))
        menu.post(event.x_root, event.y_root)

    form.new_window = tk.Toplevel(form)
    form.new_window.title("ジャンル選択画面")
    form.new_window.geometry("500x400")
    form.new_window.resizable(False, False)

    x = (form.new_window.winfo_screenwidth() - 500) // 2
    y = (form.new_window.winfo_screenheight() - 400) // 2
    form.new_window.geometry(f"+{x}+{y}")
   
    list_frame = tk.Frame(form.new_window)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    lb = tk.Listbox(list_frame, selectmode=tk.SINGLE, exportselection=False, font=("Helvetica", 11))
    sb = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=lb.yview)
    lb.config(yscrollcommand=sb.set)
    lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    lb.focus_set()

    # リストにジャンルを挿入
    for genre in form.genre_list:
        lb.insert(tk.END, genre)
    
    lb.bind("<Button-3>", lambda event: click_RightMenu(form, event))
    lb.select_set(0)

    try:
        initial_genre = None

        if hasattr(form, "selected_videos") and form.selected_videos:
            sel_label = next(iter(form.selected_videos.keys()))
            for path, info in getattr(form, "all_videos", {}).items():
                if info.get("label") == sel_label:
                    initial_genre = info.get("genre")
                    break

        if initial_genre:
            try:
                idx = form.genre_list.index(initial_genre)
                lb.selection_set(idx)
                lb.see(idx)
            except ValueError:
                pass

    except Exception:
        pass

    # 操作パネル
    bottom = tk.Frame(form.new_window)
    bottom.pack(fill=tk.X, padx=8, pady=(0,8))

    # 新規ジャンル追加
    form.new_window.txtbox_addgenre = tk.Entry(bottom)
    form.new_window.txtbox_addgenre.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))
    form.new_window.btn_addgenre = tk.Button(bottom, text="追加", width=8, command=lambda: add_Genre(form, lb))
    form.new_window.btn_addgenre.pack(side=tk.LEFT, padx=(0,6))

    def on_confirm():
        sel = lb.curselection()
        if not sel:
            messagebox.showinfo("情報", "ジャンルを選択してください。")
            return
        genre = lb.get(sel[0])
        set_Genre(form, genre)
        form.new_window.destroy()

    def on_clear():
        set_Genre(form, None)
        form.new_window.destroy()

    btn_clear = tk.Button(bottom, text="解除", command=on_clear, width=8)
    btn_clear.config(bg="#D9534F", fg="#FFFFFF", activebackground="#C9302C",bd=0)
    btn_clear.pack(side=tk.LEFT, padx=(0,6))
    btn_confirm = tk.Button(bottom, text="確定", command=on_confirm, width=8)
    btn_confirm.config(bg="#4A90E2", fg="#FFFFFF", activebackground="#357ABD",bd=0)
    btn_confirm.pack(side=tk.LEFT, padx=(0,6))
    btn_close = tk.Button(bottom, text="閉じる", command=form.new_window.destroy, width=8)
    btn_close.pack(side=tk.RIGHT)

        
    def on_entry_enter(event):
        add_Genre(form, lb)
    form.new_window.txtbox_addgenre.bind("<Return>", on_entry_enter)

    

def set_Genre(form, genre):
    """選択された一つ以上の動画にジャンルを設定する"""
    # 念のため
    if len(form.selected_videos) < 1:
        return

    for label in form.selected_videos.keys():
        # all_videosから対応するファイルパスを探す
        target_filepath = None
        for file_path, info in form.all_videos.items():
            if info['label'] == label:
                target_filepath = file_path
                break
        
        if target_filepath:
            # ジャンルを解除する場合
            if genre is None:
                # ジャンル解除
                form.all_videos[target_filepath]['genre'] = None
                # ログに記録
                add_log(f"動画 {os.path.basename(target_filepath)} のジャンルを解除")

                # ファイル名のみを抽出して表示
                file_name = os.path.basename(target_filepath)
                form.header.lbl_videoName.config(text=f"選択動画： {file_name}")

            # ジャンルを設定する場合
            else:
                form.all_videos[target_filepath]['genre'] = genre
                # ログに記録
                add_log(f"動画 {os.path.basename(target_filepath)} のジャンルを「{genre}」に設定")

                # ファイル名のみを抽出して表示
                file_name = os.path.basename(target_filepath)
                
                form.header.lbl_videoName.config(text=f"選択動画： [{genre}] {file_name}")
        check_Genre(form)


def check_Genre(form):
    """genre_checkedList(0または1を格納)を参照し、動画の表示/非表示を切り替える。    """
    # all_videos がなければ何もしない
    if not hasattr(form, "all_videos") or not form.all_videos:
        return

    # いずれも未選択なら全表示（順序を詰める）
    if not any(form.genre_checkedList):
        visible_items = list(form.all_videos.items())
    else:
        # 選択されているジャンル名の集合を作る
        active_genres = {form.genre_list[i] for i, v in enumerate(form.genre_checkedList) if v}
        # 表示対象のみ抽出（ジャンルが設定されていて active_genres に含まれるものを表示）                                   
        visible_items = [
            (path, info) for path, info in form.all_videos.items()
            if info.get('label') and info.get('genre') in active_genres
        ]

    # 非表示にするものは先にすべて隠す
    for path, info in form.all_videos.items():
        widget = info.get('container') or info.get('label')
        if widget:
            widget.grid_remove()

    # 表示対象を左上から詰めて配置
    for idx, (path, info) in enumerate(visible_items):
        widget = info.get('container') or info.get('label')
        if not widget:
            continue
        col = idx % getattr(form, 'col_size', 3)
        row = idx // getattr(form, 'col_size', 3)
        widget.grid(row=row, column=col, padx=5, pady=5)

    if hasattr(form, "mainForm") and hasattr(form, "frm_setVideo"):
        form.frm_setVideo.update_idletasks()
        try:
            form.mainForm.configure(scrollregion=form.mainForm.bbox("all"))
        except Exception:
            pass

def reset_Genre(form):
    """ジャンル選択をリセットする"""
    form.var_walk.set(0)
    form.var_run.set(0)
    form.var_up.set(0)
    form.var_throw.set(0)
    form.var_face.set(0)
    form.var_action.set(0)
    form.genre_checkedList = [0, 0, 0, 0, 0, 0]
    check_Genre(form)
