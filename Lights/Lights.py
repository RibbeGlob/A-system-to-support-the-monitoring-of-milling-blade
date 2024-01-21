# encoding:utf-8
from rpi_ws281x import Adafruit_NeoPixel, Color
import json
import os
import time


#Inicjalizacja biblioteki

def readJSON(jsonFile):
    path = os.path.dirname(__file__)  # Tworzenie ścieżki do obecnego folderu
    jsonPath = os.path.join(path)
    with open(f"{jsonPath}/{jsonFile}.json", "r") as fileJSON:
        return json.load(fileJSON)

def iteration(wiersz, iteracjawiersza):
    rows = [[*range(0, 8, 1)], [*range(8, 16, 1)], [*range(16, 24, 1)], [*range(24, 32, 1)]]
    realRows = []

    if isinstance(wiersz, float):
        wiersz = round(wiersz)
    if isinstance(iteracjawiersza, float):
        iteracjawiersza = round(iteracjawiersza)

    if wiersz > 0 and iteracjawiersza > 0:
        iteracjawiersza -=1
        while iteracjawiersza >= 0:
            holder = rows[iteracjawiersza]
            realRows.append(holder[0:wiersz])
            iteracjawiersza -=1
    elif wiersz > 0 and iteracjawiersza < 0:
        while iteracjawiersza < 0:
            holder = rows[iteracjawiersza]
            realRows.append(holder[0:wiersz])
            iteracjawiersza +=1
    elif wiersz < 0 and iteracjawiersza > 0:
        iteracjawiersza -= 1
        while iteracjawiersza >= 0:
            holder = rows[iteracjawiersza]
            realRows.append(holder[wiersz:])
            iteracjawiersza -= 1
    elif wiersz < 0 and iteracjawiersza < 0:
        while iteracjawiersza < 0:
            holder = rows[iteracjawiersza]
            realRows.append(holder[wiersz:])
            iteracjawiersza +=1

    listOfLights = []
    for x in realRows:
        listOfLights += x
    return listOfLights


x = readJSON("lightsAndIterationJSON")
lightsNumber = iteration(x["Lights"][0], x["Lights"][1])

LED_COUNT = 32  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = int(round(x["Lights"][4]))  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

strip.begin()
for i in lightsNumber:
    strip.setPixelColor(i, Color(int(round(x["Lights"][5])), int(round(x["Lights"][6])), int(round(x["Lights"][7]))))
    strip.show()

