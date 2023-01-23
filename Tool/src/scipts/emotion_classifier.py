import os
import sys

import cv2
import numpy as np
from keras import models

emotion_dict = {
    None: "None",
    0: "Angry",
    1: "Disgusted",
    2: "Fearful",
    3: "Happy",
    4: "Neutral",
    5: "Sad",
    6: "Surprised",
}


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        relative_path = relative_path.split("/")[-1]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class EmotionClassifier:
    def __init__(self) -> None:
        self.emomodel = models.load_model(resource_path("Tool/src/model_new.h5"))
        self.facecasc = cv2.CascadeClassifier(resource_path("Tool/src/haarcascade.xml"))

    def emotion_from_face(self, image):
        prediction = self.emomodel.predict(image)[0]
        probabilty = max(prediction)
        maxindex = int(np.argmax(prediction))
        emotion = emotion_dict.get(maxindex)
        return emotion, probabilty

    def face_from_image(self, image):
        cropped_img = None
        img_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.facecasc.detectMultiScale(
            img_grey, scaleFactor=1.3, minNeighbors=5
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y - 50), (x + w, y + h + 10), (255, 0, 0), 2)
            roi_gray = img_grey[y : y + h, x : x + w]
            cropped_img = np.expand_dims(
                np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0
            )
            break

        return image, cropped_img

    def add_emotion_text(self, image, emotion_text):
        cv2.putText(
            image, emotion_text, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2
        )
        return image
