import tkinter as tk

from camera import CameraController
from emotion_classifier import EmotionClassifier
from gui import GUI

if __name__ == "__main__":
    emo = EmotionClassifier()
    root = tk.Tk()
    interface = GUI(root)
    with CameraController() as camera_controller:
        while interface.is_running():
            # camera
            frame = camera_controller.get_frame()
            # emotion
            print(emo.emotion_from_image(frame))
            # interface
            interface.update_frame(frame)
            root.update()
