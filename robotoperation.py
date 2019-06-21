import time
from glob import glob

# from dobot import Dobot
from get_pulse import getPulseApp

import threading


class RobotOperator(threading.Thread):

    def __init__(self):
        super(RobotOperator, self).__init__()
        self.speed = 10
        self.rob.speed(self.speed)
        self.bMarbling = False
        self.interval = 0
        self.stop_event = threading.Event()
        self.connect()

    def connect(self):
        available_ports = glob('/dev/ttyUSB*')
        print available_ports
        if len(available_ports) == 0:
            print 'no port found for Dobot Magician'
            exit(1)
        self.rob = Dobot(port=available_ports[0], verbose=True)

    @interval.setter
    def interval(self, interval):
        if type(interval) is int:
            if interval > 0.0:
                self.interval = interval

    def marble(self):
        self.rob.go(150.0, 0.0, 25.0)
        time.sleep(0.5)
        self.rob.go(150.0, 0.0, 100.0)

    def run(self):
        while not(self.stop_event):
            if self.bMarbling:
                self.marble()
                time.sleep(self.interval)
        self.disconnectRobot()
        print "End Robot Operator"

    def get_pose(self):
        pose = self.rob.get_pose()
        print pose

    def disconnectRobot(self):
        self.rob.close()

    def stop(self):
        self.stop_event.set()


if __name__ == '__main__':
    rp = RobotOperator()
    pulseApp = getPulseApp()
    rp.start()
    pulseApp.start()

    while True:
        try:
            rp.join(1)
            pulseApp.join(1)

        except KeyboardInterrupt:
            rp.stop()
            pulseApp.stop()
            break
