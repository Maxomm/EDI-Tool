import socket
import threading
import time


class EmotionServer:
    def __init__(self, host, port):
        self.emo = "Not set"
        serveradress = (host, int(port))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(serveradress)
        thread = threading.Thread(target=self.start_server)
        thread.daemon = True
        thread.start()
        print("Started server", host, port)

    def start_server(self):
        self.server_socket.listen()
        while True:
            try:
                (client_socket, addr) = self.server_socket.accept()
                thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, addr)
                )
                thread.daemon = True
                thread.start()
                # print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")
            except socket.error:
                print("Closing socket")

    def set_emotion(self, in_emotion):
        self.emo = in_emotion

    def handle_client(self, conn, addr):
        print(f"New connection: {addr} ")
        connected = True
        last_message = " "
        while connected:
            try:
                message = str(self.emo).encode("UTF-8")
                if last_message != message:
                    conn.send(message)
                    print(f"Sending {message}")
                    last_message = message
            except socket.error:
                conn.close()
                connected = False
            time.sleep(0.1)
