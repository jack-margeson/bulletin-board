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

    def client_startup(self):
        """
        TODO: Ask server implementation for the nearest ID not yet claimed,
        which should be set for this client, replacing the hard-coded
        implementation below where it's just set to 0.
        """
        self.id = 0

        self.client_print_startup_message()

        if self.id != -1:
            # Client has been assigned an ID (and the server is running.)
            self.client_running = True
            # Start the client user terminal.
            self.client_terminal_prompt()
        else:
            print(
                "An error has occured in recieving client id from the server. Please try again later."
            )

    def client_print_startup_message(self):
        print("-------------------------------------")
        print("🗣️ OBBS - Open Bulletin Board Software")
        print("(client instantiated with ID #%d)" % (self.id))
        print(
            "\n👨 Username: %s, group: %s"
            % (self.username, self.group if self.group != "" else "n/a")
        )
        print("🕑 Time: %s" % (datetime.datetime.now()))
        print("\n💡 TIP: use %help to view commands.")
        print("-------------------------------------")

    def client_terminal_prompt(self):
        while self.client_running is True:
            print("> ", end="")
            u_input = input()
            if not u_input.startswith(self.prefix):
                print("Invalid command.")
            else:
                """
                TODO: Create command switch statement here, document all commands
                """
                print("Valid command!")

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
