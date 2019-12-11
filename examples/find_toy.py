from time import sleep

from pysphero.constants import Toy
from pysphero.utils import toy_scanner


def main():
    with toy_scanner(toy_type=Toy.sphero_bolt) as sphero:
        print(f"Found {sphero.mac_address}")
        sphero.power.wake()
        sleep(2)
        sphero.power.enter_soft_sleep()


if __name__ == "__main__":
    main()
