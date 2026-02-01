import socket
import json
import base64
from kerberos_server import en_de_crypt

USER_ID = str(input("Enter user_id: "))
USER_KEY = str(input("Enter user_key: ")).encode("utf-8")
HOST, PORT = "localhost", 5555


def send_request_to_server(server, data):
    request = {"server": server, "data": data}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(json.dumps(request).encode())
    response = s.recv(4096)
    s.close()
    return json.loads(response.decode())


def error_check(data):
    if "error" in data:
        print("Error: ", data["error"])
        return True
    return False


def client_flow():
    as_request = {"client": USER_ID}
    as_response = send_request_to_server("auth", as_request)
    if (error_check(as_response)): 
        return

    as_data_encrypted = base64.b64decode(as_response["data"].encode())
    message_plain = en_de_crypt(USER_KEY, as_data_encrypted)

    try:
        as_message = json.loads(message_plain.decode())
    except:
        print("Wrong client key")
        return
    
    session_key = base64.b64decode(as_message["session_key"].encode())
    tgt_encrypted = as_message["tgt"]
    print("Received session key for TGS: ", session_key.hex())

    service = str(input("Enter service to access: "))
    tgs_request = {
        "tgt": tgt_encrypted,
        "service": service
    }
    tgs_response = send_request_to_server("tgs", tgs_request)
    if (error_check(tgs_response)):
        return

    tgs_data_encrypted = base64.b64decode(tgs_response["data"].encode())
    tgs_message_plain = en_de_crypt(session_key, tgs_data_encrypted)
    tgs_message = json.loads(tgs_message_plain.decode())
    service_session_key = base64.b64decode(tgs_message["service_session_key"].encode())
    service_ticket = tgs_message["service_ticket"]
    print("Received service session key: ", service_session_key.hex())

    svc_request = {
        "service_ticket": service_ticket,
        "auth": base64.b64encode(service.encode()).decode(),
        "service_session_key": base64.b64encode(service_session_key).decode(),
    }
    svc_response = send_request_to_server("svc", svc_request)
    if (error_check(as_response)): 
        return

    print("Server approved client:", svc_response["client"])


if __name__ == "__main__":
    client_flow()