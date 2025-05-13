import socket

cmd_da_proteus={
    'croce':"croce_OFF",
    'inclinazione':0
}


def decode_cmd(resp):
    #TODO
    if "CFG->" in resp:
        #TOV
        cmd_da_proteus['tov']=int(resp[10:12])
        #TOH
        cmd_da_proteus['toh']=int(resp[34:36])

    if "croce" in resp:
        cmd_da_proteus['croce'] = resp
    if "inclinazione*" in resp:
        cmd_da_proteus['inclinazione'] = int(resp[len("inclinazione*"):])
    return cmd_da_proteus


def thread_comunicazione(port, cache):
    first_run=True
    while True:
        if first_run:
            msg = "start_cfg"
            first_run=False
        else:
            try:
                p = cache['queue'].get()
                msg = "XYL "+str(p['posiz_pattern_x'])+" "+str(p['posiz_pattern_y'])+" "+str(p['lux'])+" "
            except:
                msg="no news"
        try:
            conn = socket.socket()
            conn.connect(("localhost", port))
            conn.sendall(msg.encode())  # send message
            data = conn.recv(1024).decode("UTF-8")
            cache['resp'] = data.lstrip()
            decode_cmd(cache['resp'])
        except:
            data = ""
            pass

        print("[TX] " + msg, flush=True)
        print("[RX] " + data + "\n", flush=True)
        with open("/tmp/all_msgs.txt", "w") as f:
            f.write("[TX] " + msg + "\n")
            f.write("[RX] " + data + "\n")
       # time.sleep(0.5)
