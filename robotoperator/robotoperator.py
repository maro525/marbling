from pydobot import Dobot
import time


class RobotOperator:
    def __init__(self):
        self.rob = None
        self.marble_z = -75.2
        self.move_z = 11.0
        self.marble_point = [
            {"x": 196.4, "y": -83.9},
            {"x": 229.2, "y": 113.3},
            {"x": 61.3, "y": 194.4},
        ]
        self.home = {"x": 150.0, "y": 150.0, "z": 200.0}
        self.op_interval = 0.5

    def connect(self):
        port = list_ports.comports()[0].device
        self.rob = Dobot(port=port, verbose=True)
        self.set_speed(False)
        time.sleep(1.0)
        self.go_init_pos(self.r1)

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
            self.rob.speed(self.speed, self.acceleration

    def go_home(self, interval):
        print "[RO]:go home"
        self.set_speed(False)
        self.x=self.home["x"]
        self.y=self.home["y"]
        self.z=self.home["z"]
        self.rob.jump_to(self.x, self.y, self.z, wait=True)
        time.sleep(interval)

    def go_top(self, index, z_move, interval=self.op_interval, bWait=True):
        print "[RO]:go top"
        self.x=self.marble_point[index]["x"]
        self.y=self.marble_point[index]["y"]
        self.z=self.marble_z + z_move
        self.rob.jump_to(self.x, self.y, self.z, wait=bWait)
        time.sleep(interval)

    def go_marble_point(self, index, interval):
        print "go marble point"
        self.x=self.marble_point[index]["x"]
        self.y=self.marble_point[index]["y"]
        self.z=self.marble_z
        self.rob.move_to(self.x, self.y, self.z)
        time.sleep(interval)

    def gaze(self, index, interval):
        print "gaze"
        self.x=self.marble_point[0]["x"]
        self.y=self.marble_point[0]["y"]
        self.z=self.marble_z + 150.0
        self.rob.jump_to(self.x, self.y, self.z, wait=True)
        time.sleep(1.0)
        self.set_speed(False)
        self.rob.go_top(index, interval, 50.0)

    def marble(self, index, interval):
        print '[RO]:marble loop'
        # set
        self.go_top(self.index, self.move_z,
                    interval=interval, bWait=False)
        # down
        self.go_marble_point(index, interval)

    def disconnect(self):
        self.rob.close()
