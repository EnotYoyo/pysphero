from enum import Enum


class WifiCommand(Enum):
    power_on_wifi = 0x00
    power_on_wifi_complete = 0x01
    get_wifi_mac = 0x02
    start_update = 0x03
    erase_block_range = 0x04
    erase_block_range_complete = 0x05
    send_data = 0x06
    send_data_complete = 0x07
    update_done = 0x08
    update_done_complete = 0x09
