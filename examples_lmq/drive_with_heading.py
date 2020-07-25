import random
from time import sleep

from pysphero.core import Sphero
from pysphero.driving import Direction


def main():
    mac_address = "aa:bb:cc:dd:ee:ff"
    with Sphero(mac_address=mac_address) as sphero:
        sphero.power.wake()
        sleep(8)
        sphero.driving.ackermann_reset(0x0,0x0)
        sphero.driving.ackermann_drive(0x0, 0x0)

        #right
        for x in range(0x3e800000,0x3f800000, 0x50000):
            sphero.driving.ackermann_drive(x, 0x0)
            sleep(0.1)
        sleep(2)
        for x in range(0x3f800000,0x3e800000, -0x50000):
            sphero.driving.ackermann_drive(x, 0x0)
            sleep(0.1)

        #left
        for x in range(0xbe800000,0xbf800000, 0x50000):
            sphero.driving.ackermann_drive(x, 0x0)
            sleep(0.1)
        sleep(2)
        for x in range(0xbf800000,0xbe800000, -0x50000):
            sphero.driving.ackermann_drive(x, 0x0)
            sleep(0.1)

        #forward
        for x in range(0x3e000000,0x3f800000, 0x50000):
            sphero.driving.ackermann_drive(0x0, x)
            sleep(0.1)
        for x in range(0x3f800000,0x3e000000, -0x50000):
            sphero.driving.ackermann_drive(0x0, x)
            sleep(0.1)

        #reverse
        for x in range(0xBe000000,0xBf800000, 0x50000):
            sphero.driving.ackermann_drive(0x0, x)
            sleep(0.1)
        for x in range(0xBf800000,0xBe000000, -0x50000):
            sphero.driving.ackermann_drive(0x0, x)
            sleep(0.1)

        sphero.power.enter_soft_sleep()


if __name__ == "__main__":
    main()
