import os
import paramiko
import PySimpleGUI as sg
import time

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


# Klasa robiąca zdjęcia + przesył plików na PC
class Photo(Connection):
    @measure_time
    def sendOut(self, localPath):
        self.connect()
        self.localPath = localPath
        try:
            sftp = self.client.open_sftp()
            for i in range(20):
                remote_path = f'{self.folderPath}/zdjecie{i}.jpg'
                local_path = f"{self.localPath}\\test{i}.jpg"
                sftp.get(remote_path, local_path)
                print(f'Pobrano zdjecie z Raspberry Pi i zapisano je jako {local_path}')
                i += 1
        except Exception as e:
            print(f'Wystąpił błąd: {str(e)}')

    @measure_time
    def takePhoto(self, x, folderPath):
        self.folderPath = folderPath
        try:
            self.connect()
            i = 0
            while i <= 0:  # Zmieniony warunek
                self.photoPath = f"{self.folderPath}" + f'/zdjecie{i}.jpg'
                print(self.photoPath)
                command = f'raspistill -n -o {self.photoPath} -t 1'
                i += 1
                stdin, stdout, stderr = self.client.exec_command(command)
                stdin.channel.recv_exit_status()        #czeka na zakonczenie komendy
        except paramiko.SSHException as e:
            sg.Popup('Błąd SSH', f'Wystąpił błąd SSH: {str(e)}')
        finally:
            self.client.close()


# klasa do wysyłania komend do wykonania na RPI (włączenie świateł na ten moment)
@measure_time
class Commands(Connection):
    def start(self, *args):
        commands = args[0]
        print('przed connectem')
        self.connect()
        try:
            # stdin, stdout, stderr =
            self.client.exec_command(commands)
        except Exception as e:
            sg.Popup(f"Wystąpił błąd podczas wykonywania komend: {e}")
        finally:
            self.client.close()


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