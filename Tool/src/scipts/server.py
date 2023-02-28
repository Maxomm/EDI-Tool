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
        self.client_threads = []
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.stop_flag = threading.Event()
        self.client_handler_stop_flag = threading.Event()
        self.server_thread.start()
        
        print(f"Started server {self.host}:{self.port}")

    def start_server(self):
        self.server_socket.listen()
        while not self.stop_flag.is_set():
            try:
                (client_socket, addr) = self.server_socket.accept()
                thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, addr)
                )
                thread.daemon = True
                thread.start()
                self.client_threads.append(thread)
            except socket.error:
                print("Socket exception")
                break
        print("Closing socket")

    def get_host(self):
        return self.host
    
    def get_port(self):
        return self.port

    def get_server_adress(self):
        return f"Online {self.host} : {self.port}"

    def set_emotion(self, in_emotion):
        self.emo = in_emotion

    def handle_client(self, conn, addr):
        print(f"New connection: {addr}")
        last_message = " "
        while not self.client_handler_stop_flag.is_set():
            try:
                message = self.emo.encode("UTF-8")
                if last_message != message:
                    conn.send(message)
                    print(f"Sending {message}")
                    last_message = message
            except socket.error:
                print("Socket exception")
                conn.close()
                break
            time.sleep(0.1)
        print(f"Closing connection: {addr}")
        conn.close()

    def restart_server(self, new_host, new_port):
        print("Stopping server...")
        self.stop_server()
        print("Server stopped")
        print("Starting new server...", new_host, new_port)
        self.__init__(new_host, int(new_port))

    def stop_server(self):
        self.stop_flag.set()
        self.server_socket.close()
        self.client_handler_stop_flag.set()
        for thread in self.client_threads:
            thread.join()
        self.server_thread.join()

