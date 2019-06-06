import random
from time import sleep

from pysphero.core import Sphero
from pysphero.driving import Direction


def main():
    mac_address = "aa:bb:cc:dd:ee:ff"
    with Sphero(mac_address=mac_address) as sphero:
        sphero.power.wake()

        for _ in range(5):
            sleep(2)
            speed = random.randint(50, 100)
            heading = random.randint(0, 360)
            print(f"Send drive with speed {speed} and heading {heading}")

            sphero.driving.drive_with_heading(speed, heading, Direction.forward)

        sphero.power.enter_soft_sleep()


if __name__ == "__main__":
    main()
