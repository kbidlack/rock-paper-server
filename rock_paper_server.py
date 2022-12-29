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

        self.ADDRESS = ADDR[0]
        self.PORT = ADDR[1]

        self.clients = []
        self.shutdown_key = str(uuid.uuid4())

        self.console = Console(game=self)

    def start(self):
        main_thread = threading.Thread(target=self.main)
        client_thread = threading.Thread(target=self.handle_clients)
    
        main_thread.start()
        client_thread.start()

        print("done!")
        self.console.start()
    
    def shutdown(self):
        print("Game is shutting down...", end=" ")
        shutdown_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        shutdown_client.connect(self.ADDR)

        Packet(USERNAME, self.shutdown_key, shutdown_client).send()

        ... # shut down the game
        print("done!")

        sys.exit()
    
    def main(self):
        ...
    
    def handle_clients(self):
        """Handles new client connections"""
        self.server.listen()
        while self.running:
            conn, addr = self.server.accept()
            if self.waiting_for_clients:
                username = Packet.from_incoming(conn).data
                username_chars = [c for c in username]

                if username == self.shutdown_key:
                    break # end this thread

                if len(username) <= 36:
                    for char in username_chars:
                        if char not in allowed_username_chars:
                            Packet(DISCONNECT, "Invalid username!", conn).send()
                            break
                    else:
                        self.clients.append(Client(self, conn, addr, username))
                        print(f"{username} joined! ({len(self.clients)}/2)")
                else:
                    Packet(DISCONNECT, "Invalid username!", conn).send()
                    continue
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
        ...


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