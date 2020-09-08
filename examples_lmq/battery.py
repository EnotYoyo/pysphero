from time import sleep

from pysphero.core import Sphero


def main():

    mac_address = "aa:bb:cc:dd:ee:ff"
    with Sphero(mac_address=mac_address) as sphero:
        sphero.power.wake()
        sleep(10)
        
        #get battery info
        battery_state = sphero.power.get_battery_state_LMQ()
        print("Battery is: ", battery_state.name)
        
        
        #get battery percentage
        battery_percentage = sphero.power.get_battery_percentage()
        print("Battery level: ", battery_percentage, " %")

        sphero.power.enter_soft_sleep()

if __name__ == "__main__":
    main()
