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
        self.lock = threading.Lock()

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
        # Receive the client username and group
        client_info = client_socket.recv(1024).decode()
        client_name = client_info.split(" ")[0]
        client_group = client_info.split(" ")[1]
        client_id = self.client_ids
        # Send client ID to client to confirm connection
        client_socket.send(str(client_id).encode())
        # Announce that a client has been connected.
        print("A client with ID #%d has connected, waiting for queries." % (client_id))

        # Manage client, group, and board data
        self.add_clients_groups(client_id, client_name, client_group, client_socket)

        # Broadcast to all clients that a new client has joined
        self.broadcast_client_join(client_id, client_name)

        # Handle client requests
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            command = data.split(" ")[0]
            params = data.split(" ")[1:]
            # TODO: Handle all necessary commands
            match command[1:]:
                case "%command":
                    self.handle_command(command, *params)

    def add_clients_groups(self, client_id, client_name, client_group, client_socket):
        """Add the client to the list of users in a group.
        All users are added to the group "default" unless a group name is specified.
        The list of users in a group is saved on shutdown and recalled on boot as
        a user should stay in a group unless they
            1. connect with another group name instead or 
            2. use the %groupleave command.
        Users can be in multiple groups.
        """
        with self.lock:
            # Increment client_ids for the next client
            self.client_ids += 1

            # Add client to the connected clients list
            self.connected_clients[client_id] = {
                "name": client_name,
                "group": client_group,
                "client_socket": client_socket,
            }

            # GROUPS
            # If the user isn't in default, add to default group.
            if client_name not in self.groups["default"]:
                self.groups["default"].append(client_name)
            # If the user supplied a group on connect that doesn't exist, create the group.
            if client_group not in self.groups.keys():
                self.groups[client_group] = [client_name]
            # If user supplied group on connect that does exist, add them to the group.
            elif client_name not in self.groups[client_group]:
                self.groups[client_group].append(client_name)
            print(self.groups)

            # BOARDS
            # Create a board for default if it doesn't exist yet
            if "default" not in self.boards.keys():
                self.boards["default"] = {}
            # Add blank boards for all groups that don't have a board yet
            for group in self.groups.keys():
                if group not in self.boards.keys():
                    self.boards[group] = {}
            print(self.boards)

    def broadcast_client_join(self, client_id, client_name):
        """Broadcast to all clients that a new client has joined."""
        with self.lock:
            encodedMessage = str(
                "%s has joined the server (client ID #%d)."
                % (client_name, client_id)
            ).encode()
            for cid, client in self.connected_clients.items():
                # Exclude the current connected client
                if cid != client_id:
                    # Print to all other clients on their socket that *this* client has joined with its information
                    client["client_socket"].send(encodedMessage)


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
