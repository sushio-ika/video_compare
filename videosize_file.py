import cv2
import tkinter as tk
from PIL import Image, ImageTk

def update_video_frame(form, label):
    """動画フレームのサイズを更新する"""
    for file_path, info in form.video_info.items():
        if info['label'] == label:
            capture = form.video_captures[file_path]
            if capture.isOpened():
                # 現在のフレームを取得してリサイズ
                ret, frame = capture.read()
                if ret:
                    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    
                    aspect_ratio = frame_height / frame_width
                    new_width = label.winfo_width()
                    new_height = int(new_width * aspect_ratio)

                    resized_frame = cv2.resize(frame, (new_width, new_height))
                        
                    frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img_tk = ImageTk.PhotoImage(img)
                        
                    label.after(1, lambda: form.update_label_image(label, img_tk))
                            
def resize_start(form, event):
    """サイズ変更の開始"""
    # ドラッグ開始時のマウス位置と現在の動画サイズを保存
    form.resize_info = {
        'x': event.x_root,
        'y': event.y_root,
        'width': event.widget.winfo_width(),
        'height': event.widget.winfo_height()
    }    

def resize_video(form, event):
    """動画のサイズ変更"""
    if form.resize_info:
        dx = event.x_root - form.resize_info['x']
        dy = event.y_root - form.resize_info['y']

        new_width = form.resize_info['width'] + dx
        new_height = form.resize_info['height'] + dy

        # 最小サイズを設定
        if new_width > 50 and new_height > 50:
            form.selected_label.config(width=new_width, height=new_height)
            update_video_frame(form, form.selected_label) # 動画フレームを更新

def resize_end(form, event):
    """サイズ変更の終了"""
    form.resize_info = None