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
import os
import subprocess
import atexit
import signal
from datetime import datetime
import logging

from funcs import rileva_punto_angoloso, visualizza_croce_riferimento, preprocess
from camera import set_camera, apri_camera
from comms import thread_comunicazione
from utils import uccidi_processo


def show_frame(video, cache, lmain):
    if cache['DEBUG']:
        t0 = time.monotonic()

    image_input = cv2.imread("/tmp/frame.jpg")

    if image_input is None:
        lmain.after(10, lambda: show_frame(video, cache, lmain))
        return

    image_input = cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
    image_input = preprocess(image_input, cache)

    image_output = cv2.cvtColor(image_input.copy(), cv2.COLOR_GRAY2BGR)
    image_output, point, _ = rileva_punto_angoloso(image_input, image_output, cache)

    stato_comunicazione = cache['stato_comunicazione']
    if stato_comunicazione.get('croce', 'croce_OFF') == "croce_ON":
        visualizza_croce_riferimento(
            image_output,
            315,
            160 + stato_comunicazione.get('inclinazione', 0),
            stato_comunicazione.get('TOV', 50),
            stato_comunicazione.get('TOH', 50)
        )

    if point:
        cache['queue'].put({ 'posiz_pattern_x': point[0], 'posiz_pattern_y': point[1], 'lux': 0 })

    if cache['DEBUG']:
        logging.debug(f"Durata elaborazione: {1000 * (time.monotonic() - t0)} ms, fps = {1 / (t0 - cache.get('t0', 0))}")
        cache['t0'] = t0

    img = PIL.Image.fromarray(image_output)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(500, lambda: show_frame(video, cache, lmain))




def cleanup(p):
    logging.info("cleanup...")
    try:
        os.killpg(p.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler(f"/tmp/MW28912py_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"),
            logging.StreamHandler()
        ]
    )

    logging.info(f"Avvio MW28912.py {sys.argv}")

    uccidi_processo("usb_video_capture_cm4")

    tipo_faro = sys.argv[1].lower()

    # Carica la configurazione
    percorso_script = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(percorso_script, f"config_{tipo_faro}.json"), "r") as f:
        config = json.load(f)

    if len(sys.argv) > 2:
        config['port'] = int(sys.argv[2])

    cache = {
        "DEBUG": config.get("DEBUG") or False,
        "config": config,

        "stato_comunicazione": {},
        "queue": Queue(),
    }
    #thread_comunicazione( config['port'], cache)
    t=threading.Thread(target=partial(thread_comunicazione, config['port'], cache), daemon=True, name="com_in").start()

    # Imposta la telecamera
    indice_camera, video = apri_camera()
    if video is None:
        logging.error("Nessuna telecamera trovata! Uscita")
        sys.exit(1)
    video.release()
    set_camera(indice_camera, config)

    # Avvia la cattura delle immagini
    time.sleep(1)
    process_video_capture = subprocess.Popen(
        "/home/pi/Applications/usb_video_capture_cm4 -c 10000000 &",
        shell=True,
        preexec_fn=os.setsid,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    atexit.register(partial(cleanup, process_video_capture))

    def _sig_handler(signum, frame):
        cleanup(process_video_capture)
        sys.exit(0)

    for s in (signal.SIGINT, signal.SIGTERM):
        signal.signal(s, _sig_handler)

    # Imposta la finestra
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f"{config['width']}x{config['height']}+{config['window_shift_x']}+{config['window_shift_y']}")
    root.resizable(False, False)
    lmain = tk.Label(root)
    lmain.pack()

    show_frame(video, cache, lmain)
    root.mainloop()
