import socket
import threading
import time


class EmotionServer:
    def __init__(self, host, port):
        self.emo = "Not set"
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        print(f"Started server {self.host}:{self.port}")

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
            except socket.error:
                print("Closing socket")
                break

    def set_emotion(self, in_emotion):
        self.emo = in_emotion

    def handle_client(self, conn, addr):
        print(f"New connection: {addr}")
        connected = True
        last_message = " "
        while connected:
            try:
                message = self.emo.encode("UTF-8")
                if last_message != message:
                    conn.send(message)
                    print(f"Sending {message}")
                    last_message = message
            except socket.error:
                conn.close()
                connected = False
            time.sleep(0.1)

    def restart_server(self, new_host, new_port):
        print("Stopping server...")
        self.server_socket.close()
        print("starting",new_host,new_port)
        self.__init__(new_host, int(new_port))
