# encoding:utf-8
from rpi_ws281x import Adafruit_NeoPixel, Color
import json
import os
import time

LED_COUNT = 32  # Liczba LED
LED_PIN = 18  # pin GPIO
LED_FREQ_HZ = 800000  # sygnał LED w Hz
LED_DMA = 10  # kanał DMA
LED_INVERT = False

def readJSON(jsonFile):
    path = os.path.dirname(__file__)  # Tworzenie ścieżki do obecnego folderu
    jsonPath = os.path.join(path)
    with open(f"{jsonPath}/{jsonFile}.json", "r") as fileJSON:
        return json.load(fileJSON)

def iteration(row, rowIteration):
    rows = [[*range(0, 8, 1)], [*range(8, 16, 1)], [*range(16, 24, 1)], [*range(24, 32, 1)]]
    realRows = []
    if isinstance(row, float):
        row = round(row)
    if isinstance(rowIteration, float):
        rowIteration = round(rowIteration)
    if row > 0 and rowIteration > 0:
        rowIteration -=1
        while rowIteration >= 0:
            holder = rows[rowIteration]
            realRows.append(holder[0:row])
            rowIteration -=1
    elif row > 0 and rowIteration < 0:
        while rowIteration < 0:
            holder = rows[rowIteration]
            realRows.append(holder[0:row])
            rowIteration +=1
    elif row < 0 and rowIteration > 0:
        rowIteration -= 1
        while rowIteration >= 0:
            holder = rows[rowIteration]
            realRows.append(holder[row:])
            rowIteration -= 1
    elif row < 0 and rowIteration < 0:
        while rowIteration < 0:
            holder = rows[rowIteration]
            realRows.append(holder[row:])
            rowIteration +=1
    listOfLights = []
    for x in realRows:
        listOfLights += x
    return listOfLights

x = readJSON("lightsAndIterationJSON")  # Wczytanie danych konfiguracyjnych
lightsNumber = iteration(x["Lights"][0], x["Lights"][1])
LED_BRIGHTNESS = int(round(x["Lights"][4]))  # Poziom jasności
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

for i in lightsNumber:
    strip.setPixelColor(i, Color(int(round(x["Lights"][5])), int(round(x["Lights"][6])), int(round(x["Lights"][7]))))
    strip.show()

