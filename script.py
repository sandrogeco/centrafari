import os
import sys
import cv2
import tkinter as tk
import PIL
from PIL import ImageTk
import numpy as np
import time
import socket
import threading
from queue import Queue

#from MW28912_originale import end_col


############################################################################################

def get_colore(colore: str):
    if colore == "red":
        return (255, 0, 0)
    if colore == "yellow":
        return (255, 255, 0)
    if colore == "green":
        return (0, 255, 0)
    if colore == "blue":
        return (0, 0, 255)
    if colore == "gold":
        return (255, 215, 0)
    if colore == "cyan":
        return (0, 255, 255)
    if colore == "saddlebrown":
        return (139, 69, 19)
    if colore == "white":
        return (255, 255, 255)
    raise ValueError()


def controlla_colore_pixel(pixel, colore):
    colore_rgb = get_colore(colore)
    return (
        pixel[0] == colore_rgb[0]
        and pixel[1] == colore_rgb[1]
        and pixel[2] == colore_rgb[2]
    )


def disegna_pallino(frame, punto, raggio, colore, spessore):
    cv2.circle(frame, punto, raggio, get_colore(colore), spessore)


def disegna_segmento(frame, punto1, punto2, spessore, colore):
    cv2.line(
        frame,
        (int(punto1[0]), int(punto1[1])),
        (int(punto2[0]), int(punto2[1])),
        get_colore(colore),
        spessore,
    )


def disegna_croce(frame, punto, larghezza, spessore, colore):
    disegna_segmento(
        frame,
        (punto[0] - larghezza, punto[1]),
        (punto[0] + larghezza, punto[1]),
        spessore,
        colore,
    )
    disegna_segmento(
        frame,
        (punto[0], punto[1] - larghezza),
        (punto[0], punto[1] + larghezza),
        spessore,
        colore,
    )


def disegna_croci(frame, punti, larghezza, spessore, colore):
    for punto in punti:
        disegna_croce(frame, punto, larghezza, spessore, colore)


def disegna_linea(frame, punti, spessore, colore):
    for i in range(0, len(punti) - 1):
        disegna_segmento(frame, punti[i], punti[i + 1], spessore, colore)


def disegna_rettangolo(frame, punto_ll, punto_ur, spessore, colore):
    min_x = punto_ll[0]
    max_x = punto_ur[0]
    min_y = punto_ll[1]
    max_y = punto_ur[1]
    disegna_segmento(frame, (min_x, min_y), (max_x, min_y), spessore, colore)
    disegna_segmento(frame, (min_x, min_y), (min_x, max_y), spessore, colore)
    disegna_segmento(frame, (min_x, max_y), (max_x, max_y), spessore, colore)
    disegna_segmento(frame, (max_x, min_y), (max_x, max_y), spessore, colore)

############################################################################################

WHITE = (255, 255, 255)[::-1]
BLACK = (0, 0, 0)[::-1]
RED = (255, 0, 0)[::-1]
GREEN = (0, 255, 0)[::-1]
BLUE = (0, 0, 255)[::-1]

def find_y_by_x(contour, x):
    c = contour[:, 0, :]
    nearest_point = min(c, key=lambda p: abs(p[0] - x))
    return nearest_point[1]

def somma_vettori(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def differenza_vettori(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def angolo_vettori(v1, v2):
    x1, y1 = v1
    x2, y2 = v2

    dot = x1 * x2 + y1 * y2
    det = x1 * y2 - y1 * x2
    return np.arctan2(det, dot) * 180 / np.pi

def angolo_esterno_vettori(v1, v2):
    return angolo_vettori(differenza_vettori((0, 0), v1), v2)

def preprocess(image):
    height, width = image.shape[:2]

    # Ritaglia immagine
    CROP_W = 500
    CROP_H = 200
    image = image[int(height/2 - CROP_H/2):int(height/2 + CROP_H/2), int(width/2 - CROP_W/2):int(width/2 + CROP_W/2)]

    image = cv2.resize(image, (0, 0), fx=1, fy=2)

    return image

def rileva_contorno_1(image, cache=None):
    if cache is None:
        cache = {}

    def pullapart(v):
        vs = 250
        v = v - 2 * np.sign(v - vs) * (np.abs(v - vs) ** 0.6)
        v = np.clip(v, 0, 255).astype(np.uint8)
        return v

    if 'lut' not in cache:
        cache['lut'] = np.array([pullapart(d) for d in range(256)], dtype=np.uint8)

    image1 = cv2.LUT(image, cache['lut'])

    # Sembra che THRESH_OTSU funzioni abbastanza meglio di THRESH_BINARY, cioe' il contorno che viene
    # # fuori e' meno influenzato dalla haze nell'immagine e piu' vicino al bordo vero
    _, binary_image = cv2.threshold(image1, 0, 255, cv2.THRESH_OTSU)

    edges = cv2.Canny(binary_image, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("   contours vuoto")
        return None, '[rileva_contorno_1], contours vuoto'

    # return max(contours, key=cv2.contourArea), None
    return max(contours, key=lambda d: cv2.arcLength(d, False)), None

def rileva_punto_angoloso(image_input, image_output, cache=None):
    WIDTH_PIXEL = image_input.shape[1]

    # Rileva contorno
    contour, err = rileva_contorno_1(image_input, cache)
    if contour is None or err is not None:
        return image_input, None,'[rileva_punto_angoloso] contour is None'

    # Analisi contorno
    cv2.drawContours(image_output, [contour], -1, RED, 1)

    delta = 20
    punti = []

    for p in range(delta, 100 - delta, 1):
        p_prec = p - delta
        p_succ = p + delta

        x_prec = int(0.01 * p_prec * WIDTH_PIXEL)
        x = int(0.01 * p * WIDTH_PIXEL)
        x_succ = int(0.01 * p_succ * WIDTH_PIXEL)

        y_prec = find_y_by_x(contour, x_prec)
        y = find_y_by_x(contour, x)
        y_succ = find_y_by_x(contour, x_succ)
        if y_prec is None or y is None or y_succ is None:
            continue

        OFFSET_Y = 5

        v_prec = (x_prec, y_prec + OFFSET_Y)
        v = (x, y + OFFSET_Y)
        v_succ = (x_succ, y_succ + OFFSET_Y)

        angolo = -angolo_esterno_vettori(differenza_vettori(v_prec, v), differenza_vettori(v_succ, v))

        v_prec_verso_alto = angolo_vettori((1, 0), differenza_vettori(v_prec, v)) > 0

        if 5 < angolo < 20 and v_prec_verso_alto:
            punti.append(v)
            cv2.circle(image_output, v, 2, GREEN, -1)
            # Decommenta queste due o tre linee sotto per visualizzare i vettori che danno l'angolo e per scrivere l'angolo
            # cv2.line(image_output, v_prec, v, GREEN, 1)
            # cv2.line(image_output, v, v_succ, GREEN, 1)
            # cv2.putText(image_output, f'{int(angolo)}', somma_vettori(v, (10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN, 1)

    # Rimuovo i punti che sono troppo vicini alle estremita' del contour
    min_contour_x = np.min(contour[:, 0, 0])
    max_contour_x = np.max(contour[:, 0, 0])
    range_contour_x = max_contour_x - min_contour_x
    punti = [p for p in punti if min_contour_x + (0.05 * range_contour_x) < p[0] < max_contour_x - (0.05 * range_contour_x)]

    if len(punti) == 0:
        return image_output,None, '[rileva_punto_angoloso] nessun punto trovato'

    for punto in punti:
        cv2.circle(image_output, punto, 2, GREEN, -1)

    punto_finale = tuple(np.median(punti, axis=0).astype(np.int32))
    cv2.circle(image_output, punto_finale, 6, GREEN, -1)

    return image_output, punto_finale,None


def visualizza_croce_riferimento(frame,x,y,width,heigth):
    disegna_croce(frame,(x-width/2,y-heigth/2),1000,1,'green')
    disegna_croce(frame, (x + width / 2, y + heigth / 2),1000, 1, 'green')

############################################################################################

WINDOW_SHIFT_X = 278
WINDOW_SHIFT_Y = 130
WINDOW_WIDTH = 630
WINDOW_HEIGHT = 320
IP='127.0.0.1'
PORT=28500

q = Queue()




MCORR=np.array([[1.19962087e+00, 3.03070135e-01, -6.59806746e+01],
           [5.05979992e-03, 1.64790684e+00, -7.66065165e+01],
           [-1.08610130e-04, 1.09172033e-03, 1.00000000e+00]])

def show_frame(video, cache, lmain):
    _, image_input = video.read()

    image_input= cv2.warpPerspective(image_input, MCORR, (image_input.shape[1],image_input.shape[0]))
    t0 = time.monotonic()

    image_input = cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
    # image_input = preprocess(image_input)
    image_output = cv2.cvtColor(image_input.copy(), cv2.COLOR_GRAY2BGR)
    image_output,point, err = rileva_punto_angoloso(image_input, image_output, cache)
    if point:
        q.put({
            'posiz_pattern_x': point[0],
            'posiz_pattern_y': point[1],
            'lux': 0})


    disegna_rettangolo(image_output, (320-20, 220-20), (320+20, 220+20), 2, 'red')
    visualizza_croce_riferimento(image_output,300,150,50,70)

    t1 = time.monotonic()

    print(f"Durata elaborazione: {1000 * (t1 - t0)} ms, fps = {1 / (t0 - cache.get('t0', 0))}")
    cache['t0'] = t0

    img = PIL.Image.fromarray(image_output)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(50, lambda: show_frame(video, cache, lmain))


def set_camera(i,type='anabbagliante'):
    video_device='/dev/video'+str(i)
    print('set '+video_device)
#   os.system("v4l2-ctl --device "+video_device+" --list-ctrls")
    try:
        if type=='anabbagliante':
            os.system("v4l2-ctl --device "+video_device+" --set-ctrl=exposure_auto=1")
            os.system("v4l2-ctl --device " + video_device + " --set-ctrl=brightness=0")
            os.system("v4l2-ctl --device " + video_device + " --set-ctrl=contrast=100")
            os.system("v4l2-ctl --device " + video_device + " --set-ctrl=saturation=0")
            os.system("v4l2-ctl --device " + video_device + " --set-ctrl=exposure_absolute=400")

        if type=='abbagliante':
            os.system("v4l2-ctl --device "+video_device+" --set-ctrl=exposure_auto=1")
            os.system("v4l2-ctl --device " + video_device + " --set-ctrl=brightness=0")
            os.system("v4l2-ctl --device " + video_device + " --set-ctrl=contrast=0")
            os.system("v4l2-ctl --device " + video_device + " --set-ctrl=saturation=0")
            os.system("v4l2-ctl --device " + video_device + " --set-ctrl=exposure_absolute=50")
        print('pippo1')
        os.system("v4l2-ctl --device " + video_device + " --list-ctrls")
    except Exception as e:
        print(e)


def init_com():
    while True:
        try:
            client_socket = socket.socket()
            client_socket.bind((IP, PORT))
            client_socket.listen(1)
            print(f"[+] In ascolto su {IP}:{PORT}...")
            conn, addr = client_socket.accept()
            print(f"[+] Connessione da {addr}")

            t = threading.Thread(target=comunication,args=(conn,), daemon=True).start()
            while True:
                data = conn.recv(1024).decode("UTF-8")
                with open("/tmp/all_msgs.txt", "a") as f:
                    f.write("[RX] " + data + "\n")
            conn.close()
            client_socket.close()
            t.stop()
        except:
            pass



def comunication(conn):
    while True:
        p=q.get()
        #client_socket.connect((IP, PORT))
        msg = "XYL %d %d %f " % (p['posiz_pattern_x'], p['posiz_pattern_y'], p['lux'])

        with open("/tmp/all_msgs.txt", "a") as f:
             f.write("[TX] " + msg + "\n")
        try:

            conn.sendall(msg.encode())  # send message
            #replica_da_Proteus = client_socket.recv(1024).decode("UTF-8")
        except:
            pass
          #  replica_da_Proteus="no risposta da proteus"



       # client_socket.close()







if __name__ == "__main__":
    threading.Thread(target=init_com).start()


    print("nuovo_script")
    type=sys.argv[1].lower()
    # Apri la telecamera
    for i in range(11):
        set_camera(i, type)
        video = cv2.VideoCapture(i)
        if video.isOpened():
            break






    # Imposta la finestra
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{WINDOW_SHIFT_X}+{WINDOW_SHIFT_Y}")
    root.resizable(False, False)
    lmain = tk.Label(root)
    lmain.pack()

    cache: dict = {}

    show_frame(video, cache, lmain)
    root.mainloop()

