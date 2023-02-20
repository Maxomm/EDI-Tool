import tkinter as tk

import cv2
from emotion_classifier import emotion_dict
from PIL import Image, ImageTk


class GUI:
    def __init__(self, master=None, camera=None):
        self.master = master
        self.show_image = True
        self.bold_font = ("Arial", 10, "bold")
        self.master.title("Webcam feed")
        self.master.geometry("654x600")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.master.resizable(0, 0)
        self.master.config(menu=self.menu())
        # create the image label
        self.label = tk.Label(master)
        self.label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # create a frame to contain the labels and button
        self.frame = tk.Frame(master)
        self.frame.grid(row=1, column=0, sticky="w", padx=20, pady=5)

        # create the labels
        tk.Label(self.frame, text="Camera:",font=self.bold_font).grid(row=0, column=0, sticky="w")
        tk.Label(self.frame, text="Emotion:",font=self.bold_font).grid(row=1, column=0, sticky="w")
        tk.Label(self.frame, text="Server:",font=self.bold_font).grid(row=2, column=0, sticky="w")
        self.label_cam = tk.Label(self.frame, text="0")
        self.label_cam.grid(row=0, column=1, sticky="w")
        self.label_emotion = tk.Label(self.frame, text="label_emotion")
        self.label_emotion.grid(row=1, column=1, sticky="w")
        self.label_server = tk.Label(self.frame, text="offline")
        self.label_server.grid(row=2, column=1, sticky="w")

        self.frame_frequency = 5
        self.running = True
        self.camera = camera
        self.timespan = 5
        self.threshold = 0.5
        self.probability_list = []
        self.enable_camera = tk.IntVar(value=1)

    def open_settings(self):
        self.toplevel = tk.Toplevel(self.master)
        self.toplevel.title("Settings")
        self.init_camera_settings()
        self.init_emotion_settings()
        self.toplevel.update()

    def init_camera_settings(self):

        camera_settings = tk.Frame(self.toplevel, padx=30, pady=15)
        camera_settings.pack()
        title = tk.Label(camera_settings, text="Camera Settings", font=self.bold_font)
        title.grid(row=0, column=0, sticky="w")

        tk.Label(camera_settings, text="Frame Frequency").grid(
            row=1, column=0, sticky="w"
        )
        self.spinbox_frequency = tk.Spinbox(
            camera_settings, from_=1, to=30, width=5, command=self.set_frame_frequency
        )
        self.spinbox_frequency.grid(row=1, column=1, sticky="w")
        self.spinbox_frequency.delete(0, "end")
        self.spinbox_frequency.insert(0, self.frame_frequency)

        tk.Label(camera_settings, text="Camera Input").grid(row=2, column=0, sticky="w")
        self.spinbox_camera = tk.Spinbox(
            camera_settings, from_=0, to=5, width=5, command=self.switch_camera
        )
        self.spinbox_camera.grid(row=2, column=1, sticky="w")
        self.spinbox_camera.delete(0, "end")
        self.spinbox_camera.insert(0, "0")

    def init_emotion_settings(self):
        emotion_settings = tk.Frame(self.toplevel, padx=30, pady=15)
        emotion_settings.pack()
        title = tk.Label(emotion_settings, text="Emotion Settings", font=self.bold_font)
        title.grid(row=0, column=0, sticky="w")
        tk.Label(emotion_settings, text="Timespan").grid(row=1, column=0, sticky="w")
        self.spinbox_timespan = tk.Spinbox(
            emotion_settings, from_=1, to=20, width=5, command=self.change_timespan
        )
        self.spinbox_timespan.grid(row=1, column=1, sticky="w")
        self.spinbox_timespan.delete(0, "end")
        self.spinbox_timespan.insert(0, self.timespan)
        tk.Label(emotion_settings, text="Threshold").grid(row=2, column=0, sticky="w")
        self.spinbox_threshold = tk.Spinbox(
            emotion_settings,
            from_=0.1,
            to=1.0,
            width=5,
            increment=0.1,
            command=self.change_threshold,
        )
        self.spinbox_threshold.grid(row=2, column=1, sticky="w")
        self.spinbox_threshold.delete(0, "end")
        self.spinbox_threshold.insert(0, self.threshold)

    def menu(self):
        menubar = tk.Menu(self.master)
        file = tk.Menu(menubar)
        about = tk.Menu(menubar)
        settings = tk.Menu(menubar)
        about.add_command(label="About", command=self.test_button)
        file.add_command(label="Quit", command=self.on_closing)
        settings.add_command(label="Settings", command=self.open_settings)
        menubar.add_cascade(label="File", menu=file)
        menubar.add_cascade(label="Settings", menu=settings)
        menubar.add_cascade(label="Help", menu=about)
        return menubar

    def test_button(self):
        print("button clicked")

    def get_enable_camera(self):
        return self.enable_camera.get()

    def get_threshold(self):
        return self.threshold

    def change_threshold(self):
        self.threshold = float(self.spinbox_threshold.get())

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
