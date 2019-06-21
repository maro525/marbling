import time
from glob import glob
from lib.interface import waitKey

from dobot import Dobot
# from get_pulse import getPulseApp

import threading


class RobotOperator(threading.Thread):

    def __init__(self):
        super(RobotOperator, self).__init__()
        self.speed = 10
        self.rob = None
        self.connect()
        self.bMarbling = True
        self.interval = 0
        self.stop_event = threading.Event()
        self.key_controls = {"m": self.toggle_marbling}

    def connect(self):
        available_ports = glob('/dev/ttyUSB*')
        print available_ports
        if len(available_ports) == 0:
            print 'no port found for Dobot Magician'
            exit(1)
        self.rob = Dobot(port=available_ports[0], verbose=True)
        time.sleep(1.0)

    def set_interval(self, interval):
        if type(interval) is int:
            if interval > 0.0:
                self.interval = interval
                print 'interval = {}'.format(iself.interval)

    def toggle_marbling(self):
        self.bMarbling = not self.bMarbling

    def marble(self):
        print 'marble'
        x = 100.0
        y = 0.0
        z = -20.0
        self.rob.speed(100)
        self.rob.go(x, y, z)
        time.sleep(2.0)
        self.rob.speed(100)
        z = 0.0
        self.rob.go(x, y, z)

    def run(self):
        while not self.stop_event.is_set():
            # self.key_handler()
            if self.bMarbling:
                self.marble()
                # time.sleep(self.interval)
                time.sleep(5.0)
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


if __name__ == '__main__':
    robotoperation = RobotOperator()
    robotoperation.start()

    while True:
        try:
            robotoperation.join(1)
        except KeyboardInterrupt:
            print 'Ctrl-C received'
            robotoperation.stop()
            break
