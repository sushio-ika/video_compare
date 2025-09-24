import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage,ttk
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

def on_mousewheel(form, event):
    # 動画がある範囲のみスクロール可能にする
    if form.canvas.winfo_height() < form.canvas.bbox("all")[3]:
        if event.delta > 0:
            form.canvas.yview_scroll(-1, "units")
        else:
            form.canvas.yview_scroll(1, "units")
    form.canvas.yview_moveto(max(0, min(form.canvas.yview()[0], 1)))

def left_click(form, event, ctrl_click):
        """マウスの左クリックを処理する"""
        widget = event.widget
        if widget in [info['label'] for info in form.video_info.values()]:#動画をクリックした場合
            if ctrl_click:#Ctrlキーが押されている場合
                if form.selected_label == widget:#すでに選択されている動画をクリックした場合
                    reset_video_highlight(form, widget)
                    form.selected_label = None
                else:#新たに選択された動画をクリックした場合
                    apply_image_highlight(form, widget)
            else:#Ctrlキーが押されていない場合
                reset_all_highlights(form)
                apply_image_highlight(form, widget)
            form.selected_label = widget  # 現在選択中のラベルを保存

            # サイズ変更イベントをバインド
            # widget.bind("<Button-1>", lambda event: rsz.resize_start(form, event))#左クリックでサイズ変更開始
            # widget.bind("<B1-Motion>", lambda event: rsz.resize_video(form, event))#ドラッグでサイズ変更
            # widget.bind("<ButtonRelease-1>", lambda event: rsz.resize_end(form, event))#左クリックを離したらサイズ変更終了

            form.update_widget(tk.NORMAL)#動画再生コントロールを有効化

        else:#動画以外をクリックした場合
            if widget == form.footer.btn_rewind or widget == form.footer.btn_play_pause or widget == form.footer.btn_skip or widget == form.lbl_timestamp or widget == form.footer.btn_delete:
                return
            else:
                form.update_widget(tk.DISABLED)
                reset_all_highlights(form)
                form.selected_label = None

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
    menu.add_command(label="削除", command=lambda: delete_video(form, widget=form.selected_label))
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