import socket

"""
Classes that help with packets.

Packet structure:

Every packet has a header, which is sent first before the actual data.
The header is 8 bytes. The first 7 bytes define the size of the packet,
and the last byte defines the kind of packet.

disconnect: 0
keep_alive: 1
username: 2
"""

packet_kinds = ['disconnect', 'keep_alive', 'username']


class OutboundPacket:
    """A class that makes creating/sending packets easier"""

    def __init__(self, kind: str, data: str, conn: socket.socket):
        self.data = data
        self.kind = kind
        self.conn = conn
        
        self.get_header()
    
    def get_header(self) -> None:
        """Generates the packet header and encodes the data."""
        size = len(self.data.encode('utf-8'))
        if size > 9999999:
            raise ValueError("Packet is too big!")
        elif self.kind not in packet_kinds:
            raise ValueError("Invalid packet kind!")
        elif type(self.data) != str:
            raise ValueError("Invalid packet data!")
        else:
            self.size = str(size).zfill(7)
            self.kind: int = packet_kinds.index(self.kind)
            self.header = str(self.size + str(self.kind)).encode('utf-8')
            self.data = self.data.encode('utf-8')

    def send(self):
        self.conn.send(self.header)
        self.conn.send(self.data)


class InboundPacket:
    """A class that makes decoding received packets easier"""

    def __init__(self, conn: socket.socket):
        self.conn = conn

    def receive(self) -> str:
        """Receive data, decode it, and return it."""
        self.header = self.conn.recv(8)
        self.size = int(self.header[:7])

        kind = int(self.header[7:])
        self.kind = packet_kinds[kind]

        data = self.conn.recv(self.size)
        self.data = data.decode('utf-8')

        return self.kind, self.data