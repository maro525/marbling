# coding : utf-8

import threading

from marbling.marbling_operator import MarblingOperator

mab = None
kb = None

HOST = '127.0.0.1'
PORT = 5000

from socket import socket, AF_INET, SOCK_DGRAM
s = socket(AF_INET, SOCK_DGRAM)
s.bind((HOST, PORT))


class KB(threading.Thread):
    def __init__(self):
        super(KB, self).__init__()
        self.stop_event = threading.Event()
        self.restart_evnet = threading.Event()

    def run(self):
        global key, mab
        while not self.stop_event.is_set():
            print "[KB]:reading input..."
            key = raw_input()
            mab.key = key
        print "[KB]:loop end"

    def stop(self):
        self.stop_event.set()
        print("[KB]:FORCE QUIT SIGNAL RECEIVED=======")


def start_marblingoperation():
    global mab
    mab = MarblingOperator()
    mab.setup_robot()
    mab.start()


def start_kb():
    global kb
    kb = KB()
    kb.start()


if __name__ == '__main__':
    start_marblingoperation()
    start_kb()
    while True:
        try:
            msg, address = s.recvfrom(8192)
            data = int(float(msg))
            print ("->{}".format(data))
            mab.pulse = data
            mab.join(1)
            kb.join(1)
        except KeyboardInterrupt:
            mab.stop()
            kb.stop()
            s.close()
            break
    print("====PROGRAM FINISHED======")
