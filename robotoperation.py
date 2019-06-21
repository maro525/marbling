import time
from glob import glob

from dobot import Dobot


class RobotOperator:

    def __init__(self):
        self.speed = 10

    def connect(self):
        available_ports =  glob('/dev/ttyUSB*')
        print available_ports
        if len(available_ports) == 0:
            print 'no port found for Dobot Magician'
            exit(1)
        self.rob = Dobot(port=available_ports[0], verbose=True)

    def move(self):
        self.rob.speed(self.speed)
        self.rob.go(250.0, 0.0, 25.0)
        time.sleep(2)
        self.rob.go(150.0, 0.0, 25.0)
        time.sleep(2)

    def get_pose(self):
        pose = self.rob.get_pose()
        print pose

    def disconnect(self):
        self.rob.close()

if __name__ == '__main__':
    rp = RobotOperator()
    rp.connect()
    rp.get_pose()
    rp.move()
