import picamera
import json
import os
# dodać folder zapisu

def readJSON():
    jsonFile = 'lightsAndIterationJSON'
    path = os.path.dirname(__file__)  # Tworzenie ścieżki do obecnego folderu
    jsonPath = os.path.join(path)
    with open(f"{jsonPath}/{jsonFile}.json", "r") as fileJSON:
        data = json.load(fileJSON)
    listData = [data["LiczbaZdjec"], data["Folder"]]
    return(listData)

def takePhoto(data):
    try:
        with picamera.PiCamera() as camera:
            camera.resolution = (1920, 1080)
            camera.framerate = 30
            camera.shutter_speed = 33333# Przykładowa wartość 1/1000 sekundy
            for i in range(data[0]):
                camera.capture(f'{data[1]}/zdjecie_{i + 1}.jpg', use_video_port=True)
    except Exception as ex:
        print(f"Błąd podczas robienia zdjęć: {ex}")

data = readJSON()
takePhoto(data)


