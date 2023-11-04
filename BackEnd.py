import os
import paramiko
import PySimpleGUI as sg
import time
import JSON.JSONscrypt as jsc

# za jednym sendem wszyscko i wyjebac connecty/ wysyłać tylko jsony do rpi/lights i zdjecie do jednego wjebac i chuj
def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Czas wykonania funkcji '{func.__name__}': {execution_time} sekund")
        return result
    return wrapper


# Funkcja tworząca folder na komputerze
def createFolder(folderName):
    try:
        os.mkdir(folderName)
        print(f"Pomyślnie utworzono folder o nazwie '{folderName}'.")
    except FileExistsError:
        print(f"Folder o nazwie '{folderName}' już istnieje.")
    except Exception as e:
        print(f"Wystąpił błąd podczas tworzenia folderu: {e}")


# Klasa łącząca się z RPI
class Connection:
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

    # łączenie sie z rpi
    @measure_time
    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            # auto uzupełnianie klucza
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.ip, username=self.username, password=self.password)
            return True
        except paramiko.AuthenticationException:
            sg.popup_error("Błąd uwierzytelniania. Sprawdź nazwę użytkownika i hasło.")
            return False
        except paramiko.SSHException as ssh_ex:
            sg.popup_error(f"Błąd połączenia SSH: {ssh_ex}")
            return False
        except Exception as ex:
            sg.popup_error(f"Błąd połączenia: {ex}, Nastąpi wylogowanie")
            self.sshclient = None
            return False


class Sending(Connection):
    @measure_time
    def sendIn(self, localPath, remotePath):
        self.connect()
        self.localPath = localPath
        self.remotePath = remotePath
        try:
            sftp = self.client.open_sftp()
            sftp.put(self.localPath, self.remotePath)
            sftp.close()
        except paramiko.SSHException as ssh_ex:
            sg.popup_error(f"Błąd połączenia SSH: {ssh_ex}")

    def sendOut(self, localPath, iteration, folderPath, photoNumber):
        self.connect()
        try:
            sftp = self.client.open_sftp()
            for i in range(iteration):
                remote_path = f'{folderPath}/{photoNumber}_zdjecie_{i+1}.jpg'
                print(remote_path)
                local_path = f"{localPath}/{photoNumber}_zdjecie_{i+1}.jpg"
                print(local_path)
                sftp.get(remote_path, local_path)
                i += 1
        except Exception as e:
            print(f'Wystąpił błąd: {str(e)}')


# klasa do wysyłania komend do wykonania na RPI
@measure_time
class Commands(Connection):
    def start(self, *args):
        self.connect()
        commands = args[0]
        stdin, stdout, stderr = self.client.exec_command(commands)
        stdin.close()
        return stdout

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