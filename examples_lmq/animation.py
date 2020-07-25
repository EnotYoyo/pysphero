from time import sleep

from pysphero.core import Sphero
from pysphero.device_api.animatronics import LMQAnimation


def main():
    mac_address = "aa:bb:cc:dd:ee:ff"
    with Sphero(mac_address=mac_address) as sphero:
        sphero.power.wake()
        sleep(20)

        sphero.animatronics.play_animation(50)
        sleep(5)

        for data in LMQAnimation:
            sphero.animatronics.play_animation_and_wait(data.value, target_id = None, timeout = 10)

        sphero.power.enter_soft_sleep()


if __name__ == "__main__":
    main()
