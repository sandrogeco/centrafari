import socket
import threading

def thread_comunicazione(ip,port, queue):
    while True:
        try:
            p = queue.get(timeout=0.5)
            msg = "XYL "+str(p['posiz_pattern_x'])+" "+str(p['posiz_pattern_y'])+" "+str(p['lux'])+" "
        except:
            msg="no news"
        try:
            conn = socket.socket()
            conn.connect((ip, port))
            conn.sendall(msg.encode())  # send message
            data = conn.recv(1024).decode("UTF-8")
        except:
            data=""
            pass
        print("[TX] " + msg)
        print("[RX] " + data + "\n")
        with open("/tmp/all_msgs.txt", "a") as f:
            f.write("[TX] " + msg + "\n")
            f.write("[RX] " + data + "\n")
