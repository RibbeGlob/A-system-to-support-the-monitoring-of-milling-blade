import os
import PySimpleGUI as sg
from PIL import Image
import socket

def stream(server_ip):
    import cv2
    server_ip = server_ip
    server_port = 8000
    url = f'http://{server_ip}:{server_port}/stream.mjpg'
    cap = cv2.VideoCapture(url)
    layout = [[sg.Image(filename='', key='-IMAGE-')]]
    window = sg.Window('Stream', layout, finalize=True)
    while True:
        event, values = window.read(timeout=0)
        if event == sg.WINDOW_CLOSED:
            break
        ret, frame = cap.read()
        if not ret:
            break
        if frame is not None:
            encoded_image = cv2.imencode('.png', frame)[1].tobytes()
            window['-IMAGE-'].update(data=encoded_image)
    cap.release()
    cv2.destroyAllWindows()
    window.close()


def findIp():
    import subprocess
    try:
        arp_output = subprocess.check_output(['arp', '-a'], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print("Błąd podczas wykonywania polecenia arp -a")
        arp_output = ''
    lines = arp_output.strip().split('\n')
    ip_addresses = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 3 and parts[2].lower() == "dynamic":
            ip_address = parts[0]
            ip_addresses.append(ip_address)
    return ip_addresses


class ChangeJPGtoPNG:
    def __init__(self, path):
        self.path = path

    def folderMethod(self):
        # Konwersja jpg na png
        for filename in os.listdir(self.path):
            if filename.endswith(".jpg"):
                jpgPath = os.path.join(self.path, filename)
                pngPath = os.path.splitext(jpgPath)[0] + ".png"
                try:
                    jpgImage = Image.open(jpgPath)
                    jpgImage.save(pngPath, "PNG")
                    jpgImage.close()
                    os.remove(jpgPath)
                except Exception as e:
                    sg.popup_error(f"Błąd podczas konwersji i usuwania pliku {jpgPath}: {e}")


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
        self.clientSocket = None

    def connect(self):
        try:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSocket.connect((self.ip, self.port))
            return True
        except Exception as e:
            sg.popup_error(f"Błąd połączenia {e}")


# Działanie na sockecie
class Sending(Connection):
    def __init__(self, ip, port):
        super().__init__(ip, port)

    def sendData(self, data, which):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
                clientSocket.connect((self.ip, self.port))
                if which == 1:
                    file_name = os.path.basename(data)
                    clientSocket.sendall(f"FILE:{file_name}".encode())
                    with open(data, 'rb') as file:
                        clientSocket.sendfile(file)
                    clientSocket.sendall(b"END")
                elif which == 2:
                    clientSocket.sendall(f"CMD:{data}".encode())
                while True:
                    data = clientSocket.recv(1024)
                    if data == b"File received":
                        break
        except Exception as e:
            sg.popup_error(e)

    def receiveImage(self, here, range, filename, color):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
            clientSocket.connect((self.ip, self.port))
            for i in range(range):
                remoteFIlename = filename+f'/{color}_zdjecie_{i + 1}.png'
                localFilename = f"{here}/{color}_zdjecie_{i + 1}.png"
                clientSocket.sendall(f"GET_FILE:{remoteFIlename}".encode())
                receivedData = b''
                while True:
                    data = clientSocket.recv(1024)
                    if data == b'empty':
                        break
                    else:
                        with open(localFilename, 'wb') as file:
                            receivedData += data
                            end_mark = receivedData.find(b'endfile')
                            if end_mark != -1:
                                file.write(receivedData[:end_mark])
                                receivedData = receivedData[end_mark + len(b'endfile'):]
                                file.flush()
                                break


# Wybranie koloru oraz automatyczny kontrast
def changingNameToRGB(kolor):
    colors = {
        "Czarny": [255, 0, 0],
        "Cyjan": [0, 255, 0],
        "Magenta": [0, 0, 255],
        "Żółty": [255, 255, 255],
        "Niebieski": [255, 255, 0],
        "Czerwony": [0, 255, 255]
    }
    return colors.get(kolor, [255, 255, 255])