import os
import json
import base64
import socketserver

USERS = {"testuser1": b"testuser1_secret",
         "testuser2": b"testuser2_secret"}

SERVICES = {"printservice": b"qwerty123",
            "ftpservice": b"asdfgh456"}

TGS_SECRET_KEY = b"as_tgs_shared"


def en_de_crypt(key, message):
    result = bytearray()
    for i, byte in enumerate(message):
        result.append(byte ^ key[i % len(key)])
    return bytes(result)


def generate_session_key():
    return os.urandom(16)


def authserver_handler(client):
    if client not in USERS:
        raise Exception("Unknown client")
    
    client_key = USERS[client]
    session_key = generate_session_key()
    tgt_plain = client.encode() + b"::" + session_key
    tgt_encrypted = en_de_crypt(TGS_SECRET_KEY, tgt_plain)

    msg = {
        "session_key": base64.b64encode(session_key).decode(),
        "tgt": base64.b64encode(tgt_encrypted).decode(),
    }
    message_plain = json.dumps(msg).encode()
    message_encrypted = en_de_crypt(client_key, message_plain)

    print(f"[Auth Server] Client {client} data:\n",
          f"session_key: {session_key.hex()}\n",
          f"TGT_plain: {tgt_plain}")
    
    return message_encrypted


def tgs_server_handler(tgt_encrypted_b64, service):
    if service not in SERVICES:
        raise Exception("Unknown service")

    tgt_encrypted = base64.b64decode(tgt_encrypted_b64.encode())
    tgt_plain = en_de_crypt(TGS_SECRET_KEY, tgt_encrypted)
    
    try:
        client_bytes, session_key = tgt_plain.split(b"::", 1)
    except Exception as e:
        raise Exception("Invalid TGT format") from e
    
    client = client_bytes.decode()
    print(f"[TGS Server] Received client: {client} with\n",
          f"session_key: {session_key.hex()}")
    
    service_session_key = generate_session_key()
    service_ticket_plain = json.dumps({
        "client": client,
        "service_session_key": base64.b64encode(service_session_key).decode()
    }).encode()
    service_ticket_encrypted = en_de_crypt(SERVICES[service], service_ticket_plain)

    message = {
        "service_session_key": base64.b64encode(service_session_key).decode(),
        "service_ticket": base64.b64encode(service_ticket_encrypted).decode(),
    }
    message_plain = json.dumps(message).encode()
    message_encrypted = en_de_crypt(session_key, message_plain)

    print(f"[TGS Server] Generated for service {service}:\n",
          f"service_session_key: {service_session_key.hex()}\n",
          f"service_ticket_plain: {service_ticket_plain}")
    
    return message_encrypted


def service_access_handler(service_ticket_encrypted_b64, auth_b64, service_session_key_b64):
    service = base64.b64decode(auth_b64.encode()).decode("utf-8")
    service_ticket_encrypted = base64.b64decode(service_ticket_encrypted_b64.encode())
    service_session_key = base64.b64decode(service_session_key_b64.encode())
    service_ticket_plain = en_de_crypt(SERVICES[service], service_ticket_encrypted)

    try:
        data = json.loads(service_ticket_plain.decode())
    except Exception as e:
        raise Exception("Invalid service ticket format or ticket for wrong service") from e
    
    client = data.get("client")
    ticket_service_session_key_b64 = data.get("service_session_key")
    if not client or not ticket_service_session_key_b64:
        raise Exception("Invalid service ticket content")
    
    ticket_service_session_key = base64.b64decode(ticket_service_session_key_b64.encode())
    if ticket_service_session_key != service_session_key:
        raise Exception("Invalid service session key!")
    
    print(f"[{service} Service] Approved client: {client}")

    return client


class ServerRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(4096)
        if not data:
            return

        request = json.loads(data.decode())
        server = request.get("server")
        data = request.get("data")
        response = {}

        try:
            if server == "auth":
                client = data["client"]
                result = authserver_handler(client)
                response["data"] = base64.b64encode(result).decode()
            elif server == "tgs":
                tgt = data["tgt"]
                service = data["service"]
                result = tgs_server_handler(tgt, service)
                response["data"] = base64.b64encode(result).decode()
            elif server == "svc":
                service_ticket = data["service_ticket"]
                auth = data["auth"]
                service_session_key = data["service_session_key"]
                client = service_access_handler(service_ticket, auth, service_session_key)
                response["client"] = client
            else:
                response["error"] = "Unknown server"
        except Exception as e:
            response["error"] = str(e)
            print(f"[Error] Server - {server}: {e}")

        self.request.sendall(json.dumps(response).encode())


if __name__ == "__main__":
    HOST, PORT = "localhost", int(input("Enter server port: "))
    server = socketserver.ThreadingTCPServer((HOST, PORT), ServerRequestHandler)
    print(f"Server listening on: {HOST}:{PORT}")
    server.serve_forever()