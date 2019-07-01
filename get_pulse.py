from lib.processors_noopenmdao import findFaceGetPulse
from lib.interface import plotXY, imshow, waitKey, destroyWindow
from cv2 import moveWindow
import cv2
import argparse
import numpy as np
import datetime
# TODO: work on serial port comms, if anyone asks for it
# from serial import Serial
import socket
import sys
import threading

# from pythonosc import osc_message_builder
# from pythonosc import udp_client

from socket import socket, AF_INET, SOCK_DGRAM

IP = "127.0.0.1"
PORT = 5000
VIDEO_NUM = 0


class getPulseApp(threading.Thread):

    def __init__(self):
        super(getPulseApp, self).__init__()
        self.stop_event = threading.Event()

        self.selected_cam = VIDEO_NUM

        self.camera = cv2.VideoCapture(self.selected_cam)
        self.w, self.h = 0, 0
        self.pressed = 0

        self.processor = findFaceGetPulse(bpm_limits=[50, 160],
                                          data_spike_limit=2500.,
                                          face_detector_smoothness=10.)

        # Init parameters for the cardiac data plot
        self.bpm_plot = False
        self.plot_title = "Data display - raw signal (top) and PSD (bottom)"

        self.udp_socket = socket(AF_INET, SOCK_DGRAM)

        self.loop_count = 0

    @property
    def bpm(self):
        return self.processor.bpm

    def toggle_cam(self):
        # if len(self.cameras) > 1:
        self.processor.find_faces = True
        self.bpm_plot = False
        destroyWindow(self.plot_title)
        # self.selected_cam += 1
        # self.selected_cam = self.selected_cam % len(self.cameras)elimiter=',')

    def make_bpm_plot(self):
        plotXY([[self.processor.times,
                 self.processor.samples],
                [self.processor.freqs,
                 self.processor.fft]],
               labels=[False, True],
               showmax=[False, "bpm"],
               label_ndigits=[0, 0],
               showmax_digits=[0, 1],
               skip=[3, 3],
               name=self.plot_title,
               bg=self.processor.slices[0])


    def close(self):
        self.camera.release()
        cv2.destroyAllWindows()
        self.udp_socket.close()

    def run(self):
        while not self.stop_event.is_set():
            self.main_loop()
        self.close()

    def stop(self):
        self.stop_event.set()

    def main_loop(self):
        # Get current image frame from the camera
        _, frame = self.camera.read()
        self.h = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.w = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)

        # set current image frame to the processor's input
        # self.processor.frame_in = frame
        # process the image frame to perform all needed analysis
        # self.processor.run()
        # collect the output frame for display
        # output_frame = self.processor.frame_out

        # show the processed/annotated output frame
        cv2.imshow("Processed", frame)

        # create and/or update the raw data display if needed
        if self.bpm_plot:
            self.make_bpm_plot()

        self.loop_count += 1
        if self.loop_count is 30:
            self.send_bpm()
            self.loop_count = 0

    def send_bpm(self):
        bpm = self.processor.send_data
        print bpm
        if bpm is None or bpm is 0:
            bpm = 0
        msg = str(bpm)
        self.udp_socket.sendto(msg.encode(), (IP, PORT))


if __name__ == '__main__':
    pulseApp = getPulseApp()
    pulseApp.start()

    while True:
        try:
            pulseApp.join(1)
        except KeyboardInterrupt:
            print 'Ctrl-C received'
            pulseApp.stop()
            break
