import cv2


class CameraController:
    def __init__(self, source=0):
        # Create a VideoCapture object
        self.capture = cv2.VideoCapture(source)

        # Check if the video source is available
        if not self.capture.isOpened():
            raise ValueError("Unable to open video source", source)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Release the video source and destroy all windows
        self.capture.release()
        cv2.destroyAllWindows()

    def get_frame(self):
        # Grab a frame from the video source
        success, frame = self.capture.read()

        # Return the frame if it was successfully grabbed
        if success:
            return frame
        return None
