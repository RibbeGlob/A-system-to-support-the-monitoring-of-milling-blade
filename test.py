import PySimpleGUI as sg
from abc import ABC, abstractmethod
import BackEnd as BE
import scrypt as sc
import json

class Szkielet(sg.Window, ABC):
    def __init__(self, pole, *argv):
        super().__init__(title="cutterGuardingGauge", size=pole)
        self.textStyle = []  # Lista, styli tekstowych (argv[0] zawsze przyjmuje jako argument)
        self.zamkniecie = False
        self.toolList =["xd", "xd2"]        #Wyjebac i zrobic z plikow json
        for iterator in argv[0]:
            self.textStyle.append({'size': iterator})

    # Statyczna metoda konieczna do odpaleniu interfejsu
    @abstractmethod
    def run(self):
        pass

    # Statyczna metoda konieczna do integracji z BE
    @abstractmethod
    def backEndIntegration(self, *argv):
        pass

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

# Klasa odpowiedzialna za interfejs łączenia się z RPI
class PolaczenieRaspberry(Szkielet):
    def __init__(self):
        self.pole = (350, 120)
        self.textLength = [(17, 1)]     # pierwszy argv szkieletu
        self.response = None
        super().__init__(self.pole, self.textLength)
        self.interfejs = [
            [sg.Text("Adres IP Raspberry Pi: ", **self.textStyle[0]), sg.Input(key='-IP-', pad=(1, 1))],
            [sg.Text("Nazwa użytkownika: ", **self.textStyle[0]), sg.InputText(key='-LOGIN-', pad=(1, 1))],
            [sg.Text("Hasło: ", **self.textStyle[0]), sg.InputText(key='-HASLO-', password_char='*', pad=(1, 1))],
            [sg.Text("Zapamiętaj mnie", **self.textStyle[0]), sg.Checkbox("Tak", pad=(0, 1), key='-CX-'),
             sg.Button("Połącz", size=20, pad=((20, 0), (0, 0)), key='-BT-')]
            ]

        self.layout([[self.interfejs]])

    def run(self):
        while not self.zamkniecie:
            event, values = self.read()
            if event == sg.WIN_CLOSED:
                self.zamkniecie = True
                self.close()
            elif event == '-BT-':
                password = values['-HASLO-']
                login = values['-LOGIN-']
                ip = values['-IP-']
                if values['-CX-'] is True:
                    self.buttonEffect(event, 'Połącz', self.backEndIntegration(password, login, ip))
                    self.zamkniecie = self.response     # Wyrwanie z pętli (takie rozwiązanie aby nie zagnieździć if)
                else:
                    self.buttonEffect(event, 'Połącz', self.backEndIntegration(password, login, ip))
                    self.zamkniecie = self.response

    # Trzeba dodać przesył plików potrzebnych do BE
    def backEndIntegration(self, ipRpi, loginRpi, passwordRpi):
        backendObject = BE.RaspberryPi(ipRpi, loginRpi, passwordRpi)
        self.response = backendObject.connect()
        if self.response is True:
            myMenu = MenuRaspberry()
            myMenu.run()
        else:
            pass


class ColorMenu(Szkielet):
    def __init__(self):
        self.pole = (150, 150)
        self.textLength = [(22, 1), (36, 1)]
        self.colors = ['Czerwony', 'Zielony','Czerwony', 'Zielony','Czerwony', 'Zielony']
        super().__init__(self.pole, self.textLength)
        self.interfejs = [
            [sg.Text('Wybierz kolor frezu')],
            [sg.Listbox(values=self.colors, size=(100, 4),
                        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, key='-COLORLIST-')],
            [sg.Button('Potwierdź', size=14,  key='-BC-')]]

        self.layout([[self.interfejs]])


    def run(self):
        while not self.zamkniecie:
            event, values = self.read()
            if event == sg.WIN_CLOSED:
                self.zamkniecie = True
                self.close()
            elif event == '-BC-':
                self.selected_color = values['-COLORLIST-'][0] if values['-COLORLIST-'] else None
                self.buttonEffect(event, 'Połącz', self.backEndIntegration(self.selected_color))


    def backEndIntegration(self, kolor):
        self.menu = BE.IntegracjaGraficzna(kolor)
        self.menu.graphicPopUp()
        self.zamkniecie = True
        self.close()

# Klasa odpowiedzialna za główne menu RPI
class MenuRaspberry(Szkielet):
    def __init__(self):
        self.colorTxt = ""
        self.ip = ""
        self.pole = (350, 390)
        self.textLength = [(22, 1), (36, 1)]
        super().__init__(self.pole, self.textLength)
        self.interfejs = [
            [sg.Text("Czy jest to nowe narzędzie? ", **self.textStyle[0]),
             sg.Radio("Tak", "RADIO", enable_events=True, default=True, key="-YES-"),
             sg.Radio("Nie", "RADIO", enable_events=True, default=False, key="-NO-")],
            [sg.Text("Wprowadź lub wybierz z listy nazwę narzędzia",key="-TXT-", visible=True)],
            [sg.InputCombo(self.toolList, size=(20, 1), key="-COMBO-", disabled=False),
             sg.Button("Potwierdź", size=8, key="-CONFIRM-", disabled=False),
             sg.Button("Wyczyść", size=8, key="-CLEAR-", disabled=False)],
            [sg.Text("Wybierz ścieżkę zapisu pliku na komputerze")],
            [sg.Input(key="-FOLDER-", enable_events=True, **self.textStyle[1]), sg.FolderBrowse(button_text="Wybierz")],
            [sg.Frame('Lewe oświetlenie', [
             [sg.Slider(range=(-8, 8),size=(11, 16), default_value=0, orientation='h', key='-XL-'),
              sg.Slider(range=(-4, 4), size=(4, 16), orientation="v", default_value=0, key='-YL-')]
             ]),
             sg.Frame('Prawe oświetlenie', [
             [sg.Slider(range=(-8, 8),size=(11, 16), default_value=0, orientation='h', key='-XP-'),
              sg.Slider(range=(-4, 4), size=(4, 16), orientation="v", default_value=0, key='-YP-')]
             ])
            ],
            [sg.Button("Wykonaj zdjęcie", size=(10, 5), key="-PICTURE-", visible=True),
             sg.Button("Ustaw światło", size=(10, 5), key="-LIGHTBUTTON-", visible=True),
             sg.Button("Wybierz kolor frezu " + self.colorTxt, size=(15, 5), key="-COLORBUTTON-", visible=True)],
            [sg.Text("Zalogowano do: "+self.ip, key="-TXTLOGGED-"),
             sg.Button("Wyloguj", size=7, key="-LOGOUT-", button_color=("white", "red"))]
        ]

        self.layout(self.interfejs)


    def run(self):
        # Definicja funkcji obsługujących poszczególne zdarzenia
        def closeWindow(_):
            self.zamkniecie = True
            self.close()

        def radioNoButton(_):
            for iterator in ["-COMBO-", "-CONFIRM-", "-CLEAR-"]:
                self[iterator].update(disabled=True)

        def searchFolder(values):
            folder_path = values["-FOLDER-"]

        def lights(values):
            for light in ['-XL-', '-YL-', '-XP-', '-YP-']:
                v = values[light]
                print(v)

        def basicEvent(_):
            for iterator in ["-COMBO-", "-CONFIRM-", "-CLEAR-"]:
                self[iterator].update(disabled=False)

        def colorMenu(_):
            myColor = ColorMenu()
            myColor.run()

        # Mapowanie zdarzeń na odpowiednie funkcje obsługi
        eventsMap = {
            sg.WIN_CLOSED: closeWindow,
            "-NO-": radioNoButton,
            "-FOLDER-": searchFolder,
            "-LIGHTBUTTON-": lights,
            "-COLORBUTTON-": colorMenu
        }


        while not self.zamkniecie:
            event, values = self.read()
            # Wywołanie odpowiedniej funkcji obsługi dla danego zdarzenia
            runFunction = eventsMap.get(event, basicEvent)
            runFunction(values)


    def backEndIntegration(self):
        pass



if __name__ == "__main__":
    #myGui = PolaczenieRaspberry()
    # x = sc.FatherJSON("testowyjson", None)
    # xd = x.read()
    # print(json.dumps(x))

    # na tym poziomie sprawdzenie pliku json czy jest się zalogowanym
    #myGui.run()
    myGui = MenuRaspberry()
    myGui.run()
