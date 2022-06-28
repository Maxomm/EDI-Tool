import cv2
from src.edi_test.new_main import EDITool, resource_path


def test_emotion():
    edi = EDITool()
    test_img = cv2.imread(resource_path("EDI-Test/src/edi_test/files/testpicture.jpg"))
    emotion = edi.set_emotion(test_img)
    print(emotion)
    assert emotion == 2
