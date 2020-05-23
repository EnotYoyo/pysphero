import logging
from typing import NamedTuple, ClassVar

from pysphero.bluetooth import BleAdapter
from pysphero.bluetooth.ble_adapter import AbstractBleAdapter
from pysphero.constants import Toy
from pysphero.device_api import Animatronics, Sensor, UserIO, ApiProcessor, Power, SystemInfo
from pysphero.driving import Driving
from pysphero.exceptions import PySpheroException
from pysphero.helpers import cached_property

logger = logging.getLogger(__name__)


class PeripheralPreferredConnectionParameters(NamedTuple):
    min_con_interval: int
    max_con_interval: int
    slave_latency: int
    connection_supervision_timeout_multiplier: int


class Sphero:
    """
    High-level API for communicate with sphero toy
    """

    def __init__(
            self,
            mac_address: str,
            toy_type: Toy = Toy.unknown,
            ble_adapter_cls: ClassVar[AbstractBleAdapter] = BleAdapter
    ):
        self.mac_address = mac_address
        self.type = toy_type
        self._ble_adapter_cls = ble_adapter_cls
        self._ble_adapter = None

    @property
    def ble_adapter(self):
        if self._ble_adapter is None:
            raise PySpheroException("Use Sphero as context manager")
        return self._ble_adapter

    @ble_adapter.setter
    def ble_adapter(self, value):
        self._ble_adapter = value

    def __enter__(self):
        self._ble_adapter = self._ble_adapter_cls(self.mac_address)
        # if self.type is Toy.unknown:
        #     self.type = TOY_BY_PREFIX.get(self.name[:3], Toy.unknown)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ble_adapter.close()

    @cached_property
    def system_info(self) -> SystemInfo:
        return SystemInfo(ble_adapter=self.ble_adapter)

    @cached_property
    def power(self) -> Power:
        return Power(ble_adapter=self.ble_adapter)

    @cached_property
    def driving(self) -> Driving:
        return Driving(ble_adapter=self.ble_adapter)

    @cached_property
    def api_processor(self) -> ApiProcessor:
        return ApiProcessor(ble_adapter=self.ble_adapter)

    @cached_property
    def user_io(self) -> UserIO:
        return UserIO(ble_adapter=self.ble_adapter)

    @cached_property
    def sensor(self) -> Sensor:
        return Sensor(ble_adapter=self.ble_adapter)

    @cached_property
    def animatronics(self) -> Animatronics:
        return Animatronics(ble_adapter=self.ble_adapter)
