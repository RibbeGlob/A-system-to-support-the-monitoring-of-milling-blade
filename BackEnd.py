import os
import paramiko
import PySimpleGUI as sg
import time
import JSON.JSONscrypt as jsc
from PIL import Image
import socket


def resizeImage():
    # Ścieżka do folderu "icon" z dopiskiem "_icon" w nazwie
    input_folder = r"C:\Users\gerfr\OneDrive\Pulpit\x\pop"
    output_folder = os.path.join(os.path.dirname(input_folder), os.path.basename(input_folder) + "_icon")
    # Sprawdź, czy folder "icon" istnieje i jeśli nie, to go utwórz
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Utwórz listę plików w folderze "icon"
    existing_icon_files = os.listdir(output_folder)
    # Przechodź przez pliki w folderze wejściowym
    for filename in os.listdir(input_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            # Sprawdź, czy plik już istnieje w folderze "icon"
            if filename not in existing_icon_files:
                # Otwórz obraz
                with Image.open(input_path) as img:
                    width, height = img.size
                    new_width = 24
                    new_height = 24
                    resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)
                    resized_img.save(output_path)



class ChangeJPGtoPNG:
    def __init__(self, path):
        self.path = path

    def folderMethod(self):
        # Konwersja jpg na png
        for filename in os.listdir(self.path):
            if filename.endswith(".jpg"):
                jpg_path = os.path.join(self.path, filename)
                png_path = os.path.splitext(jpg_path)[0] + ".png"
                try:
                    jpg_image = Image.open(jpg_path)
                    jpg_image.save(png_path, "PNG")
                    jpg_image.close()
                    os.remove(jpg_path)
                except Exception as e:
                    print(f"Błąd podczas konwersji i usuwania pliku {jpg_path}: {e}")


# Funkcja tworząca folder na komputerze
def createFolder(folderName):
    try:
        os.mkdir(folderName)
    except FileExistsError:
        pass
    except Exception as e:
        sg.popup_error(e)


# Połączenie socket
class Connection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client_socket = None

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.ip, self.port))
            return True
        except Exception as e:
            sg.popup_error(f"Błąd połączenia {e}")


# Działanie na sockecie
class Sending(Connection):
    def __init__(self, ip, port):
        super().__init__(ip, port)

    def send_command(self, command):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.ip, self.port))
                client_socket.sendall(f"CMD:{command}".encode())
                while True:
                    data = client_socket.recv(1024)
                    print(data)
                    if data == b"File received":
                        break
        except Exception as e:
            sg.popup_error(e)

    def send_file(self, file_path):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.ip, self.port))
                file_name = os.path.basename(file_path)
                client_socket.sendall(f"FILE:{file_name}".encode())
                with open(file_path, 'rb') as file:
                    print(f"Opening file: {file_path}")
                    client_socket.sendfile(file)
                client_socket.sendall(b"ENDOLO")
                while True:
                    data = client_socket.recv(1024)
                    print(data)
                    if data == b"File received":
                        break

        except Exception as e:
            sg.popup_error(e)


    def receive_image(self, here, ilosc, filename, kolor):
        import shutil
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.ip, self.port))
            for i in range(ilosc):
                remote_filename = filename+f'/{kolor}_zdjecie_{i+1}.png'
                local_filename = f"{here}/{kolor}_zdjecie_{i+1}.png"
                client_socket.sendall(f"GET_FILE:{remote_filename}".encode())

                received_data = b''
                while True:
                    data = client_socket.recv(1024)
                    if data == b'puste':

                        break
                    else:
                        with open(local_filename, 'wb') as file:
                            received_data += data
                            end_mark = received_data.find(b'koniecpliku')

                            if end_mark != -1:
                                print('jesteeeem')
                                file.write(received_data[:end_mark])
                                received_data = received_data[end_mark + len(b'koniecpliku'):]
                                file.flush()
                                break
                print(f'xd{i}')



# Wybranie koloru oraz automatyczny kontrast
def changingNameToRGB(kolor):
    kolory = {
        "Czarny": [255, 0, 0],
        "Cyjan": [0, 255, 0],
        "Magenta": [0, 0, 255],
        "Żółty": [255, 255, 255],
        "Niebieski": [255, 255, 0],
        "Czerwony": [0, 255, 255]
    }
    return kolory.get(kolor, [255, 255, 255])