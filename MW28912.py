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

from funcs import rileva_punto_angoloso, visualizza_croce_riferimento
from camera import set_camera, apri_camera
from comms import thread_comunicazione, cmd_da_proteus
import os


def show_frame(video, cache, lmain):
    t0 = time.monotonic()

    _, image_input = video.read()

    image_input = cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
    # image_input = preprocess(image_input)
    image_output = cv2.cvtColor(image_input.copy(), cv2.COLOR_GRAY2BGR)
    image_output, point, _ = rileva_punto_angoloso(image_input, image_output, cache)

    #    decode_cmd(cache['resp'])
    print(cmd_da_proteus)
    if cmd_da_proteus['croce'] == "croce_ON":
        visualizza_croce_riferimento(image_output, 315, 160+cmd_da_proteus['inclinazione'], cmd_da_proteus['toh'], cmd_da_proteus['toh'])

    if point:
        cache['queue'].put({ 'posiz_pattern_x': point[0], 'posiz_pattern_y': point[1], 'lux': 0 })
    else:
        cache['queue'].put(None)

    print(f"Durata elaborazione: {1000 * (time.monotonic() - t0)} ms, fps = {1 / (t0 - cache.get('t0', 0))}", flush=True)
    cache['t0'] = t0

    img = PIL.Image.fromarray(image_output)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, lambda: show_frame(video, cache, lmain))


if __name__ == "__main__":
    try:
        os.chdir("/home/pi/Applications/")
    except:
        pass
    tipo_faro = sys.argv[1].lower()

    # Carica la configurazione
    with open(f"config_{tipo_faro}.json", "r") as f:
        config = json.load(f)

    cache = {
        'queue': Queue(),
        'resp': "",
    }

    threading.Thread(target=partial(thread_comunicazione, config['ip'], config['port'], cache), daemon=True, name="com_in").start()

    # Imposta la telecamera
    indice_camera, video = apri_camera()
    if indice_camera is None:
     print("Nessuna telecamera trovata")
     sys.exit(1)
    set_camera(indice_camera, config)

    # Imposta la finestra
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f"{config['window_width']}x{config['window_height']}+{config['window_shift_x']}+{config['window_shift_y']}")
    root.resizable(False, False)
    lmain = tk.Label(root)
    lmain.pack()

    show_frame(video, cache, lmain)
    root.mainloop()
