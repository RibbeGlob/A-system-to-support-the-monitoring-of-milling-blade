import json
import os
import time
from picamera2 import Picamera2, Preview
import RPi.GPIO as GPIO

def readJSON():
    jsonFile = 'lightsAndIterationJSON'
    path = os.path.dirname(__file__)  # Tworzenie ścieżki do obecnego folderu
    jsonPath = os.path.join(path)
    with open(f"{jsonPath}/{jsonFile}.json", "r") as fileJSON:
        data = json.load(fileJSON)
    listData = [data["LiczbaZdjec"], data["Folder"], data["Iteracja"]]
    return(listData)


def takePhoto(data):
    try:
        picam2 = Picamera2()
        preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})
        picam2.shutter_speed = 2
        picam2.configure(preview_config)
        picam2.start()
        time.sleep(2)

        # # Konfiguracja pinów GPIO
        # trigger_pin = 17  # Przykładowy numer pinu GPIO
        # stop_pin = 18  # Przykładowy numer pinu GPIO
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(trigger_pin, GPIO.OUT)
        # GPIO.setup(stop_pin, GPIO.IN)

        for i in range(data[0]):
            metadata = picam2.capture_file(data[1] + f'/{data[2]}_zdjecie_{i + 1}.png')

            # # Wyślij sygnał z pinu trigger_pin
            # GPIO.output(trigger_pin, GPIO.HIGH)
            # GPIO.output(trigger_pin, GPIO.LOW)
            # # Zatrzymaj iterację do czasu odebrania sygnału z pinu stop_pin
            # while not GPIO.input(stop_pin):
            #     time.sleep(0.1)

    except Exception as ex:
        print(f"Błąd podczas robienia zdjęć: {ex}")
    finally:
        # Zakończ i wyczyść GPIO
        GPIO.cleanup()


data = readJSON()
takePhoto(data)