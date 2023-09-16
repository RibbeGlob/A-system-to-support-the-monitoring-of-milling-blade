import json

class FatherJSON:
    def __init__(self, jsonFile, data):
        self.jsonFile = jsonFile
        self.data = data

    def writeJSON(self):
        with open(self.jsonFile + ".json", "w") as fileJSON:
            json.dump(self.data, fileJSON)

    def readJSON(self):
        with open(self.jsonFile + ".json", "r") as fileJSON:
            return json.load(fileJSON)

class FirstJSON(FatherJSON):
    def __init__(self, **kwargs):
        super().__init__("testowyjson", {"ZALOGOWANY": kwargs["logged"], "IP": kwargs["ip"],
                                         "NARZEDZIA": [], "ITERATOR": 1})
        self.logged = kwargs["logged"]
        self.ip = kwargs["ip"]

    def writeJSON(self, **kwargs):
        nowe_narzedzie = {"NAZWA": kwargs["name"], "USTAWIENIE": kwargs["settings"], "KOLOR": kwargs["color"]}
        self.data = super().readJSON()
        self.data["NARZEDZIA"].append(nowe_narzedzie)
        super().writeJSON()

    def readJSON(self):
        self.readData = super().readJSON()
        value = self.iteratorCheck()
        return value

    def iteratorCheck(self):
        try:
            value = self.readData["ITERATOR"]
        except KeyError:
            pass
        else:
            return value

class SecondJSON(FatherJSON):
    pass


# Użycie klasy FirstJSON
lol = FatherJSON("testowyjson", {"WERSJA": "G1.0","ZALOGOWANY": True, "IP": 32, "NARZEDZIA": [], "ITERATOR": 0})
lol.writeJSON()
# Użycie klasy FirstJSON
#xd = FirstJSON(logged = False, ip = 3223)
#xd.writeJSON(name = "Frez", settings = (1,3,6,4), color = (32,65,123), iterator = 1)
#sss = xd.readJSON()
#print(sss)


# OSOBNY DO LOGOWANIA JSON I OSOBNY DO NARZEDZI