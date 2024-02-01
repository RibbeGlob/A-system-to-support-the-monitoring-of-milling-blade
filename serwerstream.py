import io
import socket
import threading
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import sys

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        super().__init__()
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

def client_thread(client_socket, output):
    try:
        picam2 = Picamera2()
        picam2.configure(picam2.create_video_configuration(main={"size": (800,600)}))
        picam2.start_recording(JpegEncoder(), FileOutput(output))

        while True:
            with output.condition:
                output.condition.wait()
                frame = output.frame
                if frame is not None:
                    client_socket.sendall(len(frame).to_bytes(4, byteorder='big'))
                    client_socket.sendall(frame)
    except Exception as e:
        print(f"Exception in client_thread: {e}")
        picam2.stop_recording()
        client_socket.close()
        picam2.close()

    finally:
        picam2.stop_recording()
        client_socket.close()

def server_thread(host, port, output):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Serwer nasłuchuje na {host}:{port}")
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Połączono z {addr}")
            client_thread_handle = threading.Thread(target=client_thread, args=(client_socket, output))
            client_thread_handle.start()

if __name__ == '__main__':
    output = StreamingOutput()
    HOST = '0.0.0.0'
    PORT = 8000

    server_thread_handle = threading.Thread(target=server_thread, args=(HOST, PORT, output))
    server_thread_handle.start()

    try:
        server_thread_handle.join()
    except KeyboardInterrupt:
        print("Zamykanie serwera...")
