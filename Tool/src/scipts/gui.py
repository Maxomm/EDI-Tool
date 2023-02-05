import tkinter as tk

import cv2
from emotion_classifier import emotion_dict
from PIL import Image, ImageTk


class GUI:
    def __init__(self, master=None, camera=None):
        self.master = master
        self.show_image = False
        self.master.title("Webcam feed")
        self.master.geometry("800x600")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.label = tk.Label(master)
        self.label.grid(row=0, column=0, rowspan=7)
        self.frame_frequency = 10
        self.running = True
        self.camera = camera
        self.timespan = 10

        self.label_emotion = tk.Label(master, text="placeholder")
        self.label_emotion.grid(row=11, column=0)

        self.probability_list = []

        for i, emotion_text in enumerate(emotion_dict.values()):
            tk.Label(master, text=emotion_text).grid(row=0 + i, column=1)

            new_label = tk.Label(master, text="0%")
            new_label.grid(row=0 + i, column=2)
            self.probability_list.append(new_label)

        self._init_spinboxes()

    def _init_spinboxes(self):
        self.spinbox_frequency = tk.Spinbox(
            self.master, from_=1, to=30, width=5, command=self.set_frame_frequency
        )
        self.spinbox_frequency.grid(row=8, column=0)
        self.spinbox_frequency.delete(0, "end")
        self.spinbox_frequency.insert(0, self.frame_frequency)
        self.spinbox_camera = tk.Spinbox(
            self.master, from_=0, to=5, width=5, command=self.switch_camera
        )
        self.spinbox_camera.grid(row=9, column=0)
        self.spinbox_camera.delete(0, "end")
        self.spinbox_camera.insert(0, "0")

        self.spinbox_timespan = tk.Spinbox(
            self.master, from_=1, to=20, width=5, command=self.change_timespan
        )
        self.spinbox_timespan.grid(row=10, column=0)
        self.spinbox_timespan.delete(0, "end")
        self.spinbox_timespan.insert(0, self.timespan)

    def change_timespan(self):
        self.timespan = int(self.spinbox_timespan.get())

    def get_show_image(self):
        return self.show_image

    def get_timespan(self):
        return self.timespan

    def update_emotion(self, emotion_string):
        text = f"{emotion_string}"
        self.label_emotion.config(text=text)

    def update_probabilities(self, in_list):
        for i, prob_label in enumerate(self.probability_list):
            percent = round(in_list.count(emotion_dict[i]) / len(in_list) * 100)
            prob_label.config(text=str(percent) + "%")

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
        self.frame_frequency = int(self.spinbox_frequency.get())

    def get_frame_frequency(self):
        return self.frame_frequency

    def switch_camera(self):
        new_value = self.spinbox_camera.get()
        self.camera.switch_camera(int(new_value))
