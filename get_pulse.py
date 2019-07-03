from pulsedetector.processors_noopenmdao import findFaceGetPulse
import cv2
import threading
from socket import socket, AF_INET, SOCK_DGRAM

IP = "127.0.0.1"
PORT = 5000


class getPulseApp(threading.Thread):
    def __init__(self):
        super(getPulseApp, self).__init__()
        self.stop_event = threading.Event()

        self.cam_num = 0
        self.camera = cv2.VideoCapture(self.cam_num)
        self.w, self.h = 0, 0

        self.processor = findFaceGetPulse(bpm_limits=[50, 160],
                                          data_spike_limit=2500.,
                                          face_detector_smoothness=10.)

        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.loop_count = 0

    @property
    def bpm(self):
        return self.processor.bpm

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
        _, frame = self.camera.read()

        self.processor.frame_in = frame
        self.processor.run(self.cam_num)
        output_frame = self.processor.frame_out

        # show the processed/annotated output frame
        cv2.imshow("Processed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print "q pressed"

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
