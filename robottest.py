from dobot import Dobot
from glob import glob
import time

available_ports = glob('/dev/ttyUSB*')
print available_ports
if len(available_ports) == 0:
    print 'no port found for Dobot Magician'
    exit(1)
rob = Dobot(port=available_ports[0])
time.sleep(1.0)

x = 150.0
y = 150.0
z = -50.0
j1 = 2.0
j2 = 2.0
j3 = 2.0
j4 = 2.0
a = 5.0
while True:
    # rob._get_pose()
    # rob._set_ptp_joint_params(j1, j2, j3, j4, a, a, a, a)
    # j2 += 0.1
    time.sleep(1.0)
    # rob.go(x,y,z)
    # time.sleep(1.0)
    # z += 0.1
    msg = rob.get_pose()
