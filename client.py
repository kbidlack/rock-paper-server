import socket
import threading

from packet import InboundPacket, OutboundPacket


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # while True:
    #     try:
    #         address = input("Enter server address: ")
    #         port = int(input("Enter server port: "))

    #         ADDR = address, port
    #         client.connect(ADDR)

    #         break
    #     except ValueError:
    #         print("Invalid port! Please try again.")
    #         continue
    #     except ConnectionRefusedError:
    #         print("Connection refused! Please try again.")
    #         continue
    #     except socket.gaierror as e:
    #         print(e, "Please try again.")
    #         continue

    # print(f"Connected to {ADDR[0]}:{ADDR[1]}!")

    # connected = True
    # username = input("Enter a username: ")

    # if len(username) > 36:
    #     print("Invalid username!")
    #     sys.exit()
    
    client.connect(('localhost', 54321))
    username = 'helloworld'
    username_packet = OutboundPacket(kind='username', data=username, conn=client)
    username_packet.send()


if __name__ == "__main__":
    main()