import logging

from time import sleep

from pysphero.core import Sphero


def main():
    mac_address = "aa:bb:cc:dd:ee:ff"
    with Sphero(mac_address=mac_address) as sphero:
        sphero.power.wake()
        sleep(20)

        sphero.power.enter_soft_sleep()
        
        #deep sleep
        sphero.power.enter_deep_sleep()



if __name__ == "__main__":
    main()
