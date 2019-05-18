from time import sleep

from pysphero.core import Sphero


def main():
    mac_address = 'aa:bb:cc:dd:ee:ff'
    sphero = Sphero(mac_address=mac_address)
    sphero.power.wake()
    sleep(2)
    sphero.power.enter_soft_sleep()


if __name__ == '__main__':
    main()
