import socket
import threading

class Client:
    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        
    def receive_thread(self):
        while self.connected:
            try:
                self.sock.settimeout(1)
                data = self.sock.recv(1024)
                if data:
                    print(f"\n[SERVER] {data.decode().strip()}")
                    print ("You: ", flush=True)
                elif data == b'':
                    print("\n[SERVER] Connection closed")
                    self.connected = False
                    break
            except socket.timeout:
                continue
            except:
                self.connected = False
                break
    
    def connect(self):
        try:
            self.sock = socket.socket()
            self.sock.settimeout(5)
            print(f"[CLIENT] Connecting to {self.host}:{self.port}...")
            self.sock.connect((self.host, self.port))

            self.sock.send(b"SYN")
            data = self.sock.recv(1024)
            if data == b"RST":
                print("[CLIENT] Connection rejected")
                return False
                
            if data != b"SYN-ACK":
                print("[CLIENT] Handshake failed")
                return False
            
            self.sock.send(b"ACK")
            self.connected = True
            
            threading.Thread(target=self.receive_thread, daemon=True).start()
            print("[CLIENT] Connected!")
            return True
        except Exception as e:
            print(f"[CLIENT] Error: {e}")
            return False
    
    def send(self, message):
        if not self.connected:
            return False
        try:
            self.sock.send(f"{message}\n".encode())
            return True
        except:
            self.connected = False
            return False
    
    def interactive(self):
        if not self.connect():
            return
        print("\nType messages to send. Type 'exit' to quit.")
        try:
            while self.connected:
                try:
                    msg = input()
                    if msg.lower() == 'exit':
                        self.send('exit')
                        break
                    self.send(msg)
                except KeyboardInterrupt:
                    print("\n[CLIENT] Exiting...")
                    self.send('exit')
                    break
        finally:
            self.sock.close()

if __name__ == "__main__":
    client = Client()
    client.interactive()