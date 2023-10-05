import os
import paramiko
import PySimpleGUI as sg
import time

class Connection():
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

    def connect(self):              #łączenie sie z rpi
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())       #auto uzupełnianie klucz
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

    def sendOut(self, localPath, remotePath):
        if self.client is None:
            self.connect()
        self.localPath = localPath
        self.remotePath = remotePath
        try:
            sftp = self.client.open_sftp()
            sftp.put(self.remotePath, self.localPath)
            sftp.close()
        except paramiko.SSHException as ssh_ex:
            sg.popup_error(f"Błąd połączenia SSH: {ssh_ex}")


class Photo(Connection):
    def takePhoto(self, x):
        if self.ssh_client is None:
            sg.Popup('Błąd', 'Brak aktywnego połączenia z Raspberry Pi.')
            return None
        try:
            i = 0
            while i <= x:  # Zmieniony warunek
                self.photoPath = "/home/pi/" + f'zdjecie{i}.jpg'
                command = f'raspistill -n -o {self.photoPath} -t 10'
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
                print(self.photoPath)
                i += 1
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
                stdin.channel.recv_exit_status()
                time.sleep(0.3)
        except paramiko.SSHException as e:
            sg.Popup('Błąd SSH', f'Wystąpił błąd SSH: {str(e)}')


class LightsON(Connection):
    def start(self):
        commands_to_run = "sudo python3 /home/pi/Lights/lights.py"
        self.connect()
        try:
            stdin, stdout, stderr = self.client.exec_command(commands_to_run)
            print("Komendy zostały wykonane na Raspberry Pi.")
        except Exception as e:
            sg.Popup(f"Wystąpił błąd podczas wykonywania komend: {e}")



# commands_to_run = [
#     "pkill -f xd2.py"
#     "sudo python3 /home/pi/xd2.py"
# ]


def changingNameToRGB(kolor):
    kolory = {
        "Cyjan": [255, 0, 0],
        "Magenta": [0, 255, 0],
        "Żółty": [0, 0, 255],
        "Czarny": [255, 255, 255],
        "Niebieski": [255, 255, 0],
        "Czerwony": [0, 255, 255]
    }
    return kolory.get(kolor, [255, 255, 255])


class RaspberryPi:
    def __init__(self, ipAddress, username, password):
        self.ssh_client = None
        self.ipAddress = ipAddress
        self.username = username
        self.password = password

    def connect(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.ipAddress, username=self.username, password=self.password)
            self.ssh_client = client
            y = Camera("raspberryfrez", 'pi', 'student')
            y.take_photo("/home/pi/", 10)
        except paramiko.AuthenticationException:
            sg.popup_error("Błąd uwierzytelniania. Sprawdź nazwę użytkownika i hasło.")
            return False
        except paramiko.SSHException as ssh_ex:
            sg.popup_error(f"Błąd połączenia SSH: {ssh_ex}")
            return False
        except Exception as ex:
            sg.popup_error(f"Błąd połączenia: {ex}")
            self.ssh_client = None
            return False

    def disconnect(self):
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None

class Camera(RaspberryPi):
    def take_photo(self, photoPath, x):
        if self.ssh_client is None:
            sg.Popup('Błąd', 'Brak aktywnego połączenia z Raspberry Pi.')
            return None

        try:
            photoPath = os.path.join(photoPath, f'zdjecie{x}.jpg')
            print(photoPath)
            command = f'raspistill -o {photoPath}'
            self.ssh_client.exec_command(command)
            return photoPath
        except paramiko.SSHException as e:
            sg.Popup('Błąd SSH', f'Wystąpił błąd SSH: {str(e)}')



class FileTransferOut(RaspberryPi):
    def download_folder(self, remotePath, localPath):
        try:
            sftp = self.ssh_client.open_sftp()
            os.makedirs(localPath, exist_ok=True)
            files = sftp.listdir_attr(remotePath)
            for file in files:
                remoteFile = os.path.join(remotePath, file.filename)
                localFile = os.path.join(localPath, file.filename)
                if file.st_mode & 0o040000:  # Sprawdz czy to katalog
                    self.download_folder(remoteFile, localFile)
                else:
                    sftp.get(remoteFile, localFile)
            sftp.close()
        except Exception as ex:
            print(f"Błąd połączenia: {ex}")


class FileTransferIn(RaspberryPi):
    def transferFile(self, localPath, remotePath):
        try:
            if self.ssh_client is None:
                self.connect()
            sftp = self.ssh_client.open_sftp()
            sftp.put(localPath, remotePath)
            sftp.close()  # Zamknięcie połączenia SFTP po wykonaniu operacji
            print(f"Plik {localPath} został przesłany na Raspberry Pi do {remotePath}.")
        except Exception as e:
            print(f"Wystąpił błąd podczas przesyłania pliku: {e}")



class LightsCode():
    pass


# file_transfer = FileTransferIn('raspberryfrez', 'pi','student')
# file_transfer.transferFile("C:\\Users\\gerfr\\PycharmProjects\\raspberry\\Lights.py", '/home/pi/xd2.py')
# WYJEBALEM W NIEDZIELE
#
# xd = LightsON('raspberryfrez', 'pi','student')
# xd.start()
#
#
# gut dziala
#
#
# def run_commands_on_raspberry_pi(ip_address, username, password, commands):
#     try:
#         # Utwórz klienta SSH
#         client = paramiko.SSHClient()
#         client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         client.connect(ip_address, username=username, password=password)
#         print('xd')
#         # Wykonaj komendy na Raspberry Pi
#         for command in commands:
#             stdin, stdout, stderr = client.exec_command(command)
#             print(stdout.read().decode('utf-8'))
#             print(stderr.read().decode('utf-8'))
#
#         # Zakończ połączenie SSH
#         client.close()
#         print("Komendy zostały wykonane na Raspberry Pi.")
#     except Exception as e:
#         print(f"Wystąpił błąd podczas wykonywania komend: {e}")
#
# # Dane logowania do Raspberry Pi
# raspberry_pi_ip = "raspberryfrez.local"
# raspberry_pi_username = "pi"
# raspberry_pi_password = "student"
#
# # Lista komend do wykonania
# commands_to_run = [
#     "pkill -f xd2.py"
#     "sudo python3 /home/pi/xd2.py"
# ]
#
# Wywołanie funkcji uruchamiającej komendy na Raspberry Pi
# run_commands_on_raspberry_pi(raspberry_pi_ip, raspberry_pi_username, raspberry_pi_password, commands_to_run)
# CHYBA POTRZEBNE WYJEBALEM W NIEDZIZELE
#
# class downloadFile():
#     # Jeśli użytkownik nie wybrał ścieżki, zakończ funkcję
#     if not path:
#         return
#
#     # Nazwa pliku, do którego zapiszemy dane
#     filename = 'dane.txt'
#
#     # Pełna ścieżka do pliku
#     file_path = f"{path}/{filename}"
#
#     # Otwieramy plik w trybie zapisu i zapisujemy dane
#     with open(file_path, 'w') as file:
#         file.write(f'Imię: {name}\n')
#         file.write(f'Wiek: {age}\n')
