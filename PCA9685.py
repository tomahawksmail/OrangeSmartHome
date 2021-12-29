from __future__ import division
import time
from library import PCA_9685_library

# Initialise the PCA9685 using the default address (0x40).
pwm = PCA_9685_library.PCA9685()
# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(1000)
min = 0  # Min pulse length out of 4096
max = 4096  # Max pulse length out of 4096

if __name__ == '__main__':
    try:
        while True:
            i = int(input())
            pwm.set_pwm(0, 0, i)
    except KeyboardInterrupt:
        pwm.set_pwm(0, 0, 0)
        print("Keyboard interrupt")

    # for i in range(0, 4096):
    #     pwm.set_pwm(0, 0, i)
    # time.sleep(1)
    # pwm.set_pwm(0, 0, servo_max)
    # time.sleep(1)
