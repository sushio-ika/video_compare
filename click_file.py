import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage,ttk
import os
import cv2 as cv
import numpy as np

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
from create_item_file import (create_widgets)

def on_mousewheel(form, event):
    # 動画がある範囲のみスクロール可能にする
    if form.canvas.winfo_height() < form.canvas.bbox("all")[3]:
        if event.delta > 0:
            form.canvas.yview_scroll(-1, "units")
        else:
            form.canvas.yview_scroll(1, "units")
    form.canvas.yview_moveto(max(0, min(form.canvas.yview()[0], 1)))

# ラベルに動画名表示関数
def show_video_name(form, widget):
    show_filepath = None
    for file_path, info in form.video_info.items():
        if info['label'] == widget:
            show_filepath = file_path
            break
    
    form.header.lbl_video_name+=show_filepath

def double_left_click(form,event):
    widget=event.widget
    if widget in [info['label'] for info in form.video_info.values()]:
        selected_label = list(form.selected_label.keys())[0]
        file_path = ""
        for path, info in form.video_info.items():
            if info['label'] == selected_label:
                file_path = path
                break
                
        if file_path:
            form.open_popup_video(file_path)

def left_click(form, event, ctrl_click):
        """マウスの左クリックを処理する"""
        widget = event.widget

        #動画をクリックした場合
        if widget in [info['label'] for info in form.video_info.values()]:
            
            #Ctrlキーが押されている場合
            if ctrl_click:

                #すでに選択されている動画をクリックした場合
                if widget in form.selected_label:
                    reset_video_highlight(form, widget)
                    del form.selected_label[widget]
                
                #新たに選択された動画をクリックした場合
                else:
                    apply_image_highlight(form, widget)
                    form.selected_label[widget]=True

            else: # Ctrlキーが押されていない場合
                # いったんすべての選択を解除
                reset_all_highlights(form)
                form.selected_label.clear()

                # 現在選択中のラベルを保存
                apply_image_highlight(form, widget)
                form.selected_label[widget]=True

            # 一つ選択されていたら動画再生コントロールを有効にしてラベルに動画名を表示
            if len(form.selected_label)==1:
                form.update_widget(tk.NORMAL)

                selected_label = list(form.selected_label.keys())[0]
                file_path = ""
                for path, info in form.video_info.items():
                    if info['label'] == selected_label:
                        file_path = path
                        break
                
                # ファイル名のみを抽出して表示
                file_name = os.path.basename(file_path)
                form.header.lbl_video_name.config(text=f"選択動画： {file_name}")
            else:
                form.update_widget(tk.DISABLED)

                if len(form.selected_label)>1:
                    form.header.lbl_video_name.config(text="選択動画： *")
                else:
                    form.header.lbl_video_name.config(text="選択動画： なし")


        #動画以外をクリックした場合
        else:

            # フッターのアイテムは例外
            if widget not in [form.footer.btn_rewind, form.footer.btn_play_pause, form.footer.btn_skip, form.lbl_timestamp, form.footer.btn_delete]:
                form.update_widget(tk.DISABLED)
                reset_all_highlights(form)
                form.selected_label.clear() # 全てクリア
                form.header.lbl_video_name.config(text="選択動画： なし")

def reset_all_highlights(form):
    """全ての動画のハイライトをリセットする"""
    for info in form.video_info.values():
        info['label'].config(bd=0, relief=tk.FLAT)
        info['label'].config(highlightbackground="#2C2C2C", highlightcolor="#2C2C2C", highlightthickness=0)

def reset_video_highlight(form, label):
    """特定の動画のハイライトをリセットする"""
    label.config(bd=0, relief=tk.FLAT)
    label.config(highlightbackground="#2C2C2C", highlightcolor="#2C2C2C", highlightthickness=0)

def apply_image_highlight(form, label):
    """選択された動画に枠線を適用する"""
    label.config(bd=2, relief=tk.RAISED, highlightbackground="#5FB7FF", highlightcolor="#5FB7FF", highlightthickness=2)

    
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
    menu.add_command(label="削除", command=lambda: delete_video(form,  widgets=list(form.selected_label.keys())))
    menu.add_separator()

    save_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="保存", menu=save_menu)
    save_menu.add_command(label="上書き保存", command=lambda: save_file(form, overwrite=True))
    save_menu.add_command(label="名前を付けて保存", command=lambda: save_file(form, overwrite=False))

    open_menu = tk.Menu(menu, tearoff=0)
    
    menu.add_cascade(label="開く", menu=open_menu)
    open_menu.add_command(label="ファイルを開く", command=lambda: open_file(form))
    open_menu.add_command(label="動画を開く", command=form.select_video)
    menu.add_command(label="新規作成", command=lambda: new_file(form))
    menu.add_separator()
    menu.add_command(label="終了", command=form.quit)

    menu.post(event.x_root, event.y_root)