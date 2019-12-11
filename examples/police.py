from time import sleep

from pysphero.core import Sphero
from pysphero.device_api.user_io import Color


def main():
    mac_address = "aa:bb:cc:dd:ee:ff"
    with Sphero(mac_address=mac_address) as sphero:
        sphero.power.wake()
        for i in range(20):
            sphero.user_io.set_all_leds_8_bit_mask(back_color=Color(blue=0xff))
            sleep(0.25)
            sphero.user_io.set_all_leds_8_bit_mask(front_color=Color(red=0xff))
            sleep(0.25)

        sphero.power.enter_soft_sleep()


if __name__ == "__main__":
    main()
