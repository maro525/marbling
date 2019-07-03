
from serial.tools import list_ports
from socket import socket, AF_INET, SOCK_DGRAM

HOST = '127.0.0.1'
PORT = 5000


class Communication:

    def __init__(self, host, port):
        self.s = socket(AF_INET, SOCK_DGRAM)
        self.s.bind((host, port))

    def recv(self):
        msg, address = self.s.recvfrom(8192)
        data = int(float(msg))

    def close(self):
        self.s.close()
