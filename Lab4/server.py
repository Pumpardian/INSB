import select
import socket
import threading
import time

class Server:
    def __init__(self, slowloris_timeout=16, flood_protected=True,
                  spam_rate = 5, max_pending_connections = 5):
        self.host = '0.0.0.0'
        self.port = 9999
        self.pending = []
        self.running = True
        self.flood_protected = flood_protected
        self.syn_received = []
        self.spam_count = {}
        self.spam_rate = spam_rate
        self.slowloris_timeout = slowloris_timeout
        self.max_pending_connections = max_pending_connections
        self.lock = threading.Lock()
        
    def handle_client(self, client_sock, addr):
        try:
            if self.slowloris_timeout > 0:
                try:
                    client_sock.settimeout(self.slowloris_timeout)
                except:
                    return
            else:
                client_sock.settimeout(999999)
            client_sock.send(b"Welcome! Type 'exit' to quit.\n")
            
            last_activity = time.time()
            while True:
                try:
                    data = client_sock.recv(1024)
                    if not data:
                        break

                    if self.flood_protected:
                        current_time = time.time()
                        with self.lock:
                            if addr[0] not in self.spam_count:
                                self.spam_count[addr[0]] = []                   
                            self.spam_count[addr[0]] = [t for t in self.spam_count[addr[0]] if current_time - t < self.spam_rate]

                            if len(self.spam_count[addr[0]]) >= self.spam_rate:
                                print(f"[SERVER: ANTI-Flood] Blocked {addr}")
                                client_sock.send(b"RST")
                                client_sock.close()
                                return              
                            self.spam_count[addr[0]].append(current_time)

                    last_activity = time.time()               
                    msg = data.decode().strip()
                    if msg.lower() == 'exit':
                        client_sock.send(b"Goodbye!\n")
                        break               
                    client_sock.send(f"Echo: {msg}\n".encode())
                        
                except socket.timeout:
                    if self.slowloris_timeout > 0 and time.time() - last_activity > self.slowloris_timeout:
                        print(f"[SERVER Anti-Slowloris] Dropping idle connection from {addr}")
                        break
                    continue
                except:
                    break
        finally:
            client_sock.close()
            with self.lock:
                if addr in self.syn_received:
                    self.syn_received.remove(addr)
            print(f"[SERVER] {addr} disconnected")
    
    def handle_connection(self, client_sock, addr):
        with self.lock:
            self.pending.append(addr)
            client_sock.settimeout(1)
        try:
            data = client_sock.recv(1024)

            if data == b"ACK" and addr not in self.syn_received:
                print(f"[SERVER: ACK Protection] Rejecting ACK without SYN from {addr}")
                client_sock.send(b"RST")
                client_sock.close()
                return
                
            if data != b"SYN" and addr not in self.syn_received:
                print(f"[SERVER Syn] {addr} tried to connect without syn")
                client_sock.send(b"RST")
                client_sock.close()
                return
            
            with self.lock:
                self.syn_received.append(addr)
            client_sock.send(b"SYN-ACK")
            
            while(True):
                data = client_sock.recv(1024)
                if data != b"ACK":
                    if self.flood_protected:
                        print(f"[SERVER ANTI-Flood] Blocked {addr}")
                        client_sock.send(b"RST")
                        client_sock.close()
                        return
                    else:
                        print(f"[SERVER ACK] {addr} didnt answered with ack")
                        continue
                else:
                    break
            
            print(f"[SERVER] Connection from {addr} established")
            thread = threading.Thread(
                target=self.handle_client,
                args=(client_sock, addr),
                daemon=True
            )
            thread.start()
        except socket.timeout:
            client_sock.close()
            print(f"[SERVER] Handshake timeout for {addr}")
            return
        except ConnectionResetError:
            print(f"[Server] Client {addr} cancelled connection establishment")
        finally:
            with self.lock:
                if addr in self.pending:
                    self.pending.remove(addr)
    
    def start(self):
        server_sock = socket.socket()
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(10)    
        print(f"[SERVER] Listening on {self.host}:{self.port}")
        
        while self.running:
            try:
                ready, _, _ = select.select([server_sock], [], [], 1)
                if not ready:
                    continue

                client_sock, addr = server_sock.accept()
                ip, port = addr
                print(f"[Server] {addr} is trying to establish connection")
                
                if (self.max_pending_connections > 0 and len(self.pending) > self.max_pending_connections):
                    print(f"[Server] {addr} max connections reached")
                    print(f"[Server] {addr} connection denied")
                    client_sock.close()
                    continue

                connection_thread = threading.Thread(
                    target=self.handle_connection,
                    args=(client_sock, addr),
                    daemon=True
                )
                connection_thread.start()
                
            except KeyboardInterrupt:
                print("\n[SERVER] Shutting down...")
                self.running = False
                break
            except Exception as e:
                print(f"[SERVER: Error] {e}")

        server_sock.close()

if __name__ == "__main__":
    startProtected = bool(input("Start in protected mode? Leave blank to run in vulnerable: "))
    if startProtected:
        print(f"Starting in protected mode")
        server = Server(slowloris_timeout=12, flood_protected=True,
                         spam_rate=5, max_pending_connections=5)
    else:
        print(f"Starting in vulnerable mode")
        server = Server(slowloris_timeout=0, flood_protected=False,
                         spam_rate=0, max_pending_connections=0)
    server.start()