# coding : utf-8

from socket import socket, AF_INET, SOCK_DGRAM
import time
from glob import glob
from lib.interface import waitKey
from serial.tools import list_ports

from pydobot import Dobot
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
        self.r1 = 0.0
        self.r2 = 186.0
        self.r_normal = True
        self.operation_interval = 2.0
        self.normal_marble_interval = 2.0
        self.marbling_interval = self.normal_marble_interval
        self.move_z = 10.0
        self.bMarbling = True
        self.stop_event = threading.Event()
        self.marble_count = 0
        self.marble_index = 0
        self.marble_z = -30.2
        self.marble_point = [
            {"x": 183.0, "y": -71.1},
            {"x": 197.7, "y": 23.3},
            {"x": 176.3, "y": 130.7},
            {"x": 91.6, "y": 192.6},
            {"x": -14.2, "y": 197.6},
        ]

        self.pulse = 0  # pulse
        self.bStopping = False  # marbling
        self.stop_count = 0  # stop_count
        self.wait_count = 2

    def connect(self):
        port = list_ports.comports()[0].device
        self.rob = Dobot(port=port, verbose=True)
        self.rob.speed(self.speed, self.acceleration)
        time.sleep(1.0)
        self.go_home(self.r1)

    def toggle_marbling(self):
        self.bMarbling = not self.bMarbling

    def turn_marble_index(self):
        self.marble_index += 1
        if self.marble_index is 5:
            self.marble_index = 0

    def set_marbling_interval(self):
        if self.pulse == -1:
            self.bMarbling = True
            self.marbling_interval = self.normal_marble_interval
        elif self.pulse == 0:
            if self.bMarbling is False:
                return
            if not self.bStopping:
                self.bStopping = True
                print 'Stopping...'
            self.stop_count += 1  # s
            print 'Stopping...{}'.format(self.stop_count)
            # wait_count
            if self.stop_count > self.wait_count:
                self.bMarbling = False
                self.turn_marble_index()
                self.stop_count = 0
                self.bStopping = False
        else:
            self.operation_interval = 0.0
            self.marbling_interval = (float(self.pulse) / float(60)) - 0.5
            print 'marble interval {}'.format(self.marbling_interval)

    def go_home(self, r):
        self.x = self.marble_point[marble_index]["x"]
        self.y = self.marble_point[marble_index]["y"]
        self.z = self.marble_z + self.move_z
        self.rob.move_to(self.x, self.y, self.z, r)
        time.sleep(self.operation_interval)
        if r is self.r1:
            self.r_normal = True
        else:
            self.r_normal = False

    def go_marble_point(self, r):
        self.x = self.marble_point[marble_index]["x"]
        self.y = self.marble_point[marble_index]["y"]
        self.z = self.marble_z
        self.rob.move_to(self.x, self.y, self.z, r)
        time.sleep(self.marbling_interval)
        if r is self.r1:
            self.r_normal = True
        else:
            self.r_normal = False

    def rotate(self):
        if self.r_normal:
            r = self.r2
            self.rob.go(self.x, self.y, self.z, r)
            self.r_normal = False
        else:
            r = self.r1
            self.rob.go(self.x, self.y, self.z, r)
            self.r_normal = True
        time.sleep(self.operation_interval)

    def marble(self):
        print 'marble'
        # set
        self.go_home(self.r1)
        # down
        self.go_marble_point(self.r1)
        # # up
        # self.go_home(self.r1)
        # # rotate
        # self.rotate()
        # # down
        # self.go_marble_point(self.r2)
        # # up
        # self.go_home(self.r2)
        # # rotate
        # self.rotate()
        self.marble_count += 1

    def refill(self):
        print 'refill'
        # x = self.marble_point["x"]
        # y = self.marble_point["y"] + 20
        # z = self.marble_point["z"] + self.move_z
        # r = self.r1
        # self.rob.go(x,y,z,r)
        # self.rob.go(self.marble_point["x"],
        #             self.marble_point["y"], -20.0, 90.0)
        # self.rob.go(self.marble_point["x"], self.marble_point["y"], 0.0, 90.0)
        # self.rob.go(self.marble_point["x"], self.marble_point["y"], 0.0)

    def run(self):
        while not self.stop_event.is_set():
            # self.key_handler()
            self.set_marbling_interval()
            if self.bMarbling:
                self.marble()
                # time.sleep(1.0)
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


HOST = '127.0.0.1'
PORT = 5000

s = socket(AF_INET, SOCK_DGRAM)
s.bind((HOST, PORT))

if __name__ == '__main__':
    global robotoperation
    robotoperation = RobotOperator()
    robotoperation.connect()
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
            data = int(float(msg))
            robotoperation.pulse = data
            robotoperation.join(1)
        except KeyboardInterrupt:
            print 'Ctrl-C received'
            robotoperation.stop()
            s.close()
            break
