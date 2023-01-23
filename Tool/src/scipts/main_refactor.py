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
        emotion_string = "NONE"
        while interface.is_running():
            frame = camera_controller.get_frame()
            frame, face = emo.face_from_image(frame)
            if face is not None:
                frame_counter += 1
                # frame = emo.add_emotion_text(frame, emotion_string)
                if frame_counter % interface.get_frame_frequency() == 0:
                    emotion_string, probability = emo.emotion_from_face(face)
                    frame_counter = 0
                    print(emotion_string, probability)

            interface.update_frame(frame)
            root.update()
