import random
import socket
import sys
import threading
import time
import uuid

from packet import InboundPacket, OutboundPacket


class Console(threading.Thread):
    def __init__(self, game):
        super().__init__()

        self.game = game
    
    def run(self):
        while self.game.running:
            command = input("> ")
            if not command:
                continue
            if command in ["exit", "quit", "stop"]:
                self.game.shutdown()
            elif command == "list":
                connected_clients = [
                    f"{client.username} [{client.address}:{client.port}]"
                    for client in self.game.clients
                    ] or None
                if connected_clients:
                    print("Connected clients: \n" + '\n'.join(connected_clients))
                else:
                    print("No connected clients!")
            else:
                print("Invalid command!")


class Game(threading.Thread):
    def __init__(self, server: socket.socket, ADDR):
        super().__init__()
        self.daemon = True

        self.server = server
        self.ADDR = ADDR

        self.waiting_for_clients = True
        self.running = True
        self.shutdown_key = None

        self.console = Console(game=self)
        self.console.start()

        self.clients = []

    def run(self):
        self.server.listen()
        print("Game started! Waiting for clients...")

        while True:
            if self.waiting_for_clients and len(self.clients) < 2:
                conn, addr = self.server.accept()

                username_packet = InboundPacket(conn)
                username = username_packet.receive()[1]

                if not username:
                    ... # invalid username TODO
                elif self.shutdown_key and username == str(self.shutdown_key):
                    return sys.exit() # shutdown the server
                else:
                    self.clients.append(Client(conn, addr, game=self, username=username))
                    if len(self.clients) == 2:
                        ... # start game TODO
            elif self.running:
                ...
            else:
                break

        sys.exit()

    def shutdown(self):
        print("Server is shutting down...", end=" ")

        self.running = False
        self.waiting_for_clients = False

        self.shutdown_key = uuid.uuid4()

        # disconnect all clients
        for client in self.clients:
            client.disconnect("shutdown")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as shutdown_client:
            shutdown_client.connect(self.ADDR)
            shutdown_client.send(str(self.shutdown_key).encode('utf-8'))

        print("done!")
        sys.exit()


class Client:
    def __init__(self, conn, addr, game: Game, username: str):
        self.conn = conn
        self.addr = addr
        self.game = game
        self.username = username

        self.address = addr[0]
        self.port = addr[1]

        self.keep_alive_thread = threading.Thread(target=self.keep_alive)
        self.keep_alive_thread.start()

        print(f"{self.username} joined! ({len(self.game.clients)}/2)")

    def keep_alive(self):
        while self.game.running:
            try:
                time.sleep(20)
                n = str(random.randint(100, 999))
                keep_alive_packet = OutboundPacket(kind='keep_alive', data=n, conn=self.conn)
                keep_alive_packet.send()

                self.conn.settimeout(5)
                return_packet = InboundPacket(conn=self.conn)
                return_packet.receive()
            except (socket.timeout, ValueError, ConnectionResetError, BrokenPipeError):
                self.disconnect("Timed out!")
                sys.exit() # end the thread
        # when the game finishes, send a disconnect message
        #conn.send(b'')

    def disconnect(self, reason):
        disconnect_packet = OutboundPacket(kind='disconnect', data=reason, conn=self.conn)
        try:
            disconnect_packet.send()
        except BrokenPipeError:
            pass

        print(f"{self.username} disconnected: {reason}")

        for index, client in enumerate(self.game.clients):
            if client is self:
                del self.game.clients[index]


PORT = 54321
SERVER = ""
ADDR = SERVER, PORT


def main():
    print("Server is starting...", end=" ")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print("done!")
    print(f"Server is up and running on port {PORT}")
    
    #input("Press enter to start the game: ")

    game = Game(server, ADDR)
    game.start()


if __name__ == "__main__":
    main()