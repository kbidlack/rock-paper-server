import socket
import string
import sys
import threading
import time
import uuid

from net import *

allowed_username_chars = string.ascii_letters + string.digits + '_'


class Game():
    def __init__(self, server, ADDR):
        self.server = server
        self.ADDR = ADDR

        self.running = True
        self.waiting_for_clients = True
        self.game_running = False
        self.shutting_down = False

        self.ADDRESS = ADDR[0]
        self.PORT = ADDR[1]

        self.clients = []
        self.shutdown_key = str(uuid.uuid4())

        self.console = Console(game=self)

    
    def find_clients(self, all: bool = False, username: str = None) -> list[str, ...]:
        """
        Find all clients that meet the specified criteria.
        If none are met an empty list is returned.
        If all is specified all clients are returned.
        """

        if all is True:
            found = self.clients
        elif username:
            found = [
                client for client in self.clients
                if client.username == usernamej
            ]
        else:
            found = []
        
        return found

    def send_to_client(self, packet: Packet, all: bool = False, username: str = None):
        """
        Send a packet to client(s) that meet the specified criteria.
        See self.find_clients() for more details.
        """
        
        criteria = (username, ) # TODO add more criteria
        clients_to_send_to = self.find_clients(all, *criteria) # find clients

        for client in clients_to_send_to:
            packet.conn = client.conn

            try:
                packet.send()
            except:
                client.disconnect("Timed Out")


    def start(self):
        main_thread = threading.Thread(target=self.main)
        client_thread = threading.Thread(target=self.handle_clients)
    
        main_thread.start()
        client_thread.start()

        print("done!")
        self.console.start()
    
    def shutdown(self):
        print("Game is shutting down...", end=" ")

        self.shutting_down = True

        """
        Here we send a connection to the server that tells it to shutdown.
        This is required because self.server.accept() is a blocking function,
        and we need to move past it and end the handle_clients thread.
        This can be done by creating a connection to the server and telling it
        to shut down (using the shutdown key).
        This isn't required for other threads because of self.shutting_down.
        """

        shutdown_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        shutdown_client.connect(self.ADDR)

        Packet(USERNAME, self.shutdown_key, shutdown_client).send()

        # TODO check if the other threads have shut down yet
        ... # shut down the game
        print("done!")

        sys.exit()


    def main(self):
        while self.running and self.waiting_for_clients:
            if self.game_running:
                # start the game
                print("Game starting!")
                for client in self.clients:
                    # notify each client the game is starting
                    # as well as the other's username
                    other_client = [
                        c for c in self.clients
                        if client is not c # check for other client
                    ][0]
                    game_start_packet = Packet(GAME_START, other_client.username)
                    self.send_to_client(game_start_packet, all=True)
            elif self.shutting_down:
                sys.exit()
            elif self.waiting_for_clients:
                continue
            
        
        while self.game_running:
            ... # TODO
        
        sys.exit() # exit when game finishes

    def verify_username(self, username) -> tuple[bool, str]:
        """Check if a username is valid
        Returns a tuple with the validity and reason
        if the validity is false."""
        if len(username) > 36:
            return False, "Invalid username!"
        elif username in [client.username for client in self.clients]:
            # if username is taken
            return False, "Username is taken!"
        else:
            allowed = set(allowed_username_chars)

            # if username contains characters that aren't
            # allowed this returns True
            if not (set(username) | allowed) == allowed:
                    return False, "Invalid username!"
        
        return True, ""
    
    def handle_clients(self):
        """Handles new client connections"""
        self.server.listen()
        while self.running:
            conn, addr = self.server.accept()
            if self.waiting_for_clients:
                username = Packet.from_incoming(conn).data
                username_chars = [c for c in username]

                if username == self.shutdown_key:
                    break # end this thread, server is shutting down
                
                # check if username is valid
                validity, message = self.verify_username(username)
                if validity: # username is valid
                    self.clients.append(Client(self, conn, addr, username))
                    print(f"{username} joined! ({len(self.clients)}/2)")
                    if len(self.clients) == 2:
                        # start game
                        self.game_running = True
                        self.waiting_for_clients = False
                else:
                    Packet(DISCONNECT, message, conn).send()
            else:
                Packet(DISCONNECT, "Game in progress!", conn).send()
                conn.shutdown(socket.SHUT_RDWR)
        
        sys.exit()


class Client:
    def __init__(self, game, conn, addr, username):
        self.game = game
        self.conn = conn
        self.addr = addr
        self.username = username

        self.address = addr[0]
        self.port = addr[1]

        self.main_thread = threading.Thread(target=self.main)
        self.queue = PacketQueue(client=self)

        self.main_thread.start()
        self.queue.start()
    
    def main(self):
        while self.game.running:
            ... # TODO
    
    def disconnect(self, reason):
        ... # TODO


class Console(threading.Thread):
    def __init__(self, game: Game):
        super().__init__()

        self.game = game

    def run(self):
        while self.game.running:
            command = input("> ")
            if not command:
                continue
            elif command in ["exit", "quit", "stop"]:
                self.game.shutdown()
            else:
                print("Unknown command!")


def main():
    print("Server is starting...", end=" ")

    ADDRESS = ''
    PORT = 54321
    ADDR = ADDRESS, PORT

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    game = Game(server, ADDR)
    game.start()


if __name__ == "__main__":
    main()