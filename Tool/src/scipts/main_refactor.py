import tkinter as tk

from camera import CameraController
from emotion_classifier import EmotionClassifier
from gui import GUI


def most_frequent(in_list):
    item = max(set(in_list), key=in_list.count)
    count = in_list.count(item)
    return item, count


if __name__ == "__main__":
    emo = EmotionClassifier()
    root = tk.Tk()
    frame_counter = 0
    emotion_list = []
    list_size = 10
    with CameraController() as camera_controller:
        interface = GUI(root, camera_controller)
        emotion_string = "NONE"
        while interface.is_running():
            frame = camera_controller.get_frame()
            frame, face = emo.face_from_image(frame)
            if face is not None:
                frame_counter += 1
                if frame_counter % interface.get_frame_frequency() == 0:
                    emotion_string, _ = emo.emotion_from_face(face)
                    frame_counter = 0
                    emotion_list.append(emotion_string)

                    interface.update_probabilities(emotion_list)
                    freq_emotion, probability = most_frequent(emotion_list)
                    interface.update_emotion(freq_emotion)

                    # reduce list
                    emo_length = len(emotion_list)
                    timespan = interface.get_timespan()
                    if emo_length >= timespan:
                        emotion_list = emotion_list[emo_length - timespan + 1 :]
                # frame = emo.add_emotion_text(frame, emotion_string)
            interface.update_frame(frame)
            root.update()
