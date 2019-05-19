from time import sleep

from pysphero.core import Sphero


def main():
    mac_address = 'aa:bb:cc:dd:ee:ff'
    sphero = Sphero(mac_address=mac_address)
    sphero.power.wake()
    for i in range(20):
        sphero.user_io.set_all_leds_8_bit_mask(back_blue=255)
        sleep(0.25)
        sphero.user_io.set_all_leds_8_bit_mask(front_red=255)
        sleep(0.25)

    sleep(5)
    sphero.power.enter_soft_sleep()


if __name__ == '__main__':
    main()
