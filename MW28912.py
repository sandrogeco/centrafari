import sys
import cv2
import tkinter as tk
import PIL
from PIL import ImageTk
import time
import threading
from queue import Queue
from functools import partial
import json
import numpy as np

from utils import disegna_rettangolo
from funcs import rileva_punto_angoloso, visualizza_croce_riferimento
from camera import set_camera
from comms import thread_comunicazione
import os

def decode_cmd(resp):
    cmd_da_proteus = {
        'croce': "croce_ON",
        'pattern': "pattern_digital",
        'inclinazione': 0
    }
    if ((resp == 'croce_ON') or (resp == 'croce_OFF')):
        cmd_da_proteus['croce'] = resp

    return cmd_da_proteus


def show_frame(video, cache, lmain):
    _, image_input = video.read()

    image_input= cv2.warpPerspective(image_input, cache['matrice_correzione_prospettiva'], (image_input.shape[1], image_input.shape[0]))
    t0 = time.monotonic()

    image_input = cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
    # image_input = preprocess(image_input)
    image_output = cv2.cvtColor(image_input.copy(), cv2.COLOR_GRAY2BGR)
    image_output, point, _ = rileva_punto_angoloso(image_input, image_output, cache)
    print(point)
    if point:
        cache['queue'].put({ 'posiz_pattern_x': point[0], 'posiz_pattern_y': point[1], 'lux': 0 })
    cmd=decode_cmd(cache['resp'])

    disegna_rettangolo(image_output, (320-20, 220-20), (320+20, 220+20), 2, 'red')
    if cmd['croce'] == 'croce_ON':
        visualizza_croce_riferimento(image_output,300,150,50,70)

    t1 = time.monotonic()

    print(f"Durata elaborazione: {1000 * (t1 - t0)} ms, fps = {1 / (t0 - cache.get('t0', 0))}")
    cache['t0'] = t0

    img = PIL.Image.fromarray(image_output)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(50, lambda: show_frame(video, cache, lmain))


if __name__ == "__main__":

    os.chdir("/home/pi/Applications/")
    tipo_faro = sys.argv[1].lower()

    # Carica la configurazione
    with open(f"config_{tipo_faro}.json", "r") as f:
        config = json.load(f)
    q: Queue = Queue()
    resp=""

    threading.Thread(target=partial(thread_comunicazione, config['ip'], config['port'], q,resp),daemon=True,name="com_in").start()

    # Apri la telecamera
    for i in range(11):
        set_camera(i, tipo_faro)
        video = cv2.VideoCapture(i)
        if video.isOpened():
            break

    # Imposta la finestra
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f"{config['window_width']}x{config['window_height']}+{config['window_shift_x']}+{config['window_shift_y']}")
    root.resizable(False, False)
    lmain = tk.Label(root)
    lmain.pack()

    cache = {
        'matrice_correzione_prospettiva': np.array(config['matrice_correzione_prospettiva']),
        'queue': q,
        'resp':resp,
    }

    show_frame(video, cache, lmain)
    root.mainloop()
