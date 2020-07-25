import logging

from time import sleep

from pysphero.constants import Toy
from pysphero.utils import toy_scanner


def main():
    logging.basicConfig(filename='pysphero.log', level=logging.DEBUG)
    logging.info('Started')
    with toy_scanner(toy_type=Toy.lmq) as sphero:
        print(f"Found {sphero.mac_address}")
        sphero.power.wake()
        sleep(2)
        sphero.power.enter_soft_sleep()

    logging.info('Finished')
    

if __name__ == "__main__":
    main()
