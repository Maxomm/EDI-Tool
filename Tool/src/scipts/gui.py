import tkinter as tk

import cv2
from PIL import Image, ImageTk


class GUI:
    def __init__(self, master=None, camera=None):
        self.master = master
        self.master.title("Webcam feed")
        self.master.geometry("800x600")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.label = tk.Label(master)
        self.label.pack()
        self.frame_frequency = 10
        self.running = True
        self.camera = camera
        self.spinbox = tk.Spinbox(
            master, from_=1, to=30, width=5, command=self.set_frame_frequency
        )
        self.spinbox.pack()
        self.spinbox.delete(0, "end")
        self.spinbox.insert(0, self.frame_frequency)
        self.spinbox_camera = tk.Spinbox(
            master, from_=0, to=1, width=5, command=self.switch_camera
        )
        self.spinbox_camera.pack()
        self.spinbox_camera.delete(0, "end")
        self.spinbox_camera.insert(0, "0")
        self.label_emotion = tk.Label(master, text="", font=("Helvetica", 24))
        self.label_emotion.pack()

    def update_emotion(self, emotion_string, probability):
        text = f"{emotion_string} - {round(probability*100)}%"
        self.label_emotion.config(text=text)

    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(image=img)
        self.label.config(image=img)
        self.label.image = img

    def on_closing(self):
        self.running = False
        self.master.destroy()

    def is_running(self):
        return self.running

    def set_frame_frequency(self):
        new_value = self.spinbox.get()
        self.frame_frequency = int(new_value)

    def get_frame_frequency(self):
        return self.frame_frequency

    def switch_camera(self):
        new_value = self.spinbox_camera.get()
        self.camera.switch_camera(int(new_value))
