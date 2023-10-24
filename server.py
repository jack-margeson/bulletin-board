"""
server.py 
---------
Local bulitin board system server executable.
Written by Jack Margeson, MJ Schnee, and Nick Bryant 
CS4065 Computer Networks, October 2023
"""

import socket
import threading

# Define the max number of connections
MAX_CONNECTIONS = 2

class Server:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.client_ids = 0
        self.connected_clients = {}

    def server_startup(self):
        # Get instance of a socket for the server
        self.server_socket = socket.socket()
        # Bind host address and port
        self.server_socket.bind((self.host, self.port))
        # Set max amount of users to MAX_CONNECTIONS
        self.server_socket.listen(MAX_CONNECTIONS)
        # Listen for incoming connections
        print("Listening for connections on %s:%s..." % (self.host, self.port))
        self.server_socket.listen()
        while True:
            # Send each client to open_connections
            client_socket, client_address = self.server_socket.accept()
            threading.Thread(target=self.open_connection, args=(client_socket, client_address), daemon=True).start()


    def open_connection(self, client_socket, client_address):
        # Recieve the client username and group
        client_info = client_socket.recv(1024).decode()
        client_name = client_info.split(" ")[0] 
        client_group = client_info.split(" ")[1] 
        client_id = self.client_ids
        # Send client ID to client to confirm connection
        client_socket.send(str(client_id).encode())
        # Announce that a client has been connected.
        print("A client with ID #%d has connected, waiting for queries." % (client_id))

        # TODO: This could lead to a possible race condition--mutex these global memory changes.
        # Add the client socket to the list of connected clients.
        self.connected_clients[client_id] = {"name": client_name, "group": client_group, "client_socket": client_socket}
        # Increment the client_ids for the next client that gets opened.
        self.client_ids += 1

        # Broadcast to all clients that a new client has joined.
        for key, client in self.connected_clients.items():
            # Exclude the current connected client
            if key != client_id:
                # Print to all other clients on their socket that *this* client has joined with its information
                client['client_socket'].send(str("%s has joined the server (client ID #%d)." % (client_name, client_id)).encode())

        # While the connection with this client is open:
        while True:
            # Wait for data to be recieved from the client.
            data = client_socket.recv(1024).decode()
            # Parse the data sent from the client.
            # TODO: parse command
            # Send data back to the client.
            # TODO: send data back to client.


class Message:
    def __init__(self, id, sender, post, date, subject) -> None:
        self.id = id
        self.sender = sender
        self.post = post
        self.date = date
        self.subject = subject

    def save_message(self, id):
        raise NotImplementedError

    def delete_message(self, id):
        raise NotImplementedError


def main():
    host = input("Specify host IP (RETURN for localhost): ")
    port = input("Enter port (>=1024, default 1024): ")
    server = Server(host if host != "" else socket.gethostbyname(socket.gethostname()), 
                    int(port) if port != "" else 1024)
    server.server_startup()

    return 0


if __name__ == "__main__":
    main()
