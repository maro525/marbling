# coding : utf-8

from socket import socket, AF_INET, SOCK_DGRAM
import time
from glob import glob
from lib.interface import waitKey
from serial.tools import list_ports
import numpy as np

from pydobot import Dobot
# from get_pulse import getPulseApp

import threading

# from pythonosc import dispatcher
# from pythonosc import osc_server

OSC_IP = "127.0.0.1"
OSC_PORT = 5005
OSC_ADDRESS = "/bpm"

HOST = '127.0.0.1'
PORT = 5000

robotoperation = None
kb = None
# restart_flag = True

s = socket(AF_INET, SOCK_DGRAM)
s.bind((HOST, PORT))

key = None

# push enter twice
class KB(threading.Thread):
    def __init__(self):
        super(KB, self).__init__()
        self.stop_event = threading.Event()
        self.restart_evnet = threading.Event()

    def run(self):
        global key
        while not self.stop_event.is_set():
            print "loop"
            key = raw_input()
            # if key is "r":
            #     self.restart_evnet.set()
            #     self.stop_event.set()
            #     print("KB:RESTART SIGNAL RECEIVED=======")
            #     # key = None
            #     break
        print "KB:loop end"

    def stop(self):
        self.stop_event.set()
        print("KB:FORCE QUIT SIGNAL RECEIVED=======")


class RobotOperator(threading.Thread):

    def __init__(self):
        super(RobotOperator, self).__init__()
        self.rob = None
        self.r1 = -40.0
        self.r2 = 186.0
        self.r_normal = True
        self.operation_interval = 0.5
        self.normal_marble_interval = 0.5
        self.marbling_interval = self.normal_marble_interval
        self.move_z = 11.0
        self.bMarbling = False
        self.previous_bMarbling = False
        self.stop_event = threading.Event()
        # self.marble_count = 0  # count of plate transition
        self.marbling_count = 0  # count of marbling in one plate
        self.marble_index = 0
        self.marble_z = -75.2
        self.marble_point = [
            {"x": 196.4, "y": -83.9},
            {"x": 229.2, "y": 113.3},
            {"x": 61.3, "y": 194.4},
        ]

        self.pulse = 0  # pulse
        self.bStopping = False  # marbling
        self.stop_count = 0  # stop_count
        self.wait_count = 10

    def connect(self):
        port = list_ports.comports()[0].device
        self.rob = Dobot(port=port, verbose=True)
        self.set_speed(False)
        time.sleep(1.0)
        self.go_init_pos(self.r1)

    def restart(self):
        print "restart"

    def pass_wait_count(self):
        print "pass wait count"
        self.stop_count = self.wait_count+1

    def set_speed(self, bFast):
        if bFast:
            self.speed = 800
            self.acceleration = 1200
            self.rob.speed(self.speed, self.acceleration)
        else:
            self.speed = 300
            self.acceleration = 300
            self.rob.speed(self.speed, self.acceleration)

    def toggle_marbling(self):
        self.bMarbling = not self.bMarbling

    def turn_marble_index(self):
        self.marble_index += 1
        if self.marble_index is len(self.marble_point)-1:
            self.rob.jump_to(
                self.marble_point[2]["x"], self.marble_point[2]["y"], self.marble_z+100, self.r1, wait=True)
            self.marble_index = 0
        print 'add marble. index is {}'.format(self.marble_index)

    def set_marbling_interval(self):
        if self.pulse == -1:  # face detected
            self.stop_count = 0
            self.set_speed(True)
            self.bMarbling = True
            self.marbling_interval = self.normal_marble_interval
            self.operation_interval = self.normal_marble_interval
        elif self.pulse == 0:  # face not detected
            if self.bMarbling is False:
                return
            if not self.bStopping:
                self.bStopping = True
                print 'Stopping...'
            self.stop_count += 1  # s
            print 'Stopping...{}'.format(self.stop_count)
            # wait_count
            if self.stop_count > self.wait_count:
                self.set_speed(False)
                self.bMarbling = False
                self.go_top(self.r1)
                self.turn_marble_index()
                self.go_top(self.r1)
                self.stop_count = 0
                self.bStopping = False
            self.marbling_interval = self.normal_marble_interval

        else:  # getting pulse
            if self.bMarbling is False:
                self.bMarbling = True

            self.operation_interval = 0.0
            self.marbling_interval = (float(self.pulse) / float(60)) - 0.5
            print 'marble interval {}'.format(self.marbling_interval)

    def go_top(self, r):
        print "go top"
        self.x = self.marble_point[self.marble_index]["x"]
        self.y = self.marble_point[self.marble_index]["y"]
        self.z = self.marble_z + 100.0
        self.rob.jump_to(self.x, self.y, self.z, r, wait=True)
        time.sleep(self.operation_interval)
        if r is self.r1:
            self.r_normal = True
        else:
            self.r_normal = False

    def go_init_pos(self, r):
        print "go init pos"
        self.x = self.marble_point[self.marble_index]["x"]
        self.y = self.marble_point[self.marble_index]["y"]
        self.z = self.marble_z + 100.0
        self.rob.jump_to(self.x, self.y, self.z, r)
        time.sleep(self.operation_interval)
        if r is self.r1:
            self.r_normal = True
        else:
            self.r_normal = False

    def go_home(self, r):
        print "go home"
        self.x = self.marble_point[self.marble_index]["x"]
        self.y = self.marble_point[self.marble_index]["y"]
        self.z = self.marble_z + self.move_z
        self.rob.move_to(self.x, self.y, self.z, r)
        time.sleep(self.operation_interval)
        if r is self.r1:
            self.r_normal = True
        else:
            self.r_normal = False

    def go_marble_point(self, r):
        print "go marble point"
        self.x = self.marble_point[self.marble_index]["x"]
        self.y = self.marble_point[self.marble_index]["y"]
        self.z = self.marble_z
        self.rob.move_to(self.x, self.y, self.z, r)
        time.sleep(self.marbling_interval)
        if r is self.r1:
            self.r_normal = True
        else:
            self.r_normal = False

    def going_marble_point(self, r):
        print "going marble point"
        self.x = self.marble_point[self.marble_index]["x"]
        self.y = self.marble_point[self.marble_index]["y"]
        self.z = self.marble_z + 50
        self.rob.move_to(self.x, self.y, self.z, r)
        time.sleep(self.marbling_interval)
        if r is self.r1:
            self.r_normal = True
        else:
            self.r_normal = False

    def go_first_marble_point(self, r):
        print "go first marble point"
        self.x = self.marble_point[self.marble_index]["x"]
        self.y = self.marble_point[self.marble_index]["y"]
        self.z = self.marble_z + self.move_z
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
        print 'marble loop'
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
        # self.marble_count += 1

    # def refill(self):
    #     print 'refill'
        # x = self.marble_point["x"]
        # y = self.marble_point["y"] + 20
        # z = self.marble_point["z"] + self.move_z
        # r = self.r1
        # self.rob.go(x,y,z,r)
        # self.rob.go(self.marble_point["x"],
        #             self.marble_point["y"], -20.0, 90.0)
        # self.rob.go(self.marble_point["x"], self.marble_point["y"], 0.0, 90.0)
        # self.rob.go(self.marble_point["x"], self.marble_point["y"], 0.0)

    def gaze(self):
        print "gaze"
        self.x = self.marble_point[2]["x"]
        self.y = self.marble_point[2]["y"]
        self.z = self.marble_z + 150.0
        self.rob.jump_to(self.x, self.y, self.z, self.r1, wait=True)
        time.sleep(1.0)
        self.set_speed(False)
        self.going_marble_point(self.r1)

    def pulse_sigmoid(self, x=0):
        return 2 - 1/(1+np.exp(10-x))

    def run(self):
        while not self.stop_event.is_set():
            self.key_handler()
            self.previous_bMarbling = self.bMarbling
            # print self.previous_bMarbling
            self.set_marbling_interval()
            if self.bMarbling:
                print "marbling_interval {}".format(self.marbling_interval)
                if not self.previous_bMarbling:
                    self.gaze()
                    self.marbling_count = 0
                else:
                    print "marbling start"
                    if self.marbling_count < 15:
                        print "marbling_count {}".format(self.marbling_count)
                        self.marbling_interval = self.marbling_interval * \
                            self.pulse_sigmoid(self.marbling_count)
                        self.marbling_count += 1
                    self.marble()
                    # if self.marble_count is 5:
                    #     self.refill()
                    #     self.marble_count = 0
            else:
                print 'sleep'
                time.sleep(1.0)
        self.stop_sequence()
        print "End Robot Operator"

    def get_pose(self):
        pose = self.rob.get_pose()
        print "pose {}".format(pose)

    def disconnectRobot(self):
        self.rob.close()

    def stop(self):
        self.stop_event.set()
        print("RH:FORCE QUIT SIGNAL RECEIVED=======")

    def stop_sequence(self):
        self.go_init_pos(self.r1)
        self.disconnectRobot()

    def key_handler(self):
        global key
        if key is not None:
            print "{} get!".format(key)
        elif key is "p":
            self.pass_wait_count()

# def restart_handle():
#     global key, kb, robotoperation
#     if kb.restart_evnet.is_set():
#         robotoperation.stop_sequence()
#         robotoperation = None
#         kb = None
#         key = None
#         return True
    # else:
        # return False

def start_robotoperation():
    global robotoperation
    robotoperation = RobotOperator()
    robotoperation.connect()
    robotoperation.start()

def start_kb():
    global kb
    kb = KB()
    kb.start()

# def main(s):
def main():
    global robotoperation, kb
    start_robotoperation()
    start_kb()
    # restart_flag = False
    while True:
        try:
            msg, address = s.recvfrom(8192)
            data = int(float(msg))
            robotoperation.pulse = data
            robotoperation.join(1)
            kb.join(1)
            # restart_flag = restart_handle()
            # if restart_flag is True:
                # s.close()
                # break
        except KeyboardInterrupt:
            robotoperation.stop()
            kb.stop()
            s.close()
            break

if __name__ == '__main__':
    # while restart_flag:
    # s = socket(AF_INET, SOCK_DGRAM)
    # s.bind((HOST, PORT))
    main()
    # print("===============restart")
    # time.sleep(2)
