import PySimpleGUI as sg
from abc import ABC, abstractmethod
import BackEnd as BE
import JSON.JSONscrypt as jsc
import json
import time


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Czas wykonania funkcji '{func.__name__}': {execution_time} sekund")
        return result
    return wrapper

class Szkielet(sg.Window, ABC):
    def __init__(self, pole, *argv):
        # Nazwa okna + rozmiar okna
        super().__init__(title="cutterGuardingGauge", size=pole)
        # Lista, styli tekstowych (argv[0] zawsze przyjmuje jako argument)
        self.textStyle = []
        self.zamkniecie = False
        for iterator in argv[0]:
            self.textStyle.append({'size': iterator})

    # Metoda odpowiedzialna za wyświetlanie graficzne programu (konieczna do działania klasy)
    @abstractmethod
    def gui(self, *args):
        # przyjęcie interfejsu przez args
        self.interfejs = [arg for arg in args]
        self.layout([[self.interfejs]])
        self.run(None)

    # Metoda obsługująca elementy GUI np. przyciski itp (konieczna do działania klasy)
    @abstractmethod
    def run(self, mapa, basicEvent = None):
        # metoda zamykająca okno (basicEvent musi być zdefiniowany)
        def closeWindow(_):
            self.zamkniecie = True
            self.close()

        # mapowanie eventów
        self.eventsMap = {
            sg.WIN_CLOSED: closeWindow,
        }

        self.eventsMap.update(mapa)
        while not self.zamkniecie:
            event, values = self.read()
            # Wywołanie odpowiedniej funkcji obsługi dla danego zdarzenia
            runFunction = self.eventsMap.get(event, basicEvent)
            runFunction(values)

    # Metoda przycisku
    @staticmethod
    def buttonEffect(buttonTrigger, buttonName, effect):
        if buttonTrigger == buttonName:
            return effect

    # Metoda checkboxa
    @staticmethod
    def checkboxEffect(checkboxTrigger, checkboxStatus):
        if checkboxTrigger == checkboxStatus:
            pass


# Klasa wyświetlająca graficzny pop up
class GraphicPUP(Szkielet):
    def __init__(self, x, y):
        pole = (x, y)
        textLength = [(17, 1)]
        super().__init__(pole, textLength)

    def gui(self, txt):
        super().gui([sg.Column([[sg.Text(txt, justification='center', )]])],
        [sg.Column([[sg.Button('OK', key="-OK-", size=(10,10))]], justification='center')])

    def run(self, mapa, basicEvent = None):
        map = {
            '-OK-': self.exitButton,
        }
        super().run(map)

    def exitButton(self, _):
        self.zamkniecie = True
        self.close()

    def backEndIntegration(self, *argv):
        pass

# Klasa odpowiedzialna za interfejs łączenia się z RPI
class PolaczenieRaspberry(Szkielet):
    def __init__(self):
        pole = (350, 120)
        textLength = [(17, 1)]     # pierwszy argv szkieletu
        self.response = None
        super().__init__(pole, textLength)

    def checkConfiguration(self):
        try:
            checkingConfiguration = jsc.FatherJSON("configJSON", None)  # czytanie jsona
            global check        #globalna cosik bydzie trzeba zmienic
            check = checkingConfiguration.readJSON()        #pobranie danych z jsona config
            if check["ZALOGOWANY"] == True:
                i = 0
                while i < 3:
                    connection = BE.Connection(check["IP"], check["LOGIN"], check["PASSWORD"])
                    logCheck = connection.connect()   #polaczenie z rpi
                    if logCheck == True:
                        run = MenuRaspberry(check["IP"], check["LOGIN"], check["PASSWORD"], check["PATH"])
                        run.gui()
                        break
                    else:
                        # run = MenuRaspberry(check["IP"], check["LOGIN"], check["PASSWORD"], check["PATH"])
                        # run.gui()     #gui do testowania
                        print(i)        #dodać czyszczenie jsona i conne
                        i+=1
            else:
                self.gui()
        except FileNotFoundError:
            #logi do txt
            print("Error plik JSON nie istnieje, stwórz folder configJSON w folderze JSON oraz wklej do niego zawartość"
                  "repairing")
            self.gui()
        except json.decoder.JSONDecodeError:
            print("Plik JSON uszkodzony otwórz plik repairing i wklej zawartość do pliku configJSON")
            self.gui()
        except KeyError:
            print("Plik JSON uszkodzony otwórz plik repairing i wklej zawartość do pliku configJSON")
            self.gui()

    def gui(self, *args):
        super().gui([sg.Text("Adres IP Raspberry Pi: ", **self.textStyle[0]), sg.Input(key='-IP-', pad=(1, 1))],
            [sg.Text("Nazwa użytkownika: ", **self.textStyle[0]), sg.InputText(key='-LOGIN-', pad=(1, 1))],
            [sg.Text("Hasło: ", **self.textStyle[0]), sg.InputText(key='-HASLO-', password_char='*', pad=(1, 1))],
            [sg.Text("Zapamiętaj mnie", **self.textStyle[0]), sg.Checkbox("Tak", pad=(0, 1), key='-CX-'),
             sg.Button("Połącz", size=20, pad=((20, 0), (0, 0)), key='-BT-')])

    def run(self, mapa, basicEvent = None):
        map = {
            '-BT-': self.connectButtonClicked,
        }
        super().run(map)

    def connectButtonClicked(self, values):
        password = values['-HASLO-']
        login = values['-LOGIN-']
        ip = values['-IP-']
        if values['-CX-']:
            self.buttonEffect('-BT-', 'Połącz', self.backEndIntegration(ip, login, password, True))   #wywolanie BEI
        else:
            self.buttonEffect('-BT-', 'Połącz', self.backEndIntegration(ip, login, password, False))

    # Trzeba dodać przesył plików potrzebnych do BE
    def backEndIntegration(self, ip, login, password, check):
        #backendObject = BE.RaspberryPi(ipRpi, loginRpi, passwordRpi)
        #self.response = backendObject.connect()        #to git
        dataJSON = {"WERSJA": "G1.0", "ZALOGOWANY": check, "IP": ip, "LOGIN": login, "PASSWORD": password, "PATH": ""}
        checkingJS = jsc.FatherJSON("configJSON", dataJSON)
        checkingJS.writeJSON()
        self.close()
        myMenu = MenuRaspberry(ip, login, password, "")
        myMenu.gui(None)


class ColorMenu(Szkielet):
    def __init__(self):
        pole = (150, 150)
        textLength = [(22, 1), (36, 1)]
        self.colors = ['Czarny', 'Cyjan', 'Magenta', 'Żółty', 'Niebieski', 'Czerwony']   #trzeba dodac kontrast
        super().__init__(pole, textLength)

    def gui(self, *args):
        super().gui([sg.Text('Wybierz kolor frezu')],
            [sg.Listbox(values=self.colors, size=(100, 4),
                        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, key='-COLORLIST-')],
            [sg.Button('Potwierdź', size=14,  key='-BC-')])
        return self.selectedColor

    def run(self, mapa, basicEvent = None):
        map = {
            '-BC-': self.colorButton,
        }
        super().run(map)

    def colorButton(self, values):
        self.selectedColor = values['-COLORLIST-'][0] if values['-COLORLIST-'] else None
        self.buttonEffect('-BC-', 'Połącz', self.backEndIntegration(self.selectedColor))

    def backEndIntegration(self, kolor):
        if kolor is not None:
            self.menu = GraphicPUP(200, 80)
            self.menu.gui(f"Wybrany kolor: {kolor}")
            self.zamkniecie = True
            self.close()
        else:
            pass


# Klasa odpowiedzialna za główne menu RPI
class MenuRaspberry(Szkielet):
    def __init__(self, ip, login, password, path):
        self.colorCutter = ""
        self.ip, self.login, self.password, self.path = ip, login, password, path
        self.lightsList = [0, 0, 0, 0]
        self.rgb = [0, 0, 0]
        pole = (350, 390)
        textLength = [(22, 1), (36, 1)]
        xd = jsc.ToolsJSON()
        self.toolList = xd.readJSON()
        super().__init__(pole, textLength)

    def gui(self, *args):
        super().gui([sg.Text("Czy jest to nowe narzędzie? ", **self.textStyle[0]),
                     sg.Radio("Tak", "RADIO", enable_events=True, default=True, key="-YES-"),
                     sg.Radio("Nie", "RADIO", enable_events=True, default=False, key="-NO-")],
                    [sg.Text("Wprowadź lub wybierz z listy nazwę narzędzia", key="-TXT-", visible=True)],
                    [sg.InputCombo(self.toolList, size=(32, 1), key="-COMBO-", readonly=False),
                     sg.Button("Potwierdź", size=(8, 1), key="-CONFIRM-", disabled=False)],
                    [sg.Text("Wybierz ścieżkę zapisu pliku na komputerze")],
                    [sg.Input(key="-FOLDER-", default_text=self.path, enable_events=True, **self.textStyle[1]),
                     sg.FolderBrowse(button_text="Wybierz", key="-BROWSE-")],
                    [sg.Frame('Lewe oświetlenie', [
                        [sg.Slider(range=(-8, 8), size=(11, 16), default_value=0, orientation='h', key='-XL-'),
                         sg.Slider(range=(-4, 4), size=(4, 16), orientation="v", default_value=0, key='-YL-')]
                    ]),
                     sg.Frame('Prawe oświetlenie', [
                         [sg.Slider(range=(-8, 8), size=(11, 16), default_value=0, orientation='h', key='-XP-'),
                          sg.Slider(range=(-4, 4), size=(4, 16), orientation="v", default_value=0, key='-YP-')]
                     ])
                     ],
                    [sg.Button("Wykonaj zdjęcie", size=(10, 5), key="-PICTURE-", disabled = True),
                     sg.Button("Ustaw światło", size=(10, 5), key="-LIGHTBUTTON-"),
                     sg.Button(f"Wybierz kolor frezu {self.colorCutter}", size=(15, 5), key="-COLORBUTTON-")],
                    [sg.Text(f"Zalogowano do: {self.ip}", key="-TXTLOGGED-"),
                     sg.Button("Wyloguj", size=(7, 1), key="-LOGOUT-", button_color=("white", "red"))])

    def run(self, mapa, basicEvent = None):

        # noinspection PyRedeclaration
        def basicEvent(_):
            for iterator in ["-COMBO-"]:
                self[iterator].update(readonly=False)

        def radioYesButton(_):
            for iterator in ["-COMBO-"]:
                self[iterator].update(readonly=False)

        def radioNoButton(_):
            for iterator in ["-COMBO-"]:
                self[iterator].update(readonly=True)

        def searchFolder(values):
            self.folderPath = values["-FOLDER-"]
            path = jsc.PathJSON()
            path.writeJSON(self.folderPath)

        def lights(values):
            self.lightsList.clear()
            for light in ['-XL-', '-YL-', '-XP-', '-YP-']:
                self.lightsList.append(values[light])
            print(self.lightsList)
            createJson = jsc.LightsJSON(self.lightsList)
            path = createJson.writeJSON()
            # Wysyłanie do RPI JSONA z informacjami o ustawionym świetle + programu odpalającego światło, następie
            # Odpalenie światełek
            send = BE.Sending(check["IP"], check["LOGIN"], check["PASSWORD"])
            send.sendIn(f"{path}\\lightsJSON.json", '/home/pi/Lights/lightsJSON.json')
            print('przeslano json')
            send2 = BE.Sending(check["IP"], check["LOGIN"], check["PASSWORD"])
            send2.sendIn(f"{path}\\lights.py", '/home/pi/Lights/lights.py')
            print('przeslano lights')
            on = BE.Commands(check["IP"], check["LOGIN"], check["PASSWORD"])
            on.start("sudo python3 /home/pi/Lights/lights.py")

        def colorMenu(_):
            # Wyświetlanie menu z dostępnymi kolorami frezu, changing name zmienia nazwę na kontrastowe RGB
            myColor = ColorMenu()
            color = myColor.gui()
            self.rgb = BE.changingNameToRGB(color)
            print(self.rgb)

        def picture(_):
            currentDate = time.strftime('%Y-%m-%d')
            # noinspection PyUnresolvedReferences
            pictureName = f'{self.txt}_{currentDate}'   #Nazwa folderu z dzisiejsza data
            jsonLights = jsc.ToolsJSON()
            # noinspection PyUnresolvedReferences
            jsonLights.writeJSON(settings=[self.lightsList], color=[self.rgb], name=self.txt)
            on = BE.Commands(check["IP"], check["LOGIN"], check["PASSWORD"])
            on.start(f'mkdir /home/pi/{pictureName}')       #Tworzenie folderu na RPI
            # noinspection PyUnresolvedReferences
            BE.createFolder(f'{self.folderPath}\\testowanazwa')
            photo = BE.Photo(check["IP"], check["LOGIN"], check["PASSWORD"])
            photo.takePhoto(20, f'/home/pi/{pictureName}')
            # noinspection PyUnresolvedReferences
            photo.sendOut(f'{self.folderPath}\\testowanazwa')

        # przycisk potwierdzający wybór narzędzia
        def confirm(values):
            self.txt = values["-COMBO-"]
            if bool(self.txt):
                confirmButton = jsc.toolsConfirm(self.txt)
                self.actually = confirmButton.readJSON()
                self.toolList = self.actually
                self["-COMBO-"].update(values=list(self.toolList.keys()))
                self["-COMBO-"](self.txt)
                self["-PICTURE-"].update(disabled=False)
            else:
                self.menu = GraphicPUP(150, 80)
                self.menu.gui("Zdefiniuj narzędzie")

        # przycisk wyloguj
        def logout(_):
            x = jsc.DeleteConfig()
            x.readJSON()            #czysci json
            self.close()            #zamyka okno
            self.menu = GraphicPUP(150, 80)     #Graficzny PopUp
            self.menu.gui("Wylogowano")
            myGui = PolaczenieRaspberry()       #Odpalenie od poczatku
            myGui.checkConfiguration()


        # Mapowanie zdarzeń na odpowiednie funkcje obsługi
        mapa = {
            "-YES-": radioYesButton,
            "-NO-": radioNoButton,
            "-FOLDER-": searchFolder,
            "-LIGHTBUTTON-": lights,
            "-COLORBUTTON-": colorMenu,
            "-PICTURE-": picture,
            "-CONFIRM-": confirm,
            "-LOGOUT-": logout
        }

        super().run(mapa)

    def backEndIntegration(self):
        pass

def main():
    myGui = PolaczenieRaspberry()
    myGui.checkConfiguration()

if __name__ == "__main__":
    main()