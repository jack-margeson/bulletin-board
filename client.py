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


class Client:
    """
    class Client()
    -------------
    Constructors:
        default (string username, string group)

    Member functions:
        client_startup(self)
            Handles the startup for the client and instantiates terminal prompt.

        client_print_startup_message(self)
            Prints the startup message for a user client logging on.

        client_terminal_prompt(self)
            Enter a loop that asks users for input. Parses input into commands
            using the valid_commands list. Invalid commands will be noted and
            ignored.

        client_shutdown(self)
            Close socket between client and server, then shutting the user term-
            inal off and ending execution of the client program.
    """

    prefix = "%"
    valid_commands = [
        "help",
        "connect",
        "join",
        "post",
        "users",
        "leave",
        "message",
        "exit",
        "groups",
        "groupsjoin",
        "grouppost",
        "groupusers",
        "groupleave",
        "groupmessage",
    ]

    def __init__(self, username, group) -> None:
        self.id = -1
        self.username = username
        self.group = group
        self.client_socket = None
        self.client_running = False

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
            print("> ", end="")
            u_input = input()
            # Parse user command, in case of parameters.
            u_command = u_input.split(" ")[0]
            u_parameters = u_input.split(" ")[1:]

            # Make sure the comannd starts with the right prefix.
            if not u_command.startswith(self.prefix):
                print("Invalid command.")
            # Make sure the command is in the list of valid commands.
            elif u_command[1:] not in self.valid_commands:
                print("Invalid command.")
            elif self.id < 0 and u_command[1:] not in ["help", "connect"]:
                # Connection to server has not been made yet--only commands that should work
                # are help and connect.
                print(
                    "The command you have entered, '%s', is only available when the client is connected.\nPlease connect to a server using '%s' and try again."
                    % (u_command, "%connect host port")
                )
            else:
                """
                TODO: Create command switch statement here, document all commands
                """
                # Match user input with command.
                match u_command[1:]:
                    case "help":
                        print("help command")
                    case "connect":
                        if self.id > 0:
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
                                # We have the correct nummebrs of parameters. Try connecting to the bulletin board.
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
                    case "join":
                        print("join command")
                    case "post":
                        print("post command")
                    case "users":
                        print("users command")
                    case "leave":
                        print("leave command")
                    case "message":
                        print("message command")
                    case "exit":
                        print("exit command")
                    case "groups":
                        print("groups command")
                    case "groupjoin":
                        print("groupsjoin command")
                    case "grouppost":
                        print("grouppost command")
                    case "groupusers":
                        print("groupusers command")
                    case "groupleave":
                        print("groupleave command")
                    case "groupmessage":
                        print("groupmessgae command")

    def client_read_server_response(self):
        while self.client_running is True:
            data = self.client_socket.recv(1024).decode()
            if data:
                print(data)
        return 0

    def client_shutdown(self):
        return 0


def main():
    # Get input from user, username and group
    username = input("Enter username: ")
    group = input("Enter group (RETURN if n/a): ")
    # Instantiate client interface
    client = Client(username, group)
    # Start client
    client.client_startup()

    # End execution (client has been shut down, as the only way
    # to get here is for client_shutdown to be run. Or an error.)
    return 0


if __name__ == "__main__":
    main()
