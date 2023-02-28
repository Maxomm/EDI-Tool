import cv2


class CameraController:
    def __init__(self, source=0):
        # Create a VideoCapture object
        self.capture = cv2.VideoCapture(source)
        self.source = source

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

    def get_source(self):
        return self.source

    def switch_camera(self, source):
        # Open the new camera source
        self.capture.open(source)

        # Check if the new source is valid
        if self.capture.isOpened():
            self.source = source
            print("Camera switched to:", source)
        else:
            print("Invalid camera source:", source)
