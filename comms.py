import socket
import threading
import time

def thread_comunicazione(ip,port,cache):
    while True:
        try:
            p = cache['queue'].get()
            msg = "XYL "+str(p['posiz_pattern_x'])+" "+str(p['posiz_pattern_y'])+" "+str(p['lux'])+" "
        except:
            msg="no news"
        try:
            conn = socket.socket()
            conn.connect((ip, port))
            conn.sendall(msg.encode())  # send message
            data = conn.recv(1024).decode("UTF-8")
            cache['resp']= data.lstrip()
        except:
            data=""
            pass
        print("[TX] " + msg)
        print("[RX] " + data + "\n")
        with open("/tmp/all_msgs.txt", "a") as f:
            f.write("[TX] " + msg + "\n")
            f.write("[RX] " + data + "\n")
       # time.sleep(0.5)
