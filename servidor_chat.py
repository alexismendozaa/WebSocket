import socket
import threading
import base64
import hashlib

# Configuración del servidor
HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT = 9002       # Puerto del servidor

clients = []  # Lista de clientes conectados

def handle_client(client_socket, address):
    global clients
    try:
        # Handshake
        request = client_socket.recv(1024).decode()
        key_line = [line for line in request.split('\r\n') if "Sec-WebSocket-Key" in line][0]
        key = key_line.split(": ")[1]

        magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        accept_key = base64.b64encode(hashlib.sha1((key + magic_string).encode()).digest()).decode()

        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
        )
        client_socket.send(response.encode())
        clients.append(client_socket)

        print(f"{address} se conectó. Total de clientes: {len(clients)}")
        
        # Escuchar mensajes del cliente
        while True:
            message = client_socket.recv(1024)
            if not message:
                break

            # Decodificar mensaje recibido
            decoded_message = message[2:].decode()
            print(f"Mensaje de {address}: {decoded_message}")
            
            # Enviar mensaje a todos los clientes conectados
            broadcast(f"{address} dice: {decoded_message}", client_socket)
    except:
        print(f"{address} desconectado.")
    finally:
        clients.remove(client_socket)
        client_socket.close()

def broadcast(message, sender_socket):
    """Enviar un mensaje a todos los clientes conectados excepto al remitente."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(b'\x81' + bytes([len(message)]) + message.encode())
            except:
                clients.remove(client)

def start_server():
    """Iniciar el servidor de WebSocket."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Servidor de chat WebSocket escuchando en {HOST}:{PORT}")

    while True:
        client_socket, address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, address)).start()

if __name__ == "__main__":
    start_server()
