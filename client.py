"""
client.py 
---------
Terminal client for connecting to the local bulletin board system.
Written by Jack Margeson, MJ Schnee, and Nick Bryant 
CS4065 Computer Networks, October 2023
"""

# Imports and declarations
import socket
import datetime
import threading
import sys
import signal


class Client:
    prefix = "%"

    def __init__(self, username, group) -> None:
        self.id = -1
        self.username = username
        self.group = group
        self.client_socket = None
        self.client_running = False

    def client_shutdown(self, signum, frame):
        self.client_running = False
        print("\nCtrl+C pressed. Starting shutdown...")
        # If we haven't been disconnected from the server yet, do so.
        if self.id > -1:
            self.client_disconnect_from_server()
        print("Done! See you later.")
        sys.exit(0)

    def client_disconnect_from_server(self):
        # Send the exit command to the server telling them that we're either
        # just disconnecting from the server or fully shutting down the
        # client (the server doesn't care about this distinction though)
        self.client_socket.send("exit".encode())
        # Set the ID of the client to -1 to represent being disconnected
        self.id = -1
        pass

    def client_startup(self):
        self.client_print_startup_message()
        # Instantiate a socket for the client
        self.client_socket = socket.socket()
        self.client_running = True
        self.client_terminal_prompt()

    def client_print_startup_message(self):
        print("-------------------------------------")
        print("🗣️ OBBS - Open Bulletin Board Software\n")
        print(
            "\n👨 Username: %s, group: %s"
            % (self.username, self.group if self.group != "" else "default")
        )
        print("🕑 Time: %s" % (datetime.datetime.now()))
        print("\n💡 TIP: use %help to view commands.")
        print("-------------------------------------")

    def client_terminal_prompt(self):
        while self.client_running is True:
            u_input = input("> ")
            # Parse user command, in case of parameters.
            u_command = u_input.split(" ")[0]
            u_parameters = u_input.split(" ")[1:]

            # Make sure the command starts with the right prefix.
            if not u_command.startswith(self.prefix):
                print("Invalid command.")
            elif self.id < 0 and u_command[1:] not in ["help", "connect", "exit"]:
                # Connection to server has not been made yet--only commands that should work are help, connect, and exit.
                print(
                    "The command you have entered, '%s', is only available when the client is connected.\nPlease connect to a server using '%s' and try again."
                    % (u_command, "%connect host port")
                )
            else:
                # Match user input with command.
                match u_command[1:]:
                    case "help":
                        if self.id > -1:
                            self.client_socket.send(u_command[1:].encode())
                        else:
                            print(
                                "A %connect command followed by the address and port number of a running bulletin board server to connect to.\n"
                                "An %exit command to exit the client program."
                            )
                    case "connect":
                        if self.id > -1:
                            # The client has already been assigned an ID, ignore the request to connect until disconnected from current server.
                            print(
                                "You are already connected to a server. If you wish to switch servers, please disconnect and try again."
                            )
                        else:
                            # Check if we have the correct number of parameters.
                            if len(u_parameters) < 2:
                                print(
                                    "Incorrect parameters. Please supply an IP number and port number of the bulletin board.\nExample: %connect 127.0.0.1 2048"
                                )
                            else:
                                # We have the correct number of parameters. Try connecting to the bulletin board.
                                host = str(u_parameters[0])
                                port = int(u_parameters[1])
                                print("Connecting to %s:%d..." % (host, port))
                                self.client_socket.connect((host, port))
                                # Client has been connected, send username and group if applicable.
                                self.client_socket.send(
                                    (self.username + " " + self.group).encode()
                                )
                                # Get the client ID which is sent from the server.
                                self.id = int(self.client_socket.recv(1024).decode())
                                # Print message to client terminal.
                                print(
                                    "Success! Connected to %s:%s as ID #%d."
                                    % (host, port, self.id)
                                )
                                # Create thread for handling responses from the server.
                                threading.Thread(
                                    target=self.client_read_server_response, daemon=True
                                ).start()
                    case "exit":
                        if self.id > -1:
                            # If client is connect, exit just connects from server
                            self.client_disconnect_from_server()
                        else:
                            # If user
                            self.client_shutdown()
                    case _:
                        if self.id > -1:
                            self.client_socket.send(u_command[1:].encode())
                        else:
                            print("Please connect to a server first.")

    def client_read_server_response(self):
        while self.client_running is True:
            data = self.client_socket.recv(1024).decode()
            if data:
                print(data)
        return 0


def main():
    # Get input from user, username and group
    username = input("Enter username: ")
    group = input("Enter group (RETURN if n/a): ")
    # Instantiate client interface
    if group == "":
        group = "default"
    client = Client(username, group)
    # Register the Ctrl+C signal handler
    signal.signal(signal.SIGINT, client.client_shutdown)
    # Start client
    client.client_startup()

    # End execution (client has been shut down, as the only way
    # to get here is for client_shutdown to be run. Or an error.)
    return 0


if __name__ == "__main__":
    main()
