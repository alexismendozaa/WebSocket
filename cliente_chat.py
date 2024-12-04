import socket
import base64
import threading

# Configuración del cliente
# Cambia `192.168.1.10` por la IP del servidor (consulta con ipconfig en el servidor).
HOST = '192.168.0.125'  
PORT = 9002  # Mismo puerto que el servidor

def listen_to_server(client):
    """Escuchar mensajes enviados por el servidor."""
    while True:
        try:
            response = client.recv(1024)
            if not response:
                break

            # Decodificar y mostrar el mensaje recibido
            print("Mensaje recibido:", response[2:].decode())
        except:
            break

def connect_to_server():
    """Conectar al servidor y enviar/recibir mensajes."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Handshake WebSocket
    key = base64.b64encode(b"cliente-chat").decode()
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n\r\n"
    )
    client.send(handshake.encode())
    response = client.recv(1024).decode()
    print("Respuesta del servidor:")
    print(response)

    # Hilo para escuchar al servidor
    threading.Thread(target=listen_to_server, args=(client,)).start()

    # Enviar mensajes al servidor
    while True:
        message = input("Escribe un mensaje: ")
        client.send(b'\x81' + bytes([len(message)]) + message.encode())

if __name__ == "__main__":
    connect_to_server()
