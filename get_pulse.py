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

from pythonosc import osc_message_builder
from pythonosc import udp_client

OSC_IP = "127.0.0.1"
OSC_PORT = 5005
OSC_ADDRESS = "/bpm"


class getPulseApp(threading.Thread):

    """
    Python application that finds a face in a webcam stream, then isolates the
    forehead.

    Then the average green-light intensity in the forehead region is gathered
    over time, and the detected person's pulse is estimated.
    """

    # def __init__(self, args):
    def __init__(self):
        super(getPulseApp, self).__init__()
        self.stop_event = threading.Event()

        self.selected_cam = 0

        self.camera = cv2.VideoCapture(0)
        self.w, self.h = 0, 0
        self.pressed = 0

        self.processor = findFaceGetPulse(bpm_limits=[50, 160],
                                          data_spike_limit=2500.,
                                          face_detector_smoothness=10.)

        # Init parameters for the cardiac data plot
        self.bpm_plot = False
        self.plot_title = "Data display - raw signal (top) and PSD (bottom)"

        self.client = udp_client.UDPClient(OSC_IP, OSC_PORT)
        self.key_controls = {"s": self.toggle_search,
                             "c": self.toggle_cam}

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
        # self.selected_cam = self.selected_cam % len(self.cameras)

    def write_csv(self):
        """
        Writes current data to a csv file
        """
        fn = "Webcam-pulse" + str(datetime.datetime.now())
        fn = fn.replace(":", "_").replace(".", "_")
        data = np.vstack((self.processor.times, self.processor.samples)).T
        np.savetxt(fn + ".csv", data, delimiter=',')
        print("Writing csv")

    def toggle_search(self):
        """
        Toggles a motion lock on the processor's face detection component.

        Locking the forehead location in place significantly improves
        data quality, once a forehead has been sucessfully isolated.
        """
        # state = self.processor.find_faces.toggle()
        state = self.processor.find_faces_toggle()
        print("face detection lock =", not state)

    def toggle_display_plot(self):
        """
        Toggles the data display.
        """
        if self.bpm_plot:
            print("bpm plot disabled")
            self.bpm_plot = False
            destroyWindow(self.plot_title)
        else:
            print("bpm plot enabled")
            if self.processor.find_faces:
                self.toggle_search()
            self.bpm_plot = True
            self.make_bpm_plot()
            moveWindow(self.plot_title, self.w, 0)

    def make_bpm_plot(self):
        """
        Creates and/or updates the data display
        """
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

    def key_handler(self):

        self.pressed = waitKey(10) & 255

        for key in self.key_controls.keys():
            if chr(self.pressed) == key:
                self.key_controls[key]()

    def close(self):
        self.camera.release()
        cv2.destroyAllWindows()

    def run(self):
        while not self.stop_event.is_set():
            self.main_loop()
        self.close()

    def stop(self):
        self.stop_event.set()

    def main_loop(self):
        """
        Single iteration of the application's main loop.
        """
        # Get current image frame from the camera
        _, frame = self.camera.read()
        self.h = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.w = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)

        # display unaltered frame
        # imshow("Original",frame)

        # set current image frame to the processor's input
        self.processor.frame_in = frame
        # process the image frame to perform all needed analysis
        self.processor.run(self.selected_cam)
        # collect the output frame for display
        output_frame = self.processor.frame_out

        # show the processed/annotated output frame
        imshow("Processed", output_frame)

        # create and/or update the raw data display if needed
        if self.bpm_plot:
            self.make_bpm_plot()

        self.key_handler()

        self.loop_count += 1
        if self.loop_count is 30:
            self.send_bpm()
            self.loop_count = 0

    def send_bpm(self):
        msg = osc_message_builder.OscMessageBuilder(address=OSC_ADDRESS)
        msg.add_arg(self.processor.bpm)
        msg = msg.build()
        self.client.send(msg)


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
