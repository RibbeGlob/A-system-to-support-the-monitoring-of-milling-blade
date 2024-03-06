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
        picam2.resolution = (4208, 3120)
        picam2.configure(preview_config)
        picam2.start()
        # Przykładowe Piny
        # triggerPin = 17
        # stopPin = 18
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(triggerPin, GPIO.out)
        # GPIO.setup(stopPin, GPIO.IN)
        for i in range(data[0]):
            metadata = picam2.capture_file(data[1] + f'/{data[2]}_zdjecie_{i + 1}.png')
            # GPIO.output(triggerPin, GPIO.HIGH)
            # GPIO.output(triggerPin, GPIO.LOW)
            # while not GPIO.input(stopPin):
            #     time.sleep(0.1)

    except Exception as ex:
        pass
    finally:
        # Zakończ i wyczyść GPIO
        GPIO.cleanup()


data = readJSON()
takePhoto(data)