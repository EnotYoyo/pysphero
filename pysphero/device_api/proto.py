from enum import Enum
from typing import NamedTuple

from .device_api import DeviceApiABC, DeviceId



class ProtoCommand(Enum):
    set_mac_table = 0x00
    get_mac_table = 0x01
    enable_table_rssi = 0x02
    table_of_rssi = 0x03
    