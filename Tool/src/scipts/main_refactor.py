import tkinter as tk

from camera import CameraController
from emotion_classifier import EmotionClassifier
from gui import GUI

if __name__ == "__main__":
    emo = EmotionClassifier()
    root = tk.Tk()
    frame_counter = 0
    with CameraController() as camera_controller:
        interface = GUI(root, camera_controller)
        while interface.is_running():
            # camera
            frame = camera_controller.get_frame()
            frame_counter += 1
            # emotion
            if frame_counter % interface.get_frame_frequency() == 0:
                print(emo.emotion_from_image(frame))
                frame_counter = 0
            # interface
            interface.update_frame(frame)
            root.update()
