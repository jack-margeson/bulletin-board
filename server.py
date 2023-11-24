"""
server.py 
---------
Local bulitin board system server executable.
Written by Jack Margeson, MJ Schnee, and Nick Bryant 
CS4065 Computer Networks, October 2023
"""

import socket
import threading
import signal
import sys
import pickle

# Define the max number of connections
MAX_CONNECTIONS = 5


class Server:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.client_ids = 0
        self.connected_clients = {}
        # Groups loaded from groups.pkl on startup.
        self.groups = {"default": []}
        # Boards (and posts) are loaded from boards.pkl on startup.
        self.boards = {"default": {}}

    def server_shutdown(self, signum, frame):
        print("Ctrl+C pressed. Starting shutdown...")
        # Pickle anything that needs to be saved and reloaded next time the
        # server starts up.
        # Save the list of groups to groups.pkl using pickle.
        output = open("groups.pkl", "wb")
        pickle.dump(self.groups, output)
        output.close()
        print("List of groups saved...")
        # Save the list of boards and posts to boards.pkl using pickle.
        output = open("boards.pkl", "wb")
        pickle.dump(self.boards, output)
        output.close()
        print("List of boards and posts saved...")
        # Shut down the process.
        print("Done! See you later.")
        sys.exit(0)

    def server_startup(self):
        # Get instance of a socket for the server
        self.server_socket = socket.socket()
        # Bind host address and port
        self.server_socket.bind((self.host, self.port))
        # Set max amount of users to MAX_CONNECTIONS
        self.server_socket.listen(MAX_CONNECTIONS)

        # Restore data that needs to be set on server startup
        # Reload the group pickle file.
        groups_pkl = open("groups.pkl", "rb")
        self.groups = pickle.load(groups_pkl)
        print(len(self.groups), " group(s) loaded")
        groups_pkl.close()
        # Reload the group pickle file.
        boards_pkl = open("boards.pkl", "rb")
        self.boards = pickle.load(boards_pkl)
        print(len(self.boards), " board(s) loaded")
        boards_pkl.close()

        # Listen for incoming connections
        print("Listening for connections on %s:%s..." % (self.host, self.port))
        self.server_socket.listen()
        while True:
            # Send each client to open_connections
            client_socket, client_address = self.server_socket.accept()
            threading.Thread(
                target=self.open_connection,
                args=(client_socket, client_address),
                daemon=True,
            ).start()

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
        self.connected_clients[client_id] = {
            "name": client_name,
            "group": client_group,
            "client_socket": client_socket,
        }

        # Add the client to the list of users in a group. All users are added to the group "default" unless
        # a group name is specified. The list of users in a group is saved on shutdown and recalled on boot
        # as a user should stay in a group unless they 1. connect with another group name instead or 2. use the
        # %groupleave command. Users can be in multiple groups.
        # TODO: save this grouplist and restore it on server shutdown/boot

        # If the user isn't in default, add to default server.
        if client_name not in self.groups["default"]:
            self.groups["default"].append(client_name)
        # If the user supplied a group on connect that doesn't exist, create the group.
        if client_group not in self.groups.keys():
            self.groups[client_group] = [client_name]
        # If the user supplied a group on connect that exists, and they aren't a part of it
        # already, add them to that group. Otherwise, just do nothing.
        elif client_name not in self.groups[client_group]:
            self.groups[client_group].append(client_name)

        print(self.groups)

        # We're also going to build a board for each group.
        # If default doesn't have a board:
        if "default" not in self.boards.keys():
            self.boards["default"] = {}
        # Go through the list of groups. If there's a group that doesn't have a
        # board yet, go ahead and add a blank board.
        for group in self.groups.keys():
            if group not in self.boards.keys():
                self.boards[group] = {}

        print(self.boards)

        # Increment the client_ids for the next client that gets opened.
        self.client_ids += 1

        # Broadcast to all clients that a new client has joined.
        for key, client in self.connected_clients.items():
            # Exclude the current connected client
            if key != client_id:
                # Print to all other clients on their socket that *this* client has joined with its information
                client["client_socket"].send(
                    str(
                        "%s has joined the server (client ID #%d)."
                        % (client_name, client_id)
                    ).encode()
                )

        # While the connection with this client is open:
        while True:
            # Wait for data to be recieved from the client.
            data = client_socket.recv(1024).decode()
            # Parse the data sent from the client.
            # TODO: parse command
            print(data)
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
    server = Server(
        host if host != "" else socket.gethostbyname(socket.gethostname()),
        int(port) if port != "" else 1024,
    )
    # Register the Ctrl+C signal handler
    signal.signal(signal.SIGINT, server.server_shutdown)
    # Start the server.
    server.server_startup()

    return 0


if __name__ == "__main__":
    main()
