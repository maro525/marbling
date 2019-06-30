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
        self.r1 = 0.0
        self.r2 = 186.0
        self.r_normal = True
        self.operation_interval = 0.5
        self.min_interval = 0.8
        self.normal_marble_interval = 1.0
        self.marbling_interval = self.normal_marble_interval
        self.normal_pulse = 72
        self.move_z = 50.0
        self.connect()
        self.bMarbling = False
        self.interval = 0
        self.stop_event = threading.Event()
        self.key_controls = {"m": self.toggle_marbling}
        self.marble_count = 0
        self.marble_point = {"x": 200.0, "y": 220.0, "z": -62.0}
        self.rob.speed(self.speed, self.acceleration)
        time.sleep(1.0)
        self.pulse = 0
        self.go_home(self.r1)
        self.bStopping = False
        self.stop_count = 0
        self.wait_count = 2

    def connect(self):
        available_ports = glob('/dev/ttyUSB*')
        print available_ports
        if len(available_ports) == 0:
            print 'no port found for Dobot Magician'
            exit(1)
        self.rob = Dobot(port=available_ports[0], verbose=True)
        time.sleep(1.0)
        self.x = 200.0
        self.y = 200.0
        self.z = 200.0

    def set_interval(self, interval):
        interval = float(interval)
        if type(interval) is int:
            if interval > 0.0:
                self.interval = interval
                print 'interval = {}'.format(iself.interval)

    def toggle_marbling(self):
        self.bMarbling = not self.bMarbling

    def set_marbling_interval(self):
        if self.pulse == -1:
            self.bMarbling = True
            self.marbling_interval = self.normal_marble_interval
        elif self.pulse == 0:
            if not self.bStopping:
                self.bStopping = True
            self.stop_count += 1
            print 'wait..'
            if self.stop_count > self.wait_count:
                self.bMarbling = False
                self.stop_count = 0
                self.bStopping = False
        else:
            self.marbling_interval = 2.0 - self.normal_marble_interval * self.pulse / self.normal_pulse
            if self.marbling_interval < self.min_interval:
                self.marbling_interval = self.min_interval

    def go_home(self, r):
        self.x = self.marble_point["x"]
        self.y = self.marble_point["y"]
        self.z = self.marble_point["z"] + self.move_z
        self.rob.go(self.x, self.y, self.z, r)
        time.sleep(self.operation_interval)
        if r is self.r1:
            self.r_normal = True
        else:
            self.r_normal = False

    def go_marble_point(self, r):
        self.x = self.marble_point["x"]
        self.y = self.marble_point["y"]
        self.z = self.marble_point["z"]
        self.rob.go(self.x, self.y, self.z, r)
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
        # up
        self.go_home(self.r1)
        # rotate
        # self.rotate()
        # down
        # self.go_marble_point(self.r2)
        # up
        # self.go_home(self.r2)
        # rotate
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
            data = int(float(msg))
            print data
            robotoperation.pulse = data
            robotoperation.join(1)
        except KeyboardInterrupt:
            print 'Ctrl-C received'
            robotoperation.stop()
            s.close()
            break
