import threading
import time
from robotoperator.robotoperator import RobotOperator
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
        self.pulse = 0

    def setup_robot(self):
        self.rob = RobotOperator()
        self.rob.connect()

    def set_pulse(self, p):
        self.pulse = p
        # print "[MO]set pulse {}".format(self.pulse)


    def turn_marble_index(self):
        self.marble_index += 1
        if self.marble_index is len(self.rob.marble_point)-1:
            self.rob.go_top(0, 100.0)
            self.marble_index = 0
        print '[MO]:next plate. index is {}'.format(self.marble_index)

    def set_state(self, state):
        # print "[MO]self.state:{} state:{}".format(self.state, state)
        if state < 0 or state > 3:
            print '[MO]cannot set state!!!'
        elif self.state is not state:
            print '[MO]State has changed from {} ---> {}!'.format(self.state, state)
            self.state = state

    def transition(self):
        if self.pulse == 0:  # face not detected
            if self.state is 0:
                self.set_state(0)
                return
            self.stop_counter.add()
            print '[MO]Stopping...{}'.format(self.stop_counter.count)
            self.set_state(1)
            # wait_count
            if self.stop_counter.isOverThresh():
                self.set_state(0)
                self.rob.go_home(0.5)
                self.turn_marble_index()
                self.stop_counter.reset()
        else:
            self.stop_counter.reset()
            self.rob.set_speed(True)
            if self.pulse is -1:
                if self.state is 0:
                    self.set_state(2)
                    self.rob.gaze(self.marble_index, 0.4)
                else:
                    self.set_state(2)
            else:
                self.set_state(3)


    def work(self):
        if self.state is not 0:
            interval = self.cal.get(self.pulse)
            self.rob.marble(self.marble_index, interval)
        else:
            print '[MO]sleep'
            time.sleep(1.0)

    def run(self):
        while not self.stop_event.is_set():
            self.key_handler()
            self.transition()
            self.work()
        self.stop_sequence()
        print "[MO]End Robot Operator"

    def stop(self):
        self.stop_event.set()
        print("[MO]:FORCE QUIT SIGNAL RECEIVED=======")

    def stop_sequence(self):
        self.rob.go_top(0, 100.0)
        self.rob.disconnect()

    # key handlei
    def key_handler(self):
        if self.key is not None:
            print "[MO]no key command"
        elif self.key is "p":
            self.pass_stopping()

    def pass_stopping(self):
        print "[MO]:pass"
        self.set_state(0)
        self.pulse = 0
        self.stop_counter.finish()
