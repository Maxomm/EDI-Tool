import os
import socket
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox

import cv2
import numpy as np
from keras import models

# from keras import Sequential, models
# from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from PIL import Image, ImageTk

PORT = 12345
HOST = "127.0.0.1"
SEND_RATE = 1


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        relative_path = relative_path.split("/")[-1]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def time_milliseconds():
    return round(time.time() * 1000)


class EmotionController:
    def __init__(self):
        self.emotion_model = self.load_emotion_model()
        self.facecasc = cv2.CascadeClassifier(
            resource_path(
                "EDI-Test/src/edi_test/files/haarcascade_frontalface_default.xml"
            )
        )

    emotion_dict = {
        None: "Not Detected",
        0: "Angry",
        1: "Disgusted",
        2: "Fearful",
        3: "Happy",
        4: "Neutral",
        5: "Sad",
        6: "Surprised",
    }

    @staticmethod
    def load_emotion_model():
        path = resource_path("EDI-Test/src/edi_test/files/model_new.h5")
        model = models.load_model(path)
        img = np.zeros((48, 48, 48), np.float32)
        model.predict(img)
        return model

    def get_emotion_from_image(self, image):
        img_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.facecasc.detectMultiScale(
            img_grey, scaleFactor=1.3, minNeighbors=5
        )
        maxindex = -1

        for (x, y, w, h) in faces:
            # Frame um Gesicht
            cv2.rectangle(img_grey, (x, y - 50), (x + w, y + h + 10), (255, 0, 0), 2)
            roi_gray = img_grey[y : y + h, x : x + w]
            cropped_img = np.expand_dims(
                np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0
            )
            prediction = self.emotion_model.predict(cropped_img)
            maxindex = int(np.argmax(prediction))
            # self.current_emotion = str(self.emotion_dict.get(maxindex))
        return str(self.emotion_dict.get(maxindex))

    def get_face_image(self, image, current_emo):
        img_color = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = self.facecasc.detectMultiScale(
            img_color, scaleFactor=1.3, minNeighbors=5
        )
        for (x, y, w, h) in faces:
            img_color = cv2.rectangle(
                img_color, (x, y), (x + w, y + h), (255, 255, 255), 2
            )
            img_color = cv2.putText(
                img_color,
                current_emo,
                (x, y - 10),
                cv2.FONT_HERSHEY_DUPLEX,
                0.7,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
        # img1 = cv2.resize(img1, (300, 200), interpolation=cv2.INTER_LINEAR)
        return img_color


class EDITool:
    def __init__(self):
        self.running = True
        self.cam_index = 0
        self.cap = cv2.VideoCapture(0)
        self.port = PORT
        self.host = HOST
        self.current_emotion = "NONE"
        self.emotion_controller = EmotionController()
        self.root = tk.Tk(className="EDI Tool")
        self.root.title("EDI Tool")
        self.allow_not_detected = tk.IntVar()
        self.check_rate = tk.IntVar()
        self.check_rate.set(10)
        self.send_rate = tk.IntVar()
        self.send_rate.set(10)
        self.img_frame = tk.Label(self.root, bg="black")
        self.settings = None
        self.server_socket = None
        self.connected_label = None
        self.emo_text = None

    def app(self):
        self.root.geometry("645x570")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.pre_settings()
        self.root.lift()
        self.root.focus_force()
        self.menu()
        self.img_frame.grid(row=0, column=0, columnspan=4)
        self.emotion_interface(1, 0)
        self.server_interface(4, 0)

    def get_checkrate(self):
        return max(1, self.check_rate.get() * 100)

    def close_toplevel(self):
        self.settings.destroy()
        self.root.focus()

    def pre_settings(self):
        self.settings = tk.Toplevel(self.root, height=200, width=200)
        img_preview = tk.Label(self.settings, bg="black")
        input_field = tk.Spinbox(self.settings, from_=0, to=9)
        self.settings.attributes("-topmost", "true")
        self.settings.title("Camera Settings")
        tk.Label(self.settings, width=20, text="Camera index").pack()
        input_field.pack()
        tk.Button(
            self.settings,
            text="Change",
            command=lambda: self.change_cam(input_field, img_preview),
        ).pack()
        # img1 = cv2.resize(img1, (300, 200), interpolation=cv2.INTER_LINEAR)

        img_preview.pack()
        ok_button = tk.Button(
            self.settings, text="Confirm", command=self.close_toplevel
        )
        ok_button.pack()
        self.start_camera_stream(img_preview)

    def update_current_emotion(self, img):
        current_emo = self.emotion_controller.get_emotion_from_image(img)
        if self.allow_not_detected.get() == 0 and current_emo == "None":
            return
        self.current_emotion = current_emo

    def change_cam(self, input_field, img_preview):
        self.cap.release()
        self.cam_index = int(input_field.get())
        self.cap = cv2.VideoCapture(self.cam_index)
        self.start_camera_stream(img_preview)

    def init_server(self):
        serveradress = (self.host, int(self.port))
        if threading.active_count() > 1:
            self.server_socket.close()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(serveradress)
        thread = threading.Thread(target=self.start_server)
        thread.daemon = True
        thread.start()

    def get_cam_image(self):
        return self.cap.read()[1]

    def start_server(self):
        self.server_socket.listen()
        connected = True
        while connected:
            try:
                (client_socket, addr) = self.server_socket.accept()
                thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, addr)
                )
                thread.daemon = True
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")
            except socket.error:
                print("Closing Socket")
                connected = False

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION {addr} connected.")
        connected = True

        while connected:
            try:
                message = str(self.current_emotion).encode("UTF-8")
                conn.send(message)
            except socket.error:
                conn.close()
                connected = False
            time.sleep(SEND_RATE)

    def start_camera_stream(self, img_preview):
        while self.settings.winfo_exists() == 1:
            ref, image = self.cap.read()
            if ref:
                img1 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                img1 = cv2.resize(img1, (266, 200), interpolation=cv2.INTER_LINEAR)
                img = ImageTk.PhotoImage(Image.fromarray(img1))
                img_preview.config(image=img)
            self.settings.update()

    def is_running(self):
        return self.running

    def on_closing(self):
        self.cap.release()
        print("closing")
        self.running = False

    def menu(self):
        menubar = tk.Menu(self.root)
        file = tk.Menu(menubar)
        about = tk.Menu(menubar)
        settings = tk.Menu(menubar)
        about.add_command(label="About", command=self.show_about)
        file.add_command(label="Quit", command=self.on_closing)
        settings.add_command(label="Emotion Settings", command=self.emotion_settings)
        settings.add_command(label="Server Settings", command=self.server_settings)
        menubar.add_cascade(label="File", menu=file)
        menubar.add_cascade(label="Settings", menu=settings)
        menubar.add_cascade(label="Help", menu=about)
        self.root.config(menu=menubar)

    def server_interface(self, r, c):
        server_label = tk.Label(self.root, text="Connected Clients:")
        server_label.grid(row=r, column=c, sticky="w")
        self.connected_label = tk.Label(self.root, text=" ")
        self.connected_label.grid(row=r, column=c + 1, sticky="w")
        server_settings = tk.Button(
            self.root, text="Server Settings", command=self.server_settings, width=20
        )
        server_settings.grid(row=r, column=c + 3, sticky="e")

    def set_connected_label(self):
        if threading.active_count() > 1:
            text = f"Online ({threading.activeCount() - 2})"
        else:
            text = "Offline"
        self.connected_label.config(text=text)

    def emotion_settings(self):
        emotion_window = tk.Toplevel(self.root, height=200, width=200)
        emotion_window.attributes("-topmost", "true")
        emotion_window.title("Emotion Settings")
        rate_label = tk.Label(emotion_window, text="Check Rate in 100 ms:")
        nd_label = tk.Label(emotion_window, text="Allow 'Not Detected':")
        rate_label.grid(row=1, column=0, sticky="w")
        nd_label.grid(row=2, column=0, sticky="w")
        rate_spinbox = tk.Spinbox(
            emotion_window,
            textvariable=self.check_rate,
            from_=1,
            to=99,
            state="readonly",
        )
        not_detected_checkbox = tk.Checkbutton(
            emotion_window,
            variable=self.allow_not_detected,
            onvalue=True,
            offvalue=False,
        )
        rate_spinbox.grid(row=1, column=1, sticky="w")
        not_detected_checkbox.grid(row=2, column=1, sticky="w")

    def update_image(self, face):
        img_color = self.emotion_controller.get_face_image(face, self.current_emotion)
        img_set = ImageTk.PhotoImage(Image.fromarray(img_color))
        self.img_frame.config(image=img_set)
        self.root.update()

    @staticmethod
    def change_send_rate(send_rate_spin):
        global SEND_RATE
        SEND_RATE = float(send_rate_spin.get()) / 10

    def server_settings(self):
        server_window = tk.Toplevel(self.root, height=200, width=200)
        server_window.attributes("-topmost", "true")
        server_window.title("Server Settings")
        host_label = tk.Label(server_window, text="Host")
        port_label = tk.Label(server_window, text="Port")
        host_label.grid(row=0, column=0, sticky="w")
        port_label.grid(row=1, column=0, sticky="w")
        host_entry = tk.Entry(server_window)
        port_entry = tk.Entry(server_window)
        host_entry.insert(0, self.host)
        port_entry.insert(0, str(self.port))
        host_entry.grid(row=0, column=1, sticky="w")
        port_entry.grid(row=1, column=1, sticky="w")
        send_rate_label = tk.Label(server_window, text="Send rate in 100ms:")
        send_rate_label.grid(row=3, column=0, sticky="w")
        send_rate_spin = tk.Spinbox(
            server_window,
            textvariable=self.send_rate,
            from_=1,
            to=99,
            command=lambda: self.change_send_rate(send_rate_spin),
            state="readonly",
        )
        send_rate_spin.grid(row=3, column=1, sticky="w")
        restart_button = tk.Button(
            server_window,
            text="Restart",
            command=lambda: self.restart_server(host_entry, port_entry),
        )
        restart_button.grid(row=4, column=0, columnspan=2)

    def restart_server(self, host_entry, port_entry):
        self.host = host_entry.get()
        self.port = port_entry.get()
        edi.init_server()
        print("RESTARTING SERVER", self.host, self.port)

    def emotion_interface(self, r, c):
        emo_label = tk.Label(self.root, text="Current Emotion:")
        emo_label.grid(row=r, column=c, sticky="w")
        self.emo_text = tk.Label(self.root, text="Loading...")
        self.emo_text.grid(row=r, column=c + 1, sticky="w")
        emotion_settings = tk.Button(
            self.root, text="Emotion Settings", command=self.emotion_settings, width=20
        )
        emotion_settings.grid(row=r, column=c + 3, sticky="e")

    def update_emo_label(self):
        self.emo_text.config(text=self.current_emotion)

    @staticmethod
    def show_about():
        messagebox.showinfo(
            "EDI Tool",
            "This tool was created by Maximilian Warsinke"
            " to use emotions as input for other application."
            "\n\nhttps://github.com/Maxomm/EDI_Tool",
        )


if __name__ == "__main__":
    edi = EDITool()
    edi.app()
    start_time = time_milliseconds()
    while edi.is_running():
        try:
            edi.set_connected_label()
            cam_img = edi.get_cam_image()
            if time_milliseconds() - start_time >= edi.get_checkrate():
                edi.update_current_emotion(cam_img)
                edi.update_emo_label()
                start_time = time_milliseconds()
            edi.update_image(cam_img)
        except KeyboardInterrupt:
            break
    edi.cap.release()
