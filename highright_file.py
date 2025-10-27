import tkinter as tk

def clear_AllvideoHighlights(form):
    """全ての動画のハイライトをリセットする"""
    for info in form.all_videos.values():
        info['label'].config(bd=0, relief=tk.FLAT)
        info['label'].config(highlightbackground="#2C2C2C", highlightcolor="#2C2C2C", highlightthickness=0)

def clear_AvideoHighlight(form, label):
    """特定の動画のハイライトをリセットする"""
    label.config(bd=0, relief=tk.FLAT)
    label.config(highlightbackground="#2C2C2C", highlightcolor="#2C2C2C", highlightthickness=0)

def set_VideoHighlight(form, label):
    """選択された動画に枠線を適用する"""
    label.config(bd=2, relief=tk.RAISED, highlightbackground="#5FB7FF", highlightcolor="#5FB7FF", highlightthickness=2)
