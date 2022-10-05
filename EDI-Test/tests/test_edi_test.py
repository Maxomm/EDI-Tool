import cv2
from src.edi_test.new_main import EmotionController, resource_path


def test_emotion():
    emo_controller = EmotionController()
    test_img = cv2.imread(resource_path("EDI-Test/src/edi_test/files/angry_test.jpg"))
    emotion = emo_controller.get_emotion_from_image(test_img)
    print(emotion)
    assert emotion == "Angry"
