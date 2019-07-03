# coding : utf-8

import threading

from marbling_operator import MarblingOperator
from communication import Communication

mab = None
kb = None
com = None

HOST = '127.0.0.1'
PORT = 5000


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


def start_communication():
    global com
    com = Communication(HOST, PORT)


def main():
    global mab, kb, com
    start_marblingoperation()
    start_kb()
    start_communication()
    while True:
        try:
            mab.set_pulse(com.recv())
            mab.join(1)
            kb.join(1)
        except KeyboardInterrupt:
            mab.stop()
            kb.stop()
            com.close()
            break


if __name__ == '__main__':
    main()
    print("====PROGRAM FINISHED======")
