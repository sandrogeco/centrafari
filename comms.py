import socket
import logging


def decode_cmd(resp):
    stato_comunicazione = {}
    if resp.startswith("CFG->"):
        stato_comunicazione['pattern'] = int(resp[5])
        stato_comunicazione['croce'] = int(resp[6])
        stato_comunicazione['TOV'] = int(resp[10:13])
        # stato_comunicazione['mpx'] = float(resp[16:24])
        stato_comunicazione['inclinazione'] = int(resp[27:31])
        stato_comunicazione['TOH'] = int(resp[34:37])
        stato_comunicazione['qin'] = float(resp[40:45])
        # stato_comunicazione['TAX'] = float(resp[46:51])
        # stato_comunicazione['TAY'] = float(resp[54:59])
        # stato_comunicazione['TNX'] = float(resp[62:67])
        # stato_comunicazione['TNY'] = float(resp[70:75])
        # stato_comunicazione['TFX'] = float(resp[78:83])
        # stato_comunicazione['TFY'] = float(resp[86:91])
        # stato_comunicazione['CRI'] = float(resp[94:97])
        # stato_comunicazione['CRF'] = float(resp[100:103])
        # stato_comunicazione['CCI'] = float(resp[106:109])
        # stato_comunicazione['CCF'] = float(resp[112:115])
        # stato_comunicazione['tax'] = float(resp[118:121])
        # stato_comunicazione['tay'] = float(resp[124:127])
        # stato_comunicazione['Lnx'] = float(resp[130:135])
        # stato_comunicazione['Lny'] = float(resp[138:143])
        # stato_comunicazione['AtH'] = float(resp[146:149])
        # stato_comunicazione['Lnm'] = float(resp[152:163])
        # stato_comunicazione['alf'] = float(resp[166:173])
        # stato_comunicazione['ncl'] = float(resp[176:178])
        # stato_comunicazione['lwn'] = float(resp[181:184])
        # stato_comunicazione['dnv'] = float(resp[187:188])
        # stato_comunicazione['bcn'] = float(resp[191:192])
        # stato_comunicazione['mcb'] = float(resp[195:196])
        # stato_comunicazione['stm'] = float(resp[199:202])
        # stato_comunicazione['stc'] = float(resp[205:208])
        # stato_comunicazione['AtV'] = float(resp[211:214])

    return stato_comunicazione


def thread_comunicazione(port, cache):
    first_run = True

    while True:
        if first_run:
            msg = "start_cfg "
            first_run = False
        else:
            try:
                p = cache['queue'].get(timeout=0.3)
                msg = f"XYL {p['posiz_pattern_x']} {p['posiz_pattern_y']} {p['lux']:.2f} {p['roll']:.2f} {p['yaw']:.2f} {p['pitch']:.2f} "
            except:
                msg = "idle "
        try:
            conn = socket.socket()
            conn.connect((cache['config'].get('ip',"localhost"), port))
            conn.sendall(msg.encode())
            data = conn.recv(1024).decode("UTF-8")
            cache['stato_comunicazione'].update(decode_cmd(data.strip()))
        except Exception as e:
            logging.error(f"thread_comunicazione: error: {e}")
            continue

        logging.debug(f"[TX] {msg}")
        logging.debug(f"[RX] {data}")
       # time.sleep(0.3)
