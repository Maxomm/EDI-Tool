import tkinter as tk

import cv2
from PIL import Image, ImageTk


class GUI:
    def __init__(self, master=None):
        self.master = master
        self.master.title("Webcam feed")
        self.master.geometry("800x600")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.label = tk.Label(master)
        self.label.pack()
        self.running = True

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
