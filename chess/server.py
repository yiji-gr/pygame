import socket
import yaml
import threading


def receive_message(sock: socket.socket):
    while True:
        try:
            msg = sock.recv(1024)
            if msg:
                for client_sock in client_sockets:
                    client_sock.sendall(msg)
        except socket.error as e:
            print(f"error: {e}")
            break


if __name__ == '__main__':
    with open("config.yaml") as f:
        data = yaml.safe_load(f)

    host = data["HOST"]
    port = data["PORT"]

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(2)

    client_sockets = []
    while True:
        client_socket, client_addr = server_socket.accept()
        client_sockets.append(client_socket)

        receive_thread = threading.Thread(
            target=receive_message,
            args=(client_socket, ),
            daemon=True,
        )
        receive_thread.start()
