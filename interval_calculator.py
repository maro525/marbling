import numpy as np


class Counter:
    def __init__(self, thresh=0):
        self.count = 0
        self.thresh = thresh

    def add(self):
        self.count += 1

    def isOverThresh(self):
        return self.count > self.thresh

    def isZero(self):
        return self.

    def reset(self):
        self.count = 0

    def finish(self):
        self.count = self.thresh + 1


class IntervalCalculator:

    def __init__(self):
        self.interval = 1.0
        self.marble_interval = 0.5
        self.normal = 0.5
        self.sigmoid_counter = Counter()

    def get(self, pulse):
        if self.pulse == -1:
            self.interval = self.interval * \
                self.pulse_sigmoid(self.sigmoid_counter.count)
            self.sigmoid_counter.add()
            return self.interval
        else:
            self.sigmoid_counter.reset()
            self.pulse_to_interval()
            print '[IC]:marbling interval {}'.format(self.marble_interval)
            return self.marble_interval

    def pulse_to_interval(self):
        self.marble_interval = (float(self.pulse) / float(60)) - 0.5

    def pulse_sigmoid(self, x=0):
        return 2 - 1/(1+np.exp(10-x))
