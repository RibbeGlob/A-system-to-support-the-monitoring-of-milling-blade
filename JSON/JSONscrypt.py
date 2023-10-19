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
                json.dump(self.data, fileJSON)
        except FileNotFoundError:
            sg.popup_error("Error plik JSON nie istnieje")
        except json.decoder.JSONDecodeError:
            sg.popup_error("Error plik JSON jest uszkodzony")
        except Exception as e:
            sg.popup_error(f"Wystąpił nieoczekiwany błąd: {str(e)}")

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
        self.data[self.keyName]["USTAWIENIE"].append([self.configuration])
        self.data[self.keyName]["KOLOR"].append([self.color])
        increment = lambda: self.data[self.keyName].update(ITERACJA=self.data[self.keyName]["ITERACJA"] + 1)
        increment()
        super().writeJSON()


    def readJSON(self):
        self.data = super().readJSON()
        self.writeJSON()


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
                   "ITERACJA": kwargs["iteracja"], "PATH": kwargs["path"]}
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
            firstKey = next(iter(self.check))
            self.check.pop(firstKey, None)      #usuniecie klucza
            self.data = self.check
            super().writeJSON()
            return self.data
        except StopIteration:
            print("Pusty")

    def writeJSON(self):
        empty = {
        }
        self.check[self.name.upper()] = empty


class LightsJSON(FatherJSON):
    def __init__(self, data):
        super().__init__("lightsJSON", data)
        self.jsonPath = f"{self.jsonPath[:-4]}Lights"

    def writeJSON(self):
        super().writeJSON()
        return self.jsonPath

