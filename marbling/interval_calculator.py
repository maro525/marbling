import numpy as np


class Counter:
    def __init__(self, thresh=0):
        self.count = 0
        self.thresh = thresh
        self.bCounting = False

    def start(self):
        self.bCounting = True

    def add(self):
        if self.bCounting is False:
            self.bCounting = True
        self.count += 1

    def isOverThresh(self):
        if self.count > self.thresh:
            self.bCounting = False
            return True

    def isZero(self):
        return self.count is 0

    def isCounting(self):
        return self.bCounting

    def reset(self):
        self.count = 0
        self.bCounting = False

    def finish(self):
        self.count = self.thresh + 1


class IntervalCalculator:

    def __init__(self):
        self.interval = 1.0
        self.marble_interval = 0.2
        self.normal = 0.5
        self.sigmoid_counter = Counter()

    def get(self, pulse):
        if pulse is -1:
            self.interval = self.interval * \
                self.pulse_sigmoid(self.sigmoid_counter.count)
            print '[IC]:sigmoid interval {}'.format(self.interval)
            self.sigmoid_counter.add()
            return self.interval
        elif pulse is 0:
            print '[IC]:last marble interval {}'.format(self.marble_interval)
            return self.marble_interval
        else:
            self.sigmoid_counter.reset()
            self.pulse_to_interval(pulse)
            print '[IC]:marbling interval {}'.format(self.marble_interval)
            return self.marble_interval

    def pulse_to_interval(self, pulse):
        self.marble_interval = (float(pulse) / float(60))
        if self.marble_interval < 0.0:
            self.marble_interval = 0.0

    def pulse_sigmoid(self, x=0):
        return 2 - 1/(1+np.exp(10-x))
