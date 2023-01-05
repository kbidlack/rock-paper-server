"""
Classes that help with networking.

Packet structure:

Every packet has a header, which is sent first before the actual data.
The header is 8 bytes. The first 6 bytes define the size of the packet,
and the last 2 bytes defines the kind of packet.
"""

import socket
import threading
from enum import IntEnum


class PacketType(IntEnum):
    CONNECT = 10
    DISCONNECT = 11
    KEEP_ALIVE = 12
    USERNAME = 13
    ...


class Packet:
    """A class that makes creating/sending packets easier"""

    def __init__(self, type: PacketType, data: str, conn: socket.socket):
        self.data = data
        
        self.type = type
        self.conn = conn
        
        self.prep()
    
    @classmethod
    def from_incoming(cls, conn: socket.socket):
        """Create a new Packet object from incoming data.
        Returns None if the connection sent no data.
        Returns False if an error occurred."""
        try:
                header = conn.recv(8)
                size = int(header[:6])

                _type = int(header[6:])
                type = PacketType(_type)

                _data = conn.recv(size)
                data = _data.decode('utf-8')

                return cls(type, data, conn)
        except (BrokenPipeError, ConnectionError):
            return False
        except (ValueError, TimeoutError):
            return None
    
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
            self._type: int = self.type.value
            self.header = str(self._size + str(self._type)).encode('utf-8')

    def send(self):
        self.conn.send(self.header)
        self.conn.send(self._data)

    def __repr__(self):
        return f"Packet({self.type}, {self.data})"


class PacketQueue(threading.Thread):
    def __init__(self, client):
        super().__init__()

        self.client = client

        self.queue = []
    
    def run(self):
        while self.client.game.running:
            packet = Packet.from_incoming(self.client.conn)

            if packet is False:
                self.client.disconnect('Lost connection')
                sys.exit()
            elif packet is None:
                continue
            else:
                self.queue.append(packet)

    def find(self, packet_types: PacketType=[], data=[], remove=True):
        """Find a packet by packet_type, data, or both."""
        if not packet_types and not data:
            found_packets = []
        elif packet_types and not data:
            found_packets = [p for p in self.queue if p.type in packet_types]
        elif data and not packet_types:
            found_packets = [p for p in self.queue if p.data in data]
        else: # data and packet_type
            found_packets = [
                p for p in self.queue 
                if p.data in data and p.type in packet_types
                ]
        
        if remove:
            for packet in found_packets:
                self.queue.remove(packet)

        return found_packets


# so `from net import *` imports all the packet types
globals().update(PacketType.__members__)