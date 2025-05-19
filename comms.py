import socket
import logging


def decode_cmd(resp):
    stato_comunicazione = {}

    if resp.startswith("CFG->"):
        # TOV
        stato_comunicazione['tov'] = int(resp[10:13])
        # TOH
        stato_comunicazione['toh'] = int(resp[34:37])

    if resp.startswith("croce"):
        stato_comunicazione['croce'] = resp
    elif resp.startswith("inclinazione*"):
        stato_comunicazione['inclinazione'] = int(resp.replace("inclinazione*", ""))

    return stato_comunicazione


def thread_comunicazione(port, cache):
    first_run = True

    while True:
        if first_run:
            msg = "start_cfg"
            first_run = False
        else:
            if cache['queue'].empty():
                msg = "idle"
            else:
                p = cache['queue'].get()
                msg = f"XYL {p['posiz_pattern_x']} {p['posiz_pattern_y']} {p['lux']} "

        try:
            conn = socket.socket()
            conn.connect(("localhost", port))
            conn.sendall(msg.encode())
            data = conn.recv(1024).decode("UTF-8")

            cache['stato_comunicazione'].update(decode_cmd(data.strip()))
        except Exception as e:
            logging.error(f"thread_comunicazione: error: {e}")
            continue

        logging.debug(f"[TX] {msg}")
        logging.debug(f"[RX] {data}")
