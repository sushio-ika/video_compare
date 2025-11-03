import tkinter as tk
from tkinter import messagebox

from menu_file import (
    show_AppInfo,
    show_Ver,
    send_Inquiry,
    show_SettingWindow,
    put_Undo,
    put_Redo,
    copy_Video,
    paste_Video,
    cut_Video,
    delete_Video,
    show_SelectSave,
    open_File,
    save_File,
    create_NewFile,
)
from genre_file import (popup_select_genre)

def scroll_MouseWheel(form, event):
    """マウスホイールでスクロール処理"""
    # 動画がある範囲のみスクロール可能にする
    if form.mainForm.winfo_height() < form.mainForm.bbox("all")[3]:
        if event.delta > 0:
            form.mainForm.yview_scroll(-1, "units")
        else:
            form.mainForm.yview_scroll(1, "units")
    form.mainForm.yview_moveto(max(0, min(form.mainForm.yview()[0], 1)))

def click_DoubleLeft(form,event):
    """マウスの左ダブルクリック処理"""
    widget=event.widget

    # 再生中なら一時停止
    if form.video_state==False:
        form.change_PlayPause()
        form.video_state = True
        form.footer.btn_playPause.config(text="▶")

    # 動画をダブルクリックしたとき、表示サイズを最大にして、その動画の位置まで遷移する
    if widget in [info['label'] for info in form.all_videos.values()]:
        videoid=form.get_Videoid()
        videonum=form.get_VideoNum()
        
        if videoid==-1:
            messagebox.showerror("エラー","複数の動画が選択されています。") # -1が返ってくるため
        elif videonum==0:
            messagebox.showerror("エラー","動画がまだありません。") # 念のため
        else:
            form.change_VideoSize(1)
            point=videoid / videonum
            form.move_Scrollbar(point)

def click_Left(form, event, click_ctrl):
        """マウスの左クリック処理"""
        widget = event.widget

        #動画をクリックした場合
        if widget in [info['label'] for info in form.all_videos.values()]:
            
            #Ctrlキーが押されている場合
            if click_ctrl:

                #すでに選択されている動画をクリックした場合
                if widget in form.selected_videos:
                    form.clear_AvideoHighlight(widget)
                    del form.selected_videos[widget]
                
                #新たに選択された動画をクリックした場合
                else:
                    form.set_VideoHighlight(widget)
                    form.selected_videos[widget]=True
                    form.lbl_timestamp.config(text="00:00/00:00")
                    form.stop_Video()

            else: # Ctrlキーが押されていない場合
                # いったんすべての選択を解除
                form.clear_AllvideoHighlights()
                form.selected_videos.clear()

                # 現在選択中のラベルを保存
                form.set_VideoHighlight(widget)
                form.selected_videos[widget]=True


            form.set_NameLabel()

        # 再生時間をクリックした場合
        elif widget in [form.lbl_timestamp]:
            form.change_TimeFrame()

        #動画以外をクリックした場合
        else:

            # フッターとヘッダー（一部）のアイテムは例外
            if widget not in [form.footer.btn_rewind, form.footer.btn_frameBack, form.footer.btn_playPause, form.footer.btn_frameForward, form.footer.btn_skip, form.lbl_timestamp, form.footer.btn_deleteVideo, form.header.btn_sizeMinus, form.header.btn_sizePlus, form.header.lbl_videoName,form.header.btn_sort]:
                form.stop_Video()
                form.change_VideoState(tk.DISABLED)
                form.clear_AllvideoHighlights()
                form.selected_videos.clear() # 全てクリア
                form.header.lbl_videoName.config(text="選択動画： なし")
                form.lbl_timestamp.config(text="00:00/00:00")
        


    
def right_clickmenu(form, event):
    """右クリックメニューを表示する関数"""
    widget=event.widget

    if widget in form.selected_videos:
        menu=tk.Menu(form,tearoff=0)
        menu.add_command(label="ジャンル", command=lambda: popup_select_genre(form))
        menu.add_command(label="メディアで再生",command=lambda: form.play_MediaPlayer())
        menu.add_separator()
        menu.add_command(label="コピー", command=lambda: copy_Video(form))
        menu.add_command(label="切り取り", command=lambda: cut_Video(form))
        menu.add_command(label="削除", command=lambda: delete_Video(form))
        menu.post(event.x_root, event.y_root)
    elif widget in [form.header.lbl_videoName] and form.header.lbl_videoName.cget("state") == tk.NORMAL:
        menu=tk.Menu(form,tearoff=0)
        menu.add_command(label="コピー", command=lambda: form.copy_VideoName())
        menu.post(event.x_root, event.y_root)
    else:
        menu = tk.Menu(form, tearoff=0)
        menu.add_command(label="ヘルプ", command=lambda: show_AppInfo())
        menu.add_command(label="バージョン情報", command=lambda: show_Ver())
        menu.add_command(label="問い合わせ",command=lambda: send_Inquiry())
        menu.add_command(label="設定", command=lambda: show_SettingWindow(form))
        menu.add_separator()
        menu.add_command(label="一つ戻す", command=lambda: put_Undo(form))
        menu.add_command(label="一つ進める", command=lambda: put_Redo(form))
        menu.add_separator()
        menu.add_command(label="コピー", command=lambda: copy_Video(form))
        menu.add_command(label="貼り付け", command=lambda: paste_Video(form))
        menu.add_command(label="切り取り", command=lambda: cut_Video(form))
        menu.add_command(label="削除", command=lambda: delete_Video(form))
        menu.add_separator()

        save_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="保存", menu=save_menu)
        save_menu.add_command(label="上書き保存", command=lambda: save_File(form, overwrite=True))    
        save_menu.add_command(label="名前を付けて保存", command=lambda: show_SelectSave(form, overwrite=False))

        open_menu = tk.Menu(menu, tearoff=0)
    
        menu.add_cascade(label="開く", menu=open_menu)
        open_menu.add_command(label="ファイルを開く", command=lambda: open_File(form))
        open_menu.add_command(label="動画を開く", command=form.select_Video)
        menu.add_command(label="新規作成", command=lambda: create_NewFile(form))
        menu.add_separator()
        menu.add_command(label="終了", command=lambda: form.close_App())

        menu.post(event.x_root, event.y_root)
