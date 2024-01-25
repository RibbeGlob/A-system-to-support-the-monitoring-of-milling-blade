import PySimpleGUI as Sg
from abc import ABC, abstractmethod
import BackEnd as Be
import JSON.JSONscrypt as Jsc
import json
from PIL import Image
import os
import io
from threading import Thread
import time
from functools import partial


# Klasa odpowiedzialna za szkielet GUI
class Szkielet(Sg.Window, ABC):
    def __init__(self, pole, *argv):
        super().__init__(title="cutterGuardingGauge", size=pole, location=(0, 0))
        self.textStyle = []
        self.zamkniecie = False
        for iterator in argv[0]:
            self.textStyle.append({'size': iterator})

    @abstractmethod
    def gui(self, *args):
        self.interfejs = [arg for arg in args]
        self.layout([[self.interfejs]])
        self.run(None)

    @abstractmethod
    def run(self, mapa, basicEvent = None):
        def closeWindow(_):
            self.zamkniecie = True
            self.close()

        self.eventsMap = {
            Sg.WIN_CLOSED: closeWindow,
        }

        self.eventsMap.update(mapa)
        while not self.zamkniecie:
            event, values = self.read()
            runFunction = self.eventsMap.get(event, basicEvent)
            runFunction(values)

    @staticmethod
    def buttonEffect(buttonTrigger, buttonName, effect):
        if buttonTrigger == buttonName:
            return effect

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
        super().gui([Sg.Column([[Sg.Text(txt, justification='center', )]])],
                    [Sg.Column([[Sg.Button('OK', key="-OK-", size=(10, 10))]], justification='center')])

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
        textLength = [(17, 1)]
        self.response = None
        super().__init__(pole, textLength)

    def checkConfiguration(self):
        try:
            checkingConfiguration = Jsc.FatherJSON("configJSON", None)  # czytanie jsona
            global check
            check = checkingConfiguration.readJSON()        #pobranie danych z jsona config
            if check["ZALOGOWANY"] == True:
                i = 0
                while i < 3:
                    # zmienna do sprawdzenia gui
                    connection = Be.Connection(check["IP"], check["PORT"])
                    logCheck = connection.connect()   #polaczenie z rpi
                    connection.clientSocket.close()
                    if logCheck == True:
                        run = MenuRaspberry(check["IP"], check["PORT"])
                        run.gui()
                        break
                    else:
                        i += 1
            else:
                self.gui()
        except FileNotFoundError:
            Sg.popup_error(FileNotFoundError)
            self.gui()
        except json.decoder.JSONDecodeError:
            Sg.popup_error(json.decoder.JSONDecodeError)
            self.gui()
        except KeyError:
            Sg.popup_error(KeyError)
            self.gui()

    def gui(self, *args):
        super().gui([Sg.Text("Adres IP Raspberry Pi: ", **self.textStyle[0]), Sg.Input(key='-IP-', pad=(1, 1))],
                    [Sg.Text("Port: ", **self.textStyle[0]), Sg.InputText(key='-PORT-', pad=(1, 1))],
                    [Sg.Text("Zapamiętaj mnie", **self.textStyle[0]), Sg.Checkbox("Tak", pad=(0, 1), key='-CX-'),
                     Sg.Button("Połącz", size=20, pad=((20, 0), (0, 0)), key='-BT-')])

    def run(self, mapa, basicEvent = None):
        map = {
            '-BT-': self.connectButtonClicked,
        }
        super().run(map)

    def connectButtonClicked(self, values):
        login = values['-PORT-']
        ip = values['-IP-']
        if values['-CX-']:
            self.buttonEffect('-BT-', 'Połącz', self.backEndIntegration(ip, login, True))
        else:
            self.buttonEffect('-BT-', 'Połącz', self.backEndIntegration(ip, login, False))

    def backEndIntegration(self, ip, port, check):
        dataJSON = {"WERSJA": "G1.0", "ZALOGOWANY": check, "IP": ip, "PORT": port.int()}
        checkingJS = Jsc.FatherJSON("configJSON", dataJSON)
        checkingJS.writeJSON()
        self.close()
        myMenu = MenuRaspberry(ip, port)
        myMenu.gui(None)


# Klasa odpowiedzialna za menu wyboru kolorów
class ColorMenu(Szkielet):
    def __init__(self):
        pole = (150, 150)
        textLength = [(22, 1), (36, 1)]
        self.selectedColor = None
        self.colors = ['Czarny', 'Cyjan', 'Magenta', 'Żółty', 'Niebieski', 'Czerwony']
        super().__init__(pole, textLength)

    def gui(self, *args):
        super().gui([Sg.Text('Wybierz kolor frezu')],
                    [Sg.Listbox(values=self.colors, size=(100, 4),
                                select_mode=Sg.LISTBOX_SELECT_MODE_SINGLE, key='-COLORLIST-')],
                    [Sg.Button('Potwierdź', size=14, key='-BC-')])
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
    def __init__(self, ip, port):
        self.iteracja = 1
        self.angle = 0
        self.colorCutter = ""
        self.ip, self.port = ip, port
        self.lightsList = [0, 0, 0, 0]
        self.rgb = [0, 0, 0]
        size = (350, 600)
        textLength = [(22, 1), (36, 1)]
        readJSONFile = Jsc.ToolsJSON()
        self.toolList = readJSONFile.readJSON()
        self.checkIfNewTool = 0
        super().__init__(size, textLength)

    def gui(self, *args):
        super().gui([Sg.Text("Czy jest to nowe narzędzie? ", **self.textStyle[0]),
                     Sg.Radio("Tak", "RADIO", enable_events=True, default=False, key="-YES-"),
                     Sg.Radio("Nie", "RADIO", enable_events=True, default=True, key="-NO-")],
                    [Sg.Text("Wprowadź lub wybierz z listy nazwę narzędzia", key="-TXT-", visible=True)],
                    [Sg.InputCombo(self.toolList, size=(32, 1), key="-COMBO-", readonly=True),
                     Sg.Button("Potwierdź", size=(8, 1), key="-CONFIRM-", disabled=False)],
                    [Sg.Text("Wybierz ścieżkę zapisu pliku na komputerze")],
                    [Sg.Input(key="-FOLDER-", enable_events=True, **self.textStyle[1]),
                     Sg.FolderBrowse(button_text="Wybierz", key="-BROWSE-")],
                    [Sg.Text("Określ liczbę zdjęć do wykonania")],
                    [Sg.Input(key="-ANGLE-", enable_events=True, size=(34, 1)),
                     Sg.Button("Potwierdź", size=(8, 1), key="-ANGLECONFIRM-", disabled=False)],
                    [Sg.Text(f"Aktualny kąt obrotu ostrza: {self.angle} stopni",
                             **self.textStyle[1], key="-ANGLEOUTPUT-")],
                    [Sg.Frame('Lewe oświetlenie', [
                        [Sg.Slider(range=(-8, 8), size=(11, 16), default_value=0, orientation='h', key='-XL-'),
                         Sg.Slider(range=(-4, 4), size=(4, 16), orientation="v", default_value=0, key='-YL-')]
                    ]),
                     Sg.Frame('Prawe oświetlenie', [
                         [Sg.Slider(range=(-8, 8), size=(11, 16), default_value=0, orientation='h', key='-XP-'),
                          Sg.Slider(range=(-4, 4), size=(4, 16), orientation="v", default_value=0, key='-YP-')]
                     ])
                     ],
                    [Sg.Frame('Poziom jasności', [
                        [Sg.Slider(range=(0, 255), default_value=0, orientation='h', key='-HL-', expand_x=True),
                         ]], expand_x=True)],
                    [Sg.Button("Wykonaj zdjęcie", size=(8, 5), key="-PICTURE-", disabled=True),
                     Sg.Button("Ustaw światło", size=(8, 5), key="-LIGHTBUTTON-"),
                     Sg.Button(f"Wybierz kolor frezu {self.colorCutter}", size=(8, 5), key="-COLORBUTTON-"),
                     Sg.Button("Podgląd zdjęcia", size=(8, 5), key="-SHOWPICTURE-", disabled=True)],
                    [Sg.Text(f"Zalogowano do: {self.ip}", key="-TXTLOGGED-"), Sg.Push(),
                     Sg.Button("Wyloguj", size=(7, 1), key="-LOGOUT-", button_color=("white", "red"))],
                    [Sg.Button("pod", size=(7, 1), key="-P-", button_color=("white", "red"))])

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
            path = Jsc.PathJSON()
            path.writeJSON(self.folderPath)

        # Przycisk odpowiedzialny za oświetlenie
        def lights(values):
            self.lightsList.clear()
            for light in ['-XL-', '-YL-', '-XP-', '-YP-', '-HL-']:
                self.lightsList.append(values[light])
            self.lightsList.extend(self.rgb)
            createJson = Jsc.LightsJSON({"Lights": self.lightsList})
            path = createJson.writeJSON()

            # Połączenie z socketem
            send = Be.Sending(check["IP"], check["PORT"])
            files = ["lightsAndIterationJSON.json", "lights.py", "lights2.py"]

            for file in files:
                thread = Thread(target=send.sendFile, args=(f"{path}\\{file}",), daemon=True)
                thread.start()
                thread.join()
                time.sleep(0.5)

            commands = ["sudo python3 /home/pi/received_files/lights.py",
                        "sudo python3 /home/pi/received_files/lights2.py"]

            for cmd in commands:
                Thread(target=send.sendCommand, args=(cmd,), daemon=True).start()
                time.sleep(0.5)


        # Przycisk odpowiadający za podgląd zdjęć
        def showPicture(_):
            # noinspection PyUnresolvedReferences
            pictureName = f'{self.txt}'
            send = Be.Sending(check["IP"], check["PORT"])
            read = Jsc.FatherJSON("toolsJSON", None)
            # noinspection PyUnresolvedReferences
            hereFolder = read.readJSON()[self.txt.upper()].get("PATH", "")
            # noinspection PyUnresolvedReferences
            x = Thread(target=send.receiveImage, args=(f"{hereFolder}/{self.txt}", self.enteredAngle,
                                                    f'/home/pi/{pictureName.upper()}', self.iteracja), daemon=True)
            x.start()
            x.join()
            # noinspection PyUnresolvedReferences
            photoMenu = PictureMenu(self.txt)
            photoMenu.gui()

        # Przycisk odpowiadajacy za menu wyboru koloru frezu
        def colorMenu(_):
            # changing name zmienia nazwę na kontrastowe RGB
            myColor = ColorMenu()
            color = myColor.gui()
            self.rgb = Be.changingNameToRGB(color)

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
                Sg.popup_error('Błędna wartość')

        # Przycisk odpowiadający za wykonywanie zdjęć
        def picture(_):
            # noinspection PyUnresolvedReferences
            pictureName = f'{self.txt}'   #Nazwa folderu z nazwą narzędzia
            photoFolder = Jsc.LightsJSON({"Folder": f'/home/pi/{pictureName.upper()}'})
            photoFolder.appendJSON()
            if self.checkIfNewTool == 0:        # Jeżeli nie jest to nowe narzędzie to dodaje do listy toolsjson
                # noinspection PyUnresolvedReferences
                appendToJSON = Jsc.AppendJSON(self.txt.upper(), [self.lightsList], [self.rgb])
                self.iteracja = appendToJSON.readJSON()
                # noinspection PyUnresolvedReferences
                photoIteration = Jsc.LightsJSON({"LiczbaZdjec": self.enteredAngle, "Iteracja": self.iteracja})
                photoIteration.appendJSON()         # Json wysyłany na RPI

            else:           #jeżeli nowe narzędzie to tworzy nowy key w jsonie
                try:
                    # noinspection PyUnresolvedReferences
                    photoIteration = Jsc.LightsJSON({"LiczbaZdjec": self.enteredAngle, "Iteracja": self.iteracja})
                    photoIteration.appendJSON()
                except FileNotFoundError:
                    Sg.popup_error(FileNotFoundError)
                except Exception as e:
                    # noinspection PyUnresolvedReferences
                    if self.enteredAngle is None:
                        Sg.popup_error(f"Wprowadź liczbę zdjęć")
                    else:
                        pass
                self.checkIfNewTool -= 1        # Unika się nadpisywania tylko przechodzi do appendu
                jsonLights = Jsc.ToolsJSON()
                # noinspection PyUnresolvedReferences
                jsonLights.writeJSON(settings=[self.lightsList], color=[self.rgb],
                                     name=self.txt, iteracja=self.iteracja, path=self.folderPath, liczba=self.enteredAngle)
                # noinspection PyUnresolvedReferences
                Be.createFolder(rf"{self.folderPath}\{self.txt}")

            path = photoIteration.returnPath()
            send = Be.Sending(check["IP"], check["PORT"])

            def sendFileToRPI(file_path, sleep_time=0.5):
                thread = Thread(target=send.sendFile, args=(file_path,), daemon=True)
                thread.start()
                thread.join()
                time.sleep(sleep_time)

            def sendCommandToRPI(command, sleep_time=0.5):
                thread = Thread(target=send.sendCommand, args=(command,), daemon=True)
                thread.start()
                thread.join()
                time.sleep(sleep_time)

            sendFileToRPI(f"{path}\\lightsAndIterationJSON.json")
            sendCommandToRPI(f'mkdir /home/pi/{pictureName.upper()}')
            sendFileToRPI(f"{path}\\Camera.py")
            sendCommandToRPI("sudo python3 /home/pi/received_files/Camera.py")
            sendCommandToRPI(f"sudo rm -r /home/pi/sendedFile.json")
            self["-ANGLECONFIRM-"].update(disabled=True)

        def pod(values):
            send = Be.Sending(check["IP"], check["PORT"])
            thread = Thread(target=send.previewImage, args=('xd',), daemon=True)
            thread.start()
            thread.join()


        # przycisk potwierdzający wybór narzędzia
        def confirm(values):
            self.txt = values["-COMBO-"]        # Pobranie wartości z comboboxa
            if bool(self.txt):
                confirmButton = Jsc.toolsConfirm(self.txt)
                self.actually = confirmButton.readJSON()
                self.toolList = self.actually
                self["-COMBO-"].update(values=list(self.toolList.keys()))
                self["-COMBO-"](self.txt)
                self["-PICTURE-"].update(disabled=False)
                self["-SHOWPICTURE-"].update(disabled=False)
                try:
                    self["-FOLDER-"].update(value=self.actually[self.txt.upper()]["PATH"])
                    result = "ILOSCZDJEC" in self.actually[self.txt.upper()] and \
                             self.actually[self.txt.upper()]["ILOSCZDJEC"] is not None
                    self["-ANGLECONFIRM-"].update(disabled=result)
                    self["-ANGLE-"].update(self.actually[self.txt.upper()]["ILOSCZDJEC"])
                    self.enteredAngle = self.actually[self.txt.upper()]["ILOSCZDJEC"]
                except KeyError:
                    pass
            else:
                Sg.popup_error("Zdefiniuj narzędzie")


        # przycisk wyloguj
        def logout(_):
            x = Jsc.DeleteConfig()
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
            "-P-":pod,
        }

        super().run(mapa)

    def backEndIntegration(self):
        pass


# Klasa odpowiedzialna za wyświetlanie zdjec
class PictureMenu(Szkielet):
    def __init__(self, txt):
        keyRead = Jsc.FatherJSON("toolsJSON", None)
        keyPath = keyRead.readJSON()
        self.txt = txt.upper()
        self.photoFolder = f"{keyPath[str(self.txt)]['PATH']}/{self.txt}"
        self.iconPath = f"{keyPath[str(self.txt)]['PATH']}/{self.txt}_icon"
        self.lightSlider = keyPath[str(self.txt)]["ITERACJA"]
        self.photoSlider = keyPath[str(self.txt)]["ILOSCZDJEC"]
        self.defaultPhoto = f"{self.photoFolder}\\1_zdjecie_1.png"
        self.pictureIndex, self.pictureLight, self.maxNumber = 1, 1, 1
        pole = (830, 810)
        textLength = [(22, 1), (36, 1)]
        self.changeJPGtoPNG()
        self.resizeImage()
        super().__init__(pole, textLength)
        self.num_columns = 30


    def resizeImage(self):
        inputFolder = self.photoFolder
        outputFolder = os.path.join(os.path.dirname(inputFolder), os.path.basename(inputFolder) + "_icon")
        # Sprawdź, czy folder "icon" istnieje i jeśli nie, to go utwórz
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)
        # Utwórz listę plików w folderze "icon"
        existing_icon_files = os.listdir(outputFolder)
        # Przechodź przez pliki w folderze wejściowym
        for filename in os.listdir(inputFolder):
            if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                input_path = os.path.join(inputFolder, filename)
                output_path = os.path.join(outputFolder, filename)
                # Sprawdź, czy plik już istnieje w folderze "icon"
                if filename not in existing_icon_files:
                    # Otwórz obraz
                    with Image.open(input_path) as img:
                        new_width = 24
                        new_height = 24
                        resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)
                        # Zapisz zmniejszony obraz w folderze "icon"
                        resized_img.save(output_path)

    # Gdyby były przesłane jako JPG a nie PNG
    def changeJPGtoPNG(self):
        # Konwersja jpg na png
        for filename in os.listdir(self.photoFolder):
            if filename.endswith(".jpg"):
                jpgPath = os.path.join(self.photoFolder, filename)
                pngPath = os.path.splitext(jpgPath)[0] + ".png"
                try:
                    jpg_image = Image.open(jpgPath)
                    jpg_image.save(pngPath, "PNG")
                    jpg_image.close()
                    os.remove(jpgPath)
                except Exception as e:
                    Sg.popup_error(f"Błąd podczas konwersji i usuwania pliku {jpgPath}: {e}")

        # Liczenie plików PNG
        if os.path.exists(self.photoFolder) and os.path.isdir(self.photoFolder):
            for filename in os.listdir(self.photoFolder):
                if filename.endswith(".png"):
                    try:
                        number = int(filename[len("1_zdjecie_"):filename.find(".png")])
                        self.maxNumber = max(self.maxNumber, number)
                    except ValueError:
                        Sg.popup_error(f"Błąd podczas przetwarzania pliku {filename}: Nie można odczytać numeru.")

    def gui(self, *args):
        super().gui([
            [Sg.Text("Aktualnie wyświetlane narzędzie")],
            [Sg.Image((os.path.join(self.photoFolder, f"{1}_zdjecie_{1}.png")),
                      key="cutterGuardingGauge", expand_x=True), ],
            [Sg.Slider(range=(1, self.photoSlider), default_value=1, orientation='h', key='-SP-', enable_events=True,
                       expand_x=True), ],
            [Sg.Slider(range=(1, self.lightSlider), default_value=1, orientation='h', key='-SL-', enable_events=True,
                       expand_x=True)],
            [[Sg.Button(pad=((3, 0), (10, 0)),
                        image_filename=os.path.join(self.iconPath, f"1_zdjecie_{i}.png"),
                        key=f"BT{i}", border_width=0, enable_events=True, metadata=i)
              for i in range(1, self.num_columns + 1)]]])

    def run(self, mapa, basicEvent=None):

        def pictureSlider(values):
            self.pictureIndex = int(values['-SP-'])
            self.updatePicture()

        def lightSlider(values):
            self.pictureLight = int(values['-SL-'])
            self.updatePicture()
            self.updateButtonPicture()

        def testowe(x, w):
            self._window_that_exited['-SP-'].update(x)
            self.pictureIndex = int(x)
            self.updatePicture()

        map = {
            '-SP-': pictureSlider,
            '-SL-': lightSlider,
        }

        for i in range(1, self.num_columns + 1):
            map[f"BT{i}"] = partial(testowe, i)

        super().run(map)

    # Metoda do zmiany PNG na BIO
    def changePNGtoBIO(self, image_path):
        originalImage = Image.open(image_path)
        bio = io.BytesIO()
        originalImage.save(bio, format="PNG")
        return bio.getvalue()

    # Update pokazywanych zdjęć
    def updatePicture(self):
        photoPath = os.path.join(self.photoFolder, f'{self.pictureLight}_zdjecie_{self.pictureIndex}.png')
        photoImage = self.changePNGtoBIO(photoPath)
        self._window_that_exited["cutterGuardingGauge"].update(data=photoImage)

    # Aktualizacja obrazów w przyciskach
    def updateButtonPicture(self):
        for i in range(1, self.num_columns + 1):
            buttonKey = f"BT{i}"
            buttonImagePath = os.path.join(self.iconPath, f"{self.pictureLight}_zdjecie_{i}.png")
            self._window_that_exited[buttonKey].update(image_filename=buttonImagePath)

    def backEndIntegration(self, kolor):
        pass

def main():
    myGui = PolaczenieRaspberry()
    myGui.checkConfiguration()

if __name__ == "__main__":
    main()