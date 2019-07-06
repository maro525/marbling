# coding : utf-8

# from socket import socket, AF_INET, SOCK_DGRAM
import threading

from pulsedetector.get_pulse import getPulseApp
from marbling.marbling_operator import MarblingOperator

mab = None
kb = None
pa = None

# HOST = '127.0.0.1'
# PORT = 5000
# s = socket(AF_INET, SOCK_DGRAM)
# s.bind((HOST, PORT))


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


def start_pulse_app():
    global pa
    pa = getPulseApp()
    pa.start()


if __name__ == '__main__':
    start_marblingoperation()
    start_kb()
    start_pulse_app()
    while True:
        try:
            # msg, address = s.recvfrom(8192)
            # data = int(float(msg))
            # print("pulse->{}".format(pa.data))
            mab.pulse = pa.data
            # mab.set_pulse(pa.data)
            mab.join(1)
            kb.join(1)
            pa.join(1)
        except KeyboardInterrupt:
            pa.stop()
            mab.stop()
            kb.stop()
            # s.close()
            break
    print("====PROGRAM FINISHED======")
