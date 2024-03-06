import socket
import subprocess
import os
import psutil
import io
import json
from picamera2 import Picamera2


def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.output.decode()


def send_file(client_socket, file_path):
    with open(file_path, 'rb') as file:
        image = file.read()
        client_socket.sendall(image)


def receive_file(connection, file_name):
    directory = '/home/pi/received_files'
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, file_name)
    response_message = "im"
    with open(file_path, 'wb') as file:
        buffer = b''
        while True:
            data = connection.recv(1024)
            buffer += data
            print(buffer)
            end_marker_index = buffer.find(b'END')
            if end_marker_index != -1:
                file.write(buffer[:end_marker_index])
                buffer = buffer[end_marker_index + len(b'END'):]
                file.flush()
                response_message = "im"
                break
    connection.sendall(b"File received")


def save(requested_file):
    try:
        with open("/home/pi/sendedFile.json", "r") as plik:
            liczby = json.load(plik)
    except (FileNotFoundError, json.JSONDecodeError):
        liczby = []
    if requested_file in liczby:
        print('jest')

        return True
    else:
        liczby.append(requested_file)
        with open("/home/pi/sendedFile.json", "w") as plik:
            json.dump(liczby, plik)
        return False


def main():
    server_ip = '0.0.0.0'
    server_port = 12345
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((server_ip, server_port))
        server_socket.listen(1)
        while True:
            conn, addr = server_socket.accept()
            with conn:
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    elif data.startswith("CMD:"):
                        command = data[4:]
                        execute_command(command)
                        conn.sendall(b"File received")
                    elif data.startswith("FILE:"):
                        # Oczekuj na nazwÄ™ pliku bez Ĺ›cieĹĽki
                        file_name = data[5:]
                        receive_file(conn, file_name)
                    elif data.startswith("GET_FILE:"):
                        requested_file = data[9:]
                        iteracja = data[10]
                        if os.path.exists(requested_file):
                            x = save(requested_file)
                            (send_file(conn, requested_file),
                             conn.sendall(b'koniecpliku')) if x == False else conn.sendall(b'puste')
                        else:
                            pass

if __name__ == '__main__':
    main()