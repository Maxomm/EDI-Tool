import threading
import tkinter as tk

from collections import deque
from camera import CameraController
from emotion_classifier import EmotionClassifier
from emotion_server import EmotionServer
from gui import GUI

PORT = 12345
HOST = "127.0.0.1"


def most_frequent(in_list):
    # Create a set from the list to get unique elements
    unique_elements = set(in_list)
    
    # Use the max function and the count method of the list to determine the most frequent element
    item = max(unique_elements, key=in_list.count)
    count = in_list.count(item)
    
    # Return the most frequent element and its count
    return item, count / len(in_list)



if __name__ == "__main__":

    # Initialize the EmotionClassifier object
    emo = EmotionClassifier()

    # Initialize the GUI object
    root = tk.Tk()

    # Initialize the EmotionServer object
    server = EmotionServer(HOST, PORT)

    def process_frames():
        # Counter to keep track of the number of frames processed
        frame_counter = 0
        
        # Use a camera controller to access the camera
        with CameraController() as camera_controller:
            # Initialize the GUI object
            interface = GUI(root, camera_controller)

            # Initialize a deque to store the emotion strings
            emotion_queue = deque(maxlen=interface.get_timespan())

            # Continuously process frames as long as the GUI is running
            while interface.is_running():
                # Get the next frame from the camera
                frame = camera_controller.get_frame()
                
                # Get the face and emotion from the frame
                frame, face = emo.face_from_image(frame)
                if face is not None:
                    frame_counter += 1
                    
                    # Only process emotions for every nth frame (as specified by frame frequency)
                    if frame_counter % interface.get_frame_frequency() == 0:
                        emotion_string, _ = emo.emotion_from_face(face)
                        frame_counter = 0
                        emotion_queue.append(emotion_string)

                        # Update the probabilities and current emotion in the GUI
                        interface.update_probabilities(emotion_queue)
                        freq_emotion, probability = most_frequent(emotion_queue)
                        interface.update_emotion(freq_emotion)

                        # Set the emotion in the server
                        server.set_emotion(freq_emotion + str(probability * 100))
                        
                        # Reduce the queue if necessary
                        timespan = interface.get_timespan()

                        print(emotion_queue)

                        if len(emotion_queue) != timespan:
                            emotion_queue = deque(emotion_queue, maxlen=timespan)
                
                # Update image with new frame
                interface.update_frame(frame)

    # Start the frame processing function in a separate thread
    frame_thread = threading.Thread(target=process_frames)
    frame_thread.daemon = True
    frame_thread.start()

    # Start the GUI main loop
    root.mainloop()

