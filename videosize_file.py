import cv2
import tkinter as tk
from PIL import Image, ImageTk

class VideoResize:
    @staticmethod
    def update_video_frame(form, label):
        """動画フレームのサイズを更新する"""
        for file_path, info in form.video_info.items():
            if info['label'] == label:
                frame = info.get('last_frame')
                if frame is not None:
                    # フレームのサイズ取得
                    frame_height, frame_width = frame.shape[:2]
                    aspect_ratio = frame_height / frame_width

                    # ラベルの幅を取得し、高さをアスペクト比で計算
                    new_width = max(50, int(label.winfo_width()))
                    new_height = max(50, int(new_width * aspect_ratio))

                    # フレームをリサイズ
                    resized_frame = cv2.resize(frame, (new_width, new_height))

                    # BGR→RGB変換してPILイメージ化
                    frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img_tk = ImageTk.PhotoImage(img)

                    # ラベルに画像を表示
                    label.after(1, lambda: form.update_label_image(label, img_tk))

    @staticmethod
    def resize_start(form, event):
        """サイズ変更の開始"""
        # ドラッグ開始時のマウス位置と現在の動画サイズを保存
        form.resize_info = {
            'x': event.x_root,
            'y': event.y_root,
            'width': event.widget.winfo_width(),
            'height': event.widget.winfo_height()
        }    

    @staticmethod
    def resize_video(form, event):
        """アスペクト比を維持して動画のサイズ変更"""
        if form.resize_info and form.selected_label:
            dx = event.x_root - form.resize_info['x']
            #元のアスペクト比を取得
            aspect_ratio = form.resize_info['height'] / form.resize_info['width']
            #新しい幅と高さを計算
            new_width = max(50, form.resize_info['width'] + dx)
            new_height = int(new_width * aspect_ratio)

            # 最小サイズを設定
            if new_width > 50 and new_height > 50:
                form.selected_label.config(width=new_width, height=new_height)
        VideoResize.update_video_frame(form, form.selected_label)

    @staticmethod
    def resize_end(form, event):
        """サイズ変更の終了"""
        form.resize_info = None