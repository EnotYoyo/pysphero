import abc
from concurrent.futures import Future
from enum import Enum
from typing import Callable

from pysphero.packet import Packet


class DeviceId(Enum):
    api_processor = 0x10
    system_info = 0x11
    system_modes = 0x12
    power = 0x13
    driving = 0x16
    animatronics = 0x17
    sensors = 0x18
    user_io = 0x1a


class DeviceApiABC(abc.ABC):
    device_id: Enum = NotImplemented

    def __init__(self, sphero_core):
        self.sphero_core = sphero_core

    def request(self, command_id: Enum, with_api_error: bool = True, timeout: float = 10, **kwargs) -> Packet:
        return self.sphero_core.request(
            self.packet(command_id=command_id.value, **kwargs),
            with_api_error=with_api_error,
            timeout=timeout,
        )

    def notify(
            self,
            command_id: Enum,
            callback: Callable,
            sleep_time: float = 0.1,
            timeout: float = 10,
            **kwargs
    ) -> Future:
        return self.sphero_core.notify(
            self.packet(command_id=command_id.value, **kwargs),
            callback=callback,
            sleep_time=sleep_time,
            timeout=timeout,
        )

    def cancel_notify(self, command_id):
        packet = self.packet(command_id=command_id.value)
        self.sphero_core.cancel_notify(packet)

    def packet(self, **kwargs):
        packet = Packet(
            device_id=self.device_id.value,
            **kwargs
        )
        return packet
