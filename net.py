"""
Classes that help with networking.

Packet structure:

Every packet has a header, which is sent first before the actual data.
The header is 8 bytes. The first 6 bytes define the size of the packet,
and the last 2 bytes defines the kind of packet.
"""

import enum
import socket
import time


class PacketType(enum.Enum):
    CONNECT = 10
    DISCONNECT = 11
    KEEP_ALIVE = 12
    USERNAME = 13
    ...


class OutboundPacket:
    """A class that makes creating/sending packets easier"""

    def __init__(self, packet_type: PacketType, data: str, conn: socket.socket):
        self.data = data
        self.packet_type = packet_type
        self.conn = conn
        
        self.prep()
    
    def prep(self) -> None:
        """Generates the packet header and encodes the data."""

        self.size = len(self.data.encode('utf-8'))
        if self.size > 9999999:
            raise ValueError("Packet is too big!")
        elif type(self.data) != str:
            raise ValueError("Invalid packet data!")
        else:
            # encode data
            self._data = self.data.encode('utf-8')

            # generate header
            self._size = str(self.size).zfill(6)
            self._packet_type: int = self.packet_type.value
            self.header = str(self._size + str(self._packet_type)).encode('utf-8')

    def send(self):
        self.conn.send(self.header)
        self.conn.send(self._data)


class InboundPacket:
    """A class that makes decoding received packets easier"""

    def __init__(self, conn: socket.socket):
        self.conn = conn

    def receive(self):
        """Receive data, decode it, and return it.
            Returns None if an error occurred."""
        for i in range(50):
            try:
                self.header = self.conn.recv(8)
                self.size = int(self.header[:6])

                self._packet_type = int(self.header[6:])
                self.packet_type = PacketType(self._packet_type)

                self._data = self.conn.recv(self.size)
                self.data = self._data.decode('utf-8')

                return self.data
            except BrokenPipeError:
                return None
            except ValueError:
                time.sleep(0.1)
                continue
        
        return None