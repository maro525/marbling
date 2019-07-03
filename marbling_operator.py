import threading
from robotoperator.robotoperation import RobotOperator
from interval_calculator import IntervalCalculator, Counter


class MarblingOperator(threading.Thread):

    def __init__(self):
        super(MarblingOperator, self).__init__()
        self.stop_event = threading.Event()
        self.marble_index = 0
        self.state = 0  # [0:sleep, 1, stopping, 2:previousmarbling 3:marbling]
        self.cal = IntervalCalculator()
        self.stop_thresh = 10
        self.stop_counter = Counter(self.stop_thresh)
        self.key = None

    def setup_robot(self):
        self.rob = RobotOperator()
        self.rob.connect()

    def set_pulse(self, p):
        self.pulse = p

    def turn_marble_index(self):
        self.marble_index += 1
        if self.marble_index is len(self.rob.marble_point)-1:
            self.rob.go_top(0, 100.0)
            self.marble_index = 0
        print '[MO]:add marble. index is {}'.format(self.marble_index)

    def set_state(self, state):
        if state < 0 or state > 3:
            print 'cannot set state!!!'
        else if self.state is not state:
            print 'State has changed!'
            if state is 0:
                self.go_home(0.5)
                self.state = state
            elif state is 2:
                self.rob.set_speed(False)
                self.rob.gaze(self.marble_index, 1.0)

    def think(self):
        if self.pulse == 0:  # face not detected
            if self.stop_counter.isZero():
                print '[MO]Stopping...'
                self.set_state(1)
            self.stop_counter.add()
            print '[MO]Stopping...{}'.format(self.stop_counter.count)
            # wait_count
            if self.stop_counter.isOverThresh():
                self.set_state(0)
        else:
            self.stop_counter.reset()
            self.rob.set_speed(True)
            if self.pulse is -1:
                self.set_state(2)
            else:
                self.set_state(3)

    def work(self):
        if self.state is not 0:
            print "marbling_interval {}".format(self.marbling_interval)
            self.rob.marble(self.marble_index, self.marbling_interval)
        else:
            print 'sleep'
            time.sleep(1.0)

    def run(self):
        while not self.stop_event.is_set():
            self.key_handler()
            self.think()
            self.work()
        self.stop_sequence()
        print "End Robot Operator"

    def stop(self):
        self.stop_event.set()
        print("[MO]:FORCE QUIT SIGNAL RECEIVED=======")

    def stop_sequence(self):
        self.rob.go_top(0, 100.0)
        self.rob.disconnect()

    # key handlei
    def key_handler(self):
        if self.key is not None:
            print "{} get!".format(key)
        elif key is "p":
            self.pass_wait_count()

    def pass_wait_count(self):
        print "[MO]:pass wait count"
        self.stop_counter.finish()
