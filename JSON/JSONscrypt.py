import json
import os
import PySimpleGUI as sg


class FatherJSON:
    def __init__(self, jsonFile, data):
        self.jsonFile = jsonFile
        self.data = data
        path = os.path.dirname(__file__)        #Tworzenie ścieżki do obecnego folderu
        self.jsonPath = os.path.join(path)

    # Tworzenie nowego pliku JSON
    def writeJSON(self):
        try:
            with open(f"{self.jsonPath}\\{self.jsonFile}.json", "w") as fileJSON:
                json.dump(self.data, fileJSON, indent=1)
        except FileNotFoundError:
            sg.popup_error("Error plik JSON nie istnieje")
        except json.decoder.JSONDecodeError:
            sg.popup_error("Error plik JSON jest uszkodzony")
        except Exception as e:
            sg.popup_error(f"Wystąpił nieoczekiwany błąd: {str(e)}")
        finally:
            if 'fileJSON' in locals() and not fileJSON.closed:
                fileJSON.close()
    # Czytanie pliku JSON
    def readJSON(self):
        try:
            with open(f"{self.jsonPath}\\{self.jsonFile}.json", "r") as fileJSON:
                return json.load(fileJSON)
        except FileNotFoundError:
            sg.popup_error("Error plik JSON nie istnieje")
        except json.decoder.JSONDecodeError:
            sg.popup_error("Error plik JSON jest uszkodzony")
        except Exception as e:
            sg.popup_error(f"Wystąpił nieoczekiwany błąd: {str(e)}")


class AppendJSON(FatherJSON):
    def __init__(self, keyName, configuration, color):
        self.keyName = keyName
        self.configuration = configuration
        self.color = color
        super().__init__("toolsJSON", None)

    def writeJSON(self):
        self.data[self.keyName]["USTAWIENIE"].extend(self.configuration)
        self.data[self.keyName]["KOLOR"].extend(self.color)
        increment = lambda: self.data[self.keyName].update(ITERACJA=self.data[self.keyName]["ITERACJA"] + 1)
        increment()
        super().writeJSON()


    def readJSON(self):
        self.data = super().readJSON()
        self.writeJSON()
        return self.data[self.keyName]["ITERACJA"]


    # JSON do ścieżki
class PathJSON(FatherJSON):
    def __init__(self):
        super().__init__("configJSON", None)

    def writeJSON(self, *args):
        self.data = super().readJSON()
        self.data["PATH"] = args[0]
        super().writeJSON()


# Klasa odpowiedzialna za usuwanie Klucza w JSONIE
class DeleteConfig(FatherJSON):
    def __init__(self):
        super().__init__("configJSON", None)

    def readJSON(self):
        self.data = super().readJSON()
        self.deleteJSON()

    def deleteJSON(self):
        for key in self.data:
            if key == "WERSJA":
                self.data[key] = "G1.0"
            else:
                self.data[key] = None
        super().writeJSON()


class ToolsJSON(FatherJSON):
    def __init__(self):
        super().__init__("toolsJSON", None)

    # Pisanie daty do stworzonego pliku JSON (NIE TWORZYMY NOWEGO)
    def writeJSON(self, **kwargs):
        newTool = {"USTAWIENIE": kwargs["settings"], "KOLOR": kwargs["color"],
                   "ITERACJA": kwargs["iteracja"], "PATH": kwargs["path"], "ILOSCZDJEC": kwargs["liczba"]}
        self.data = super().readJSON()
        self.data[kwargs["name"].upper()] = newTool
        super().writeJSON()

    # Czytanie pliku JSON
    def readJSON(self):
        readData = super().readJSON()
        klucze = list(readData.keys())
        return klucze


class toolsConfirm(FatherJSON):
    def __init__(self, data):
        super().__init__("toolsJSON", None)
        self.name = data

    def readJSON(self):
        self.check = super().readJSON()
        # self.writeJSON()
        if len(self.check) >= 4:
            actually = self.deleteJSON()
            return actually
        else:
            self.data = self.check
            super().writeJSON()
            return self.data


    def deleteJSON(self):
        try:
            import BackEnd as BE
            from threading import Thread
            firstKey = next(iter(self.check))
            checkingConfiguration = FatherJSON("configJSON", None)
            check = checkingConfiguration.readJSON()
            send = BE.Sending(check["IP"], check["PORT"])
            Thread(target=send.sendData, args=(f"sudo rm -r /home/pi/{firstKey}", 2),
                   daemon=True).start()
            self.check.pop(firstKey, None)      #usuniecie klucza
            self.data = self.check
            super().writeJSON()
            return self.data
        except StopIteration:
            pass

    def writeJSON(self):
        empty = {
        }
        self.check[self.name.upper()] = empty


class LightsJSON(FatherJSON):
    def __init__(self, data):
        super().__init__("lightsAndIterationJSON", data)
        self.jsonPath = f"{self.jsonPath[:-4]}Lights"

    def writeJSON(self):
        super().writeJSON()
        return self.jsonPath

    def appendJSON(self):
        try:
            with open(f"{self.jsonPath}/{self.jsonFile}.json", "r+") as fileJSON:
                try:
                    existing_data = json.load(fileJSON)
                except json.decoder.JSONDecodeError:
                    existing_data = {}  # In case the file is empty or not valid JSON
                # Dodaj nowe dane do istniejącego obiektu JSON
                existing_data.update(self.data)
                # Przejdź na początek pliku, wyczyść zawartość i zapisz zaktualizowane dane
                fileJSON.seek(0)
                fileJSON.truncate()
                json.dump(existing_data, fileJSON, indent=2)
        except FileNotFoundError:
            sg.popup_error(FileNotFoundError)
        except json.decoder.JSONDecodeError:
            sg.popup_error(json.decoder.JSONDecodeError)
        except Exception as e:
            sg.popup_error(f"Wystąpił nieoczekiwany błąd: {str(e)}")

    def returnPath(self):
        return self.jsonPath

