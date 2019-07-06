import threading
import time
import datetime
from robotoperator.robotoperator import RobotOperator
from interval_calculator import IntervalCalculator, Counter
import csv

class MarblingOperator(threading.Thread):

    def __init__(self):
        super(MarblingOperator, self).__init__()
        self.stop_event = threading.Event()
        self.sleep_event = threading.Event()
        self.marbling_index = 0
        self.start_marbling_time = 0.0
        self.state = 0  # [0:wait, 1, gaze, 2:marbling 3sleep]
        self.cal = IntervalCalculator()
        # self.stop_thresh = 10
        # self.stop_counter = Counter(self.stop_thresh)
        self.key = None
        self.pulse = 0
        self.interval = self.cal.pulse_to_interval(60)
        self.csv_file = "pulse_data.csv"
        self.last_marble_pulse = 0.0

    def setup_robot(self):
        self.rob = RobotOperator()
        self.rob.connect()

    def set_pulse(self, p):
        print type(p)
        self.pulse = p
        if self.pulse < 10.0:
            self.pulse = int(self.pulse)
        print "[MO]set pulse {} type : {}".format(self.pulse, type(self.pulse))

    def turn_marble_index(self):
        self.marbling_index += 1
        if self.marbling_index is len(self.rob.marble_point):
            self.marbling_index = 0
        print '[MO]:next plate. index is {}'.format(self.marbling_index)

    def still_marbling_time(self):
        now = time.time()
        diff = now - self.start_marbling_time
        if diff < 30:
            return True
        else:
            return False

    def transition(self):
        # print '[[PULSE]] : {}. type {}'.format(self.pulse, type(self.pulse))
        # print "Marbling State before: {}".format(self.state)
        if self.state is 0: # wait
            if int(self.pulse) is -1:
                self.state = 1
                self.rob.gaze()
                print "Marbling State changed to..: {}".format(self.state)

            elif int(self.pulse) is 0:
                self.state = 0

            if self.key is "f":
                self.state = 2
                self.start_marbling_time = time.time()
                self.interval = self.cal.pulse_to_interval(60)
                self.last_marble_pulse = 60
                self.rob.go_top(self.marbling_index, 50.0, interval=0.2)
                self.key = None
        elif self.state is 1: # gaze
            if int(self.pulse) is -1:
                self.state = 1
                if self.key is "f":
                    self.state = 2
                    self.start_marbling_time = time.time()
                    self.interval = self.cal.pulse_to_interval(60)
                    print "[MO]set interval {}".format(self.interval)
                    self.last_marble_pulse = 60
                    self.rob.go_top(self.marbling_index, 50.0, interval=0.2)
                    self.key = None
            elif int(self.pulse) is 0:
                self.rob.go_home()
                self.state = 0
                print "Marbling State changed to..: {}".format(self.state)

            else:
                self.state = 2
                self.start_marbling_time = time.time()
                self.interval = self.cal.pulse_to_interval(self.pulse)
                self.last_marble_pulse = self.pulse
                print "s {}".format(self.last_marble_pulse)
                self.rob.go_top(self.marbling_index, 50.0, interval=0.2)
                print "Marbling State changed to..: {}".format(self.state)

        elif self.state is 2: # marbling
            self.rob.set_speed(True)
            self.rob.marble(self.marbling_index, self.interval)
            if not self.still_marbling_time():
                self.rob.go_top(self.marbling_index, 50.0, interval=0.2)
                self.rob.go_home()
                self.turn_marble_index()
                self.write_pulse_data()
                self.rob.set_speed(False)
                # self.rob.go_top(self.marbling_index, 30.0, interval=0.5)
                self.state = 3
                self.key = None
                print "Marbling State changed to..: {}".format(self.state)

        elif self.state is 3:
            if self.key is "r":
                self.state = 0
                print "Marbling State changed to..: {}".format(self.state)

    def run(self):
        while not self.stop_event.is_set():
            self.transition()
        self.stop_sequence()
        print "[MO]End Robot Operator"

    def stop(self):
        self.stop_event.set()
        print("[MO]:FORCE QUIT SIGNAL RECEIVED=======")

    def stop_sequence(self):
        self.rob.set_speed(False)
        self.rob.go_home()
        self.rob.disconnect()

    def write_pulse_data(self):
        with open(self.csv_file, 'a') as fd:
            t = datetime.datetime.now()
            writer= csv.writer(fd)
            dl = [t, self.last_marble_pulse]
            writer.writerow(dl)
