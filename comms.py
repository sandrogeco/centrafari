import socket
import threading

def avvia_comunicazione(ip, port, queue):
    while True:
        try:
            client_socket = socket.socket()
            client_socket.bind((ip, port))
            client_socket.listen(1)
            print(f"[+] In ascolto su {ip}:{port}...")
            conn, addr = client_socket.accept()
            print(f"[+] Connessione da {addr}")

            t = threading.Thread(target=thread_comunicazione, args=(conn, queue), daemon=True).start()

            while True:
                data = conn.recv(1024).decode("UTF-8")
                with open("/tmp/all_msgs.txt", "a") as f:
                    f.write("[RX] " + data + "\n")

            conn.close()
            client_socket.close()
            t.stop()
        except:
            pass

def thread_comunicazione(conn, queue):
    while True:
        p = queue.get()
        msg = "XYL %d %d %f " % (p['posiz_pattern_x'], p['posiz_pattern_y'], p['lux'])

        with open("/tmp/all_msgs.txt", "a") as f:
            f.write("[TX] " + msg + "\n")
        print("[TX] " + msg)

        try:
            conn.sendall(msg.encode())  # send message
            #replica_da_Proteus = client_socket.recv(1024).decode("UTF-8")
        except:
            pass
