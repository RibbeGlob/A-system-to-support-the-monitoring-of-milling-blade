import os
import PySimpleGUI as sg
from PIL import Image
import socket


def resizeImage():
    # Ścieżka do folderu "icon" z dopiskiem "_icon" w nazwie
    inputFolder = r"C:\Users\gerfr\OneDrive\Pulpit\x\pop"
    outPutFolder = os.path.join(os.path.dirname(inputFolder), os.path.basename(inputFolder) + "_icon")
    # Sprawdź, czy folder "icon" istnieje i jeśli nie, to go utwórz
    if not os.path.exists(outPutFolder):
        os.makedirs(outPutFolder)
    # Utwórz listę plików w folderze "icon"
    existingIconFiles = os.listdir(outPutFolder)
    # Przechodź przez pliki w folderze wejściowym
    for filename in os.listdir(inputFolder):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            inputPath = os.path.join(inputFolder, filename)
            outputPath = os.path.join(outPutFolder, filename)
            # Sprawdź, czy plik już istnieje w folderze "icon"
            if filename not in existingIconFiles:
                # Otwórz obraz
                with Image.open(inputPath) as img:
                    width, height = img.size
                    newWidth = 24
                    newHeight = 24
                    resized_img = img.resize((newWidth, newHeight), Image.ANTIALIAS)
                    resized_img.save(outputPath)



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

    def sendCommand(self, command):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
                clientSocket.connect((self.ip, self.port))
                clientSocket.sendall(f"CMD:{command}".encode())
                while True:
                    data = clientSocket.recv(1024)
                    if data == b"File received":
                        break
        except Exception as e:
            sg.popup_error(e)

    def sendFile(self, filePath):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
                clientSocket.connect((self.ip, self.port))
                file_name = os.path.basename(filePath)
                clientSocket.sendall(f"FILE:{file_name}".encode())
                with open(filePath, 'rb') as file:
                    clientSocket.sendfile(file)
                clientSocket.sendall(b"END")
                while True:
                    data = clientSocket.recv(1024)
                    if data == b"File received":
                        break
        except Exception as e:
            sg.popup_error(e)


    def previewImage(self,xd):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
            clientSocket.connect((self.ip, self.port))
            remoteFIlename = "/home/pi/preview/preview.jpg"
            localFilename = r"C:\Users\gerfr\OneDrive\Pulpit\x\preview.jpg"
            clientSocket.sendall(f"PREVIEW:".encode())
            receivedData = b''
            while True:
                data = clientSocket.recv(1024)
                if data == b'puste':
                    break
                else:
                    with open(localFilename, 'wb') as file:
                        receivedData += data
                        end_mark = receivedData.find(b'koniecpliku')
                        if end_mark != -1:
                            file.write(receivedData[:end_mark])
                            receivedData = receivedData[end_mark + len(b'koniecpliku'):]
                            file.flush()
                            break



    def receiveImage(self, here, ilosc, filename, kolor):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
            clientSocket.connect((self.ip, self.port))
            for i in range(ilosc):
                remoteFIlename = filename+f'/{kolor}_zdjecie_{i+1}.png'
                localFilename = f"{here}/{kolor}_zdjecie_{i+1}.png"
                clientSocket.sendall(f"GET_FILE:{remoteFIlename}".encode())
                receivedData = b''
                while True:
                    data = clientSocket.recv(1024)
                    if data == b'puste':
                        break
                    else:
                        with open(localFilename, 'wb') as file:
                            receivedData += data
                            end_mark = receivedData.find(b'koniecpliku')
                            if end_mark != -1:
                                file.write(receivedData[:end_mark])
                                receivedData = receivedData[end_mark + len(b'koniecpliku'):]
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