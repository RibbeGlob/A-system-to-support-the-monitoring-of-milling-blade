import PySimpleGUI as sg
import JSON.JSONscrypt as Jsc

def stream(server_ip):
    import cv2
    server_ip = server_ip
    server_port = 8000
    url = f'http://{server_ip}:{server_port}/stream.mjpg'
    cap = cv2.VideoCapture(url)
    layout = [[sg.Image(filename='', key='-IMAGE-')]]
    window = sg.Window('Stream', layout, finalize=True)
    while True:
        event, values = window.read(timeout=0)
        if event == sg.WINDOW_CLOSED:
            break
        ret, frame = cap.read()
        if not ret:
            break
        if frame is not None:
            encoded_image = cv2.imencode('.png', frame)[1].tobytes()
            window['-IMAGE-'].update(data=encoded_image)
    cap.release()
    cv2.destroyAllWindows()
    window.close()


checkingConfiguration = Jsc.FatherJSON("configJSON", None)
check = checkingConfiguration.readJSON()
stream(check["IP"])