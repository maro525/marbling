from pydobot import Dobot
import time
from serial.tools import list_ports


class RobotOperator:
    def __init__(self):
        self.rob = None
        self.marble_z = -63.7
        self.move_z = 18.0
        self.marble_point = [
            {"x":135.9, "y": 229.1},
            {"x": 273.0, "y": 107.8},
            {"x": 264.7, "y": -135.5},
            {"x": 102.0, "y": -253.0},

        ]
        self.home = {"x": 228.1, "y": -3.5, "z": 86.5}
        self.gaze_point = {"x": 295.5, "y":13.9, "z":120.3}
        self.op_interval = 0.5

    def connect(self):
        port = list_ports.comports()[0].device
        self.rob = Dobot(port=port, verbose=True)
        self.set_speed(False)
        time.sleep(1.0)
        self.go_home(self.op_interval)

    def get_pose(self):
        pose = self.rob.get_pose()
        print "pose {}".format(pose)

    def set_speed(self, bFast):
        if bFast:
            self.speed = 800
            self.acceleration = 1200
            self.rob.speed(self.speed, self.acceleration)
        else:
            self.speed = 300
            self.acceleration = 300
            self.rob.speed(self.speed, self.acceleration)

    def go_interval(self, interval):
        if interval is 0.0:
            return
        elif interval < 0.0:
            return
        elif interval > 1.5:
            time.sleep(1.5)
        else:
            time.sleep(interval)

    def go_home(self, interval=None):
        print "[RO]:go home"
        self.set_speed(False)
        self.x=self.home["x"]
        self.y=self.home["y"]
        self.z=self.home["z"]
        self.rob.jump_to(self.x, self.y, self.z, wait=True)
        if interval is None:
            time.sleep(self.op_interval)
        else:
            self.go_interval(interval)

    def go_top(self, index, z_move, interval=None, bWait=False):
        # print "[RO]:go top. {} {}".format(z_move, interval)
        self.x=self.marble_point[index]["x"]
        self.y=self.marble_point[index]["y"]
        self.z=self.marble_z + z_move
        self.rob.move_to(self.x, self.y, self.z, wait=bWait)
        if interval is None:
            time.sleep(self.op_interval)
        else:
            self.go_interval(interval)

    def go_marble_point(self, index, interval=None):
        # print "[RO]go marble point"
        self.x=self.marble_point[index]["x"]
        self.y=self.marble_point[index]["y"]
        self.z=self.marble_z
        self.rob.move_to(self.x, self.y, self.z)
        if interval is None:
            return
        else:
            self.go_interval(interval)

    def gaze(self, interval=0.5):
        print "[RO]gaze {}".format(interval)
        self.set_speed(False)
        self.x = self.gaze_point["x"]
        self.y = self.gaze_point["y"]
        self.z = self.gaze_point["z"]
        self.rob.move_to(self.x, self.y, self.z)
        if interval is not None:
            self.go_interval(interval)

    def marble(self, index, interval):
        # print '[RO]:marble loop'
        # set
        self.set_speed(True)
        self.go_top(index, self.move_z,
                    interval=interval, bWait=False)
        # down
        self.go_marble_point(index, interval)

    def disconnect(self):
        self.rob.close()
