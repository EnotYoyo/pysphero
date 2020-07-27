import abc
from concurrent.futures import Future
from enum import Enum
from typing import Callable

from pysphero.packet import Packet
from pysphero.packet import Flag


class DeviceId(Enum):
    api_processor = 0x10
    system_info = 0x11
    system_modes = 0x12
    power = 0x13
    driving = 0x16
    animatronics = 0x17
    sensors = 0x18
    peer_connection = 0x19
    user_io = 0x1a
    storage_command = 0x1b
    secondary_mcu_firmware_update_command = 0x1d
    wifi_command = 0x1e
    factory_test = 0x1f
    macro_system = 0x20
    proto = 0xfe


class DeviceApiABC(abc.ABC):
    device_id: Enum = NotImplemented

    def __init__(self, ble_adapter):
        self.ble_adapter = ble_adapter

    def request(self, command_id: Enum, timeout: float = 10, raise_api_error: bool = True, **kwargs) -> Packet:
        return self.ble_adapter.write(
            self.packet(command_id=command_id.value, **kwargs),
            raise_api_error=raise_api_error,
            timeout=timeout,
        )

    def notify(
            self,
            command_id: Enum,
            callback: Callable,
            timeout: float = 10,
            **kwargs
    ) -> Future:
        return self.ble_adapter.start_notify(
            self.packet(command_id=command_id.value, **kwargs),
            callback=callback,
            timeout=timeout,
        )

    def cancel_notify(self):
        self.ble_adapter.stop_notify()

    def packet(self, **kwargs):
        packet = Packet(
            device_id=self.device_id.value,
            **kwargs
        )
        return packet
