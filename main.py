import PySimpleGUI as sg
from abc import ABC, abstractmethod
import BackEnd as BE
import JSON.JSONscrypt as jsc
import json
from PIL import Image
import os
import io
# Na samym początku sprawdzić czy wszystkie pliki przesłane         dodać jpga
# Zoptymalizować
# Dodać ilość zdjęć  (6,3) ilośc przycisków zależna od ilości zdjęć
# dodaj thread do zmian miejsca

class Szkielet(sg.Window, ABC):
    def __init__(self, pole, *argv):
        # Nazwa okna + rozmiar okna
        super().__init__(title="cutterGuardingGauge", size=pole, location=(0,0))
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
                    # zmiana do sprawdzenia gui
                    connection = BE.Connection(check["IP"], check["LOGIN"], check["PASSWORD"])
                    logCheck = connection.connect()   #polaczenie z rpi
                    if logCheck == True:
                        run = MenuRaspberry(check["IP"], check["LOGIN"], check["PASSWORD"])
                        run.gui()
                        break
                    else:
                        # run = MenuRaspberry(check["IP"], check["LOGIN"], check["PASSWORD"], check["PATH"])
                        # run.gui()     #gui do testowania
                        # print(i)        #dodać czyszczenie jsona i conne
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
        dataJSON = {"WERSJA": "G1.0", "ZALOGOWANY": check, "IP": ip, "LOGIN": login, "PASSWORD": password}
        checkingJS = jsc.FatherJSON("configJSON", dataJSON)
        checkingJS.writeJSON()
        self.close()
        myMenu = MenuRaspberry(ip, login, password)
        myMenu.gui(None)


class ColorMenu(Szkielet):
    def __init__(self):
        pole = (150, 150)
        textLength = [(22, 1), (36, 1)]
        self.selectedColor = None
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
        self.buttonEffect('-BC-', 'Połącz', self.backEndIntegration())

    def backEndIntegration(self):
        if self.selectedColor is not None:
            self.menu = GraphicPUP(200, 80)
            self.menu.gui(f"Wybrany kolor: {self.selectedColor}")
            self.zamkniecie = True
            self.close()
        else:
            pass


# Klasa odpowiedzialna za główne menu RPI
class MenuRaspberry(Szkielet):
    def __init__(self, ip, login, password):
        self.iteracja = 1
        self.angle = 0
        self.colorCutter = ""
        self.ip, self.login, self.password = ip, login, password
        self.lightsList = [0, 0, 0, 0]
        self.rgb = [0, 0, 0]
        pole = (350, 480)
        textLength = [(22, 1), (36, 1)]
        xd = jsc.ToolsJSON()
        self.toolList = xd.readJSON()
        self.checkIfNewTool = 0
        super().__init__(pole, textLength)

    def gui(self, *args):
        super().gui([sg.Text("Czy jest to nowe narzędzie? ", **self.textStyle[0]),
                     sg.Radio("Tak", "RADIO", enable_events=True, default=False, key="-YES-"),
                     sg.Radio("Nie", "RADIO", enable_events=True, default=True, key="-NO-")],
                    [sg.Text("Wprowadź lub wybierz z listy nazwę narzędzia", key="-TXT-", visible=True)],
                    [sg.InputCombo(self.toolList, size=(32, 1), key="-COMBO-", readonly=True),
                     sg.Button("Potwierdź", size=(8, 1), key="-CONFIRM-", disabled=False)],
                    [sg.Text("Wybierz ścieżkę zapisu pliku na komputerze")],
                    [sg.Input(key="-FOLDER-", enable_events=True, **self.textStyle[1]),
                     sg.FolderBrowse(button_text="Wybierz", key="-BROWSE-")],
                    [sg.Text("Określ liczbę zdjęć do wykonania")],
                    [sg.Input(key="-ANGLE-", enable_events=True, size=(34, 1)),
                     sg.Button("Potwierdź", size=(8, 1), key="-ANGLECONFIRM-", disabled=False)],
                    [sg.Text(f"Aktualny kąt obrotu ostrza: {self.angle} stopni",
                             **self.textStyle[1], key="-ANGLEOUTPUT-")],
                    [sg.Frame('Lewe oświetlenie', [
                        [sg.Slider(range=(-8, 8), size=(11, 16), default_value=0, orientation='h', key='-XL-'),
                         sg.Slider(range=(-4, 4), size=(4, 16), orientation="v", default_value=0, key='-YL-')]
                    ]),
                     sg.Frame('Prawe oświetlenie', [
                         [sg.Slider(range=(-8, 8), size=(11, 16), default_value=0, orientation='h', key='-XP-'),
                          sg.Slider(range=(-4, 4), size=(4, 16), orientation="v", default_value=0, key='-YP-')]
                     ])
                     ],
                    [sg.Button("Wykonaj zdjęcie", size=(8, 5), key="-PICTURE-", disabled=True),
                     sg.Button("Ustaw światło", size=(8, 5), key="-LIGHTBUTTON-"),
                     sg.Button(f"Wybierz kolor frezu {self.colorCutter}", size=(8, 5), key="-COLORBUTTON-"),
                     sg.Button("Podgląd zdjęcia", size=(8, 5), key="-SHOWPICTURE-", disabled=True)],
                    [sg.Text(f"Zalogowano do: {self.ip}", key="-TXTLOGGED-"), sg.Push(),
                     sg.Button("Wyloguj", size=(7, 1), key="-LOGOUT-", button_color=("white", "red"))])

    def run(self, mapa, basicEvent = None):
        # noinspection PyRedeclaration
        def basicEvent(_):
            for iterator in ["-COMBO-"]:
                self[iterator].update(readonly=False)

        def radioYesButton(_):
            self.checkIfNewTool = 1
            for iterator in ["-COMBO-"]:
                self[iterator].update(readonly=False)


        def radioNoButton(_):
            self.checkIfNewTool = 0
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
            createJson = jsc.LightsJSON({"Lights": self.lightsList})
            path = createJson.writeJSON()
            # Wysyłanie do RPI JSONA z informacjami o ustawionym świetle + programu odpalającego światło, następie
            # Odpalenie światełek
            send = BE.Sending(check["IP"], check["LOGIN"], check["PASSWORD"])
            send.sendIn(f"{path}\\lightsAndIterationJSON.json", '/home/pi/Lights/lightsAndIterationJSON.json')
            send.sendIn(f"{path}\\lights.py", '/home/pi/Lights/lights.py')
            on = BE.Commands(check["IP"], check["LOGIN"], check["PASSWORD"])
            on.start("sudo python3 /home/pi/Lights/lights.py")

        # Przycisk odpowiadający za podgląd zdjęć
        def showPicture(_):
            # noinspection PyUnresolvedReferences
            photoMenu = PictureMenu(self.txt)
            photoMenu.gui()

        # Przycisk odpowiadajacy za menu wyboru koloru frezu
        def colorMenu(_):
            # changing name zmienia nazwę na kontrastowe RGB
            myColor = ColorMenu()
            color = myColor.gui()
            self.rgb = BE.changingNameToRGB(color)
            print(self.rgb)

        # Puste aby działała aktualizacja kąta
        def angle(_):
            pass

        # Potwierdzenie wyboru ilosci zdjec
        def angleConfirm(values):
            try:
                self.enteredAngle = int(values["-ANGLE-"])
                # Przeliczanie ilości zdjęć na kąt obrotu frezu
                angle = round(360 / self.enteredAngle, 3)
                self["-ANGLEOUTPUT-"].update(f"Aktualny kąt obrotu ostrza: {angle} stopni")
            except ValueError:
                sg.popup_error('Błędna wartość')

        # Przycisk odpowiadający za wykonywanie zdjęć
        def picture(_):
            # noinspection PyUnresolvedReferences
            pictureName = f'{self.txt}'   #Nazwa folderu z nazwą narzędzia
            photoFolder = jsc.LightsJSON({"Folder": f'/home/pi/{pictureName}'})
            photoFolder.appendJSON()
            if self.checkIfNewTool == 0:        # Jeżeli nie jest to nowe narzędzie to dodaje do listy toolsjson
                # noinspection PyUnresolvedReferences
                appendToJSON = jsc.AppendJSON(self.txt.upper(), [self.lightsList], [self.rgb])
                self.iteracja = appendToJSON.readJSON()
                # noinspection PyUnresolvedReferences
                photoIteration = jsc.LightsJSON({"LiczbaZdjec": self.enteredAngle, "Iteracja": self.iteracja})
                photoIteration.appendJSON()         # Json wysyłany na RPI

            else:           #jeżeli nowe narzędzie to tworzy nowy key w jsonie
                try:
                    # noinspection PyUnresolvedReferences
                    photoIteration = jsc.LightsJSON({"LiczbaZdjec": self.enteredAngle, "Iteracja": self.iteracja})
                    photoIteration.appendJSON()
                except FileNotFoundError:
                    sg.popup_error("Plik JSON nie istnieje.")
                except Exception as e:
                    # noinspection PyUnresolvedReferences
                    if self.enteredAngle is None:
                        sg.popup_error(f"Wprowadź liczbę zdjęć")
                    else:
                        pass
                self.checkIfNewTool -= 1        # Unika się nadpisywania tylko przechodzi do appendu
                jsonLights = jsc.ToolsJSON()
                # noinspection PyUnresolvedReferences
                jsonLights.writeJSON(settings=[self.lightsList], color=[self.rgb],
                                     name=self.txt, iteracja=self.iteracja, path=self.folderPath)
                # noinspection PyUnresolvedReferences
                BE.createFolder(rf"{self.folderPath}\{self.txt}")

            path = photoIteration.returnPath()
            on = BE.Commands(check["IP"], check["LOGIN"], check["PASSWORD"])
            on.start(f'mkdir /home/pi/{pictureName}')       #Tworzenie folderu na RPI
            send = BE.Sending(check["IP"], check["LOGIN"], check["PASSWORD"])
            send.sendIn(f"{path}\\lightsAndIterationJSON.json", '/home/pi/Lights/lightsAndIterationJSON.json')
            send.sendIn(f"{path}\\Camera.py", '/home/pi/Lights/Camera.py')
            stdout = on.start("sudo python3 /home/pi/Lights/Camera.py")
            while not stdout.channel.exit_status_ready():       # Czekanie aż się wykonają zdjęcia
                pass
            read = jsc.FatherJSON("toolsJSON", None)
            # data = read.readJSON()
            hereFolder = read.readJSON()[self.txt.upper()].get("PATH", "")
            send.sendOut(hereFolder+f"/{self.txt}", self.enteredAngle,
                                   f'/home/pi/{pictureName}', self.iteracja)
            self["-ANGLECONFIRM-"].update(disabled=True)


        # przycisk potwierdzający wybór narzędzia
        def confirm(values):
            self.txt = values["-COMBO-"]        # Pobranie wartości z comboboxa
            if bool(self.txt):
                confirmButton = jsc.toolsConfirm(self.txt)
                self.actually = confirmButton.readJSON()
                self.toolList = self.actually
                self["-COMBO-"].update(values=list(self.toolList.keys()))
                self["-COMBO-"](self.txt)
                self["-PICTURE-"].update(disabled=False)
                self["-SHOWPICTURE-"].update(disabled=False)
                # Dodać na czytanie ścieżki
                try:
                    self["-FOLDER-"].update(value=self.actually[self.txt.upper()]["PATH"])
                    result = "ITERACJA" in self.actually[self.txt.upper()] and \
                             self.actually[self.txt.upper()]["ITERACJA"] is not None
                    self["-ANGLECONFIRM-"].update(disabled=result)
                    self["-ANGLE-"].update(self.actually[self.txt.upper()]["ITERACJA"])
                    self.enteredAngle = self.actually[self.txt.upper()]["ITERACJA"]
                except KeyError:
                    pass

            else:
                sg.popup_error("Zdefiniuj narzędzie")


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
            "-LOGOUT-": logout,
            "-SHOWPICTURE-": showPicture,
            "-ANGLE-": angle,
            "-ANGLECONFIRM-": angleConfirm,
        }

        super().run(mapa)

    def backEndIntegration(self):
        pass

# Klasa odpowiedzialna za wyświetlanie zdjec
class PictureMenu(Szkielet):
    def __init__(self, txt):
        keyRead = jsc.FatherJSON("toolsJSON", None)
        keyPath = keyRead.readJSON()
        self.txt = txt.upper()
        print(f"{keyPath[str(self.txt)]['PATH']}/{self.txt}")
        self.photoFolder = f"{keyPath[str(self.txt)]['PATH']}/{self.txt}"
        self.photoFolder = self.photoFolder.replace('/', '\\')
        self.lightSlider = keyPath[str(self.txt)]["ITERACJA"]
        self.pictureIndex = 1
        self.pictureLight = 1
        self.max_number = 1
        pole = (1530, 810)
        textLength = [(22, 1), (36, 1)]
        self.folderMethod()
        self.defaultPhoto = f"{self.photoFolder}\\1_zdjecie_1.png"
        self.resized_image = self.resize_image(self.defaultPhoto, (850, 620))
        super().__init__(pole, textLength)

    def folderMethod(self):
        # Konwersja jpg na png
        for filename in os.listdir(self.photoFolder):
            if filename.endswith(".jpg"):
                jpg_path = os.path.join(self.photoFolder, filename)
                png_path = os.path.splitext(jpg_path)[0] + ".png"
                try:
                    jpg_image = Image.open(jpg_path)
                    jpg_image.save(png_path, "PNG")
                    jpg_image.close()
                    os.remove(jpg_path)
                except Exception as e:
                    print(f"Błąd podczas konwersji i usuwania pliku {jpg_path}: {e}")

        # Liczenie plików PNG
        if os.path.exists(self.photoFolder) and os.path.isdir(self.photoFolder):
            for filename in os.listdir(self.photoFolder):
                if filename.endswith(".png"):
                    try:
                        number = int(filename[len("1_zdjecie_"):filename.find(".png")])
                        self.max_number = max(self.max_number, number)
                    except ValueError:
                        print(f"Błąd podczas przetwarzania pliku {filename}: Nie można odczytać numeru.")

    def gui(self, *args):
        i = 0
        super().gui([sg.Text(f"Aktualnie wyświetlane narzędzie {self.txt}")],
                    [sg.Image(self.resized_image, key="cutterGuardingGauge")],
                     [sg.Slider(range=(1, self.max_number), default_value=1,
                                           orientation='h',  key='-SP-', enable_events=True,size=(100,20))],
                        [sg.Slider(range=(1, self.lightSlider), default_value=1,
                                              orientation='h', key='-SL-', enable_events=True,size=(100,20))],

                    )

    def run(self, mapa, basicEvent = None):

        def pictureSlider(values):
            self.pictureIndex = int(values['-SP-'])
            self.updatePicture()

        def lightSlider(values):
            self.pictureLight = int(values['-SL-'])
            self.updatePicture()

        map = {
            '-SP-': pictureSlider,
            '-SL-': lightSlider,

        }


        super().run(map)

    # Metoda do zmniejszania png
    def resize_image(self, image_path, size):
        original_image = Image.open(image_path)
        original_image.thumbnail(size, Image.LANCZOS)
        bio = io.BytesIO()
        original_image.save(bio, format="PNG")
        return bio.getvalue()

    # Update pokazywanych zdjęć
    def updatePicture(self):
        photoPath = os.path.join(self.photoFolder, f'{self.pictureLight}_zdjecie_{self.pictureIndex}.png')
        photo_image = self.resize_image(photoPath, (850, 620))
        self._window_that_exited["cutterGuardingGauge"].update(data=photo_image)

    def updateButtonPicture(self):
        pass

    def backEndIntegration(self, kolor):
        pass

def main():
    myGui = PolaczenieRaspberry()
    myGui.checkConfiguration()

if __name__ == "__main__":
    main()