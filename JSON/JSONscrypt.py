import json
import os

class FatherJSON:
    def __init__(self, jsonFile, data):
        self.jsonFile = jsonFile
        self.data = data
        path = os.path.dirname(__file__)        #Tworzenie ścieżki do obecnego folderu
        self.jsonPath = os.path.join(path)

    # Tworzenie nowego pliku JSON
    def writeJSON(self):
        with open(f"{self.jsonPath}\\{self.jsonFile}.json", "w") as fileJSON:
            json.dump(self.data, fileJSON)
            print('xd')

    # Czytanie pliku JSON
    def readJSON(self):
        with open(f"{self.jsonPath}\\{self.jsonFile}.json", "r") as fileJSON:
            return json.load(fileJSON)

# JSON do ścieżki
class PathJSON(FatherJSON):
    def __init__(self):
        super().__init__("configJSON", None)

    def writeJSON(self, *args):
        self.data = super().readJSON()
        self.data["PATH"] = args[0]
        super().writeJSON()


class ToolsJSON(FatherJSON):
    def __init__(self):
        super().__init__("toolsJSON", None)

    # Pisanie daty do stworzonego pliku JSON (NIE TWORZYMY NOWEGO)
    def writeJSON(self, **kwargs):
        newTool = {"USTAWIENIE": kwargs["settings"], "KOLOR": kwargs["color"]}
        self.data = super().readJSON()
        self.data[kwargs["name"].upper()] = newTool
        super().writeJSON()

    # Czytanie pliku JSON
    def readJSON(self):
        try:
            readData = super().readJSON()
            klucze = list(readData.keys())
            return klucze
        except FileNotFoundError:
            print("Error plik JSON nie istnieje")
        except json.decoder.JSONDecodeError:
            print("Error plik JSON jest uszkodzony")


# odblokuj mozliwosc po zatwierdzeniu nazwy
class toolsConfirm(FatherJSON):
    def __init__(self, data):
        super().__init__("toolsJSON", None)
        self.name = data

    def readJSON(self):
        try:
            self.check = super().readJSON()
            self.writeJSON()
            if len(self.check) >= 4:
                actually = self.deleteJSON()
                return actually
            else:
                self.data = self.check
                super().writeJSON()
                return self.data
        except FileNotFoundError:
            print("Error plik JSON nie istnieje")
        except json.decoder.JSONDecodeError:
            print("Error plik JSON jest uszkodzony")

    def deleteJSON(self):
        try:
            firstKey = next(iter(self.check))
            self.check.pop(firstKey, None)
            self.data = self.check
            super().writeJSON()
            return self.data
        except StopIteration:
            print("Pusty")

    def writeJSON(self):
        empty = {
            "USTAWIENIE": [],
            "KOLOR": []
        }
        self.check[self.name.upper()] = empty








