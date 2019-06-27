import time
from glob import glob
from lib.interface import waitKey

from dobot import Dobot
# from get_pulse import getPulseApp

import threading

# from pythonosc import dispatcher
# from pythonosc import osc_server

OSC_IP = "127.0.0.1"
OSC_PORT = 5005
OSC_ADDRESS = "/bpm"


class RobotOperator(threading.Thread):

    def __init__(self):
        super(RobotOperator, self).__init__()
        self.speed = 800
        self.acceleration = 800
        self.rob = None
        self.def_r = 0.0
        self.def_rotate = 186.0
        self.operation_interval = 2.0
        self.move_z = 30.0
        self.connect()
        self.bMarbling = True
        self.interval = 0
        self.stop_event = threading.Event()
        self.key_controls = {"m": self.toggle_marbling}
        self.marble_count = 0
        self.marble_point = {"x": 200.0, "y": 200.0, "z": -62.0}
        self.rob.speed(self.speed, self.acceleration)
        time.sleep(1.0)

    def connect(self):
        available_ports = glob('/dev/ttyUSB*')
        print available_ports
        if len(available_ports) == 0:
            print 'no port found for Dobot Magician'
            exit(1)
        self.rob = Dobot(port=available_ports[0], verbose=True)
        time.sleep(1.0)

    def set_interval(self, interval):
        interval = float(interval)
        if type(interval) is int:
            if interval > 0.0:
                self.interval = interval
                print 'interval = {}'.format(iself.interval)

    def toggle_marbling(self):
        self.bMarbling = not self.bMarbling

    def marble(self):
        print 'marble'
        x = self.marble_point["x"]
        y = self.marble_point["y"]
        z = self.marble_point["z"] + self.move_z
        r = self.def_r
        self.rob.go(x, y, z, r)
        time.sleep(self.operation_interval)
        z = self.marble_point["z"]
        self.rob.go(x,y,z,r)
        time.sleep(self.operation_interval)
        z = self.marble_point["z"] + self.move_z
        self.rob.go(x,y,z,r)
        time.sleep(self.operation_interval)
        r = self.def_rotate
        self.rob.go(x,y,z,r)
        time.sleep(self.operation_interval)
        z = self.marble_point["z"]
        self.rob.go(x,y,z,r)
        time.sleep(self.operation_interval)
        z = self.marble_point["z"] + self.move_z
        r = self.def_rotate
        self.rob.go(x,y,z,r)
        time.sleep(self.operation_interval)
        self.marble_count += 1

    def refill(self):
        print 'refill'
        x = self.marble_point["x"]
        y = self.marble_point["y"] + 20
        z = self.marble_point["z"] + self.move_z
        r = self.def_r
        self.rob.go(x,y,z,r)
        # self.rob.go(self.marble_point["x"],
        #             self.marble_point["y"], -20.0, 90.0)
        # self.rob.go(self.marble_point["x"], self.marble_point["y"], 0.0, 90.0)
        # self.rob.go(self.marble_point["x"], self.marble_point["y"], 0.0)

    def run(self):
        while not self.stop_event.is_set():
            # self.key_handler()
            if self.bMarbling:
                self.marble()
                # time.sleep(self.interval)
                time.sleep(1.0)
                if self.marble_count is 5:
                    self.refill()
                    self.marble_count = 0
            else:
                print 'sleep'
                time.sleep(1.0)
        self.disconnectRobot()
        print "End Robot Operator"

    def get_pose(self):
        pose = self.rob.get_pose()
        print pose

    def disconnectRobot(self):
        self.rob.close()

    def stop(self):
        self.stop_event.set()

    def key_handler(self):
        self.pressed = waitKey(10) & 255

        for key in self.key_controls.keys():
            if chr(self.pressed) == key:
                self.key_controls[key]()

# robotoperation = None
#
# def get_digit(unused_addr, *i):
#     global robotoperation
#     robotoperation.set_interval(i)

from socket import socket, AF_INET, SOCK_DGRAM

HOST = '127.0.0.1'
PORT = 5000

s = socket(AF_INET, SOCK_DGRAM)
s.bind((HOST, PORT))

if __name__ == '__main__':
    global robotoperation
    robotoperation = RobotOperator()
    robotoperation.start()
    # dispatcher = dispatcher.Dispatcher()
    # dispatcher.map(OSC_ADDRESS, get_digit)
    # server = osc_server.ThreadingOSCUDPServer(
    #     (OSC_IP, OSC_PORT), dispatcher)
    # print("Serving on {}".format(server.server_address))
    # server.serve_forever()

    while True:
        try:
            msg, address = s.recvfrom(8192)
            print msg
            robotoperation.join(1)
        except KeyboardInterrupt:
            print 'Ctrl-C received'
            robotoperation.stop()
            s.close()
            break
