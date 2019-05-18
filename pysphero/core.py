import contextlib
import logging
import struct
from collections import namedtuple
from typing import List

from bluepy.btle import ADDR_TYPE_RANDOM, Characteristic, DefaultDelegate, Descriptor, Peripheral

from pysphero.api_processor import ApiProcessor
from pysphero.constants import Api2Error, GenericCharacteristic, SpheroCharacteristic
from pysphero.driving import Driving
from pysphero.exceptions import PySpheroApiError, PySpheroRuntimeError, PySpheroTimeoutError
from pysphero.helpers import cached_property
from pysphero.packet import Packet
from pysphero.power import Power
from pysphero.system_info import SystemInfo

logger = logging.getLogger(__name__)

PeripheralPreferredConnectionParameters = namedtuple(
    "PeripheralPreferredConnectionParameters", (
        "min_con_interval",
        "max_con_interval",
        "slave_latency",
        "connection_supervision_timeout_multiplier",
    )
)


class SpheroDelegate(DefaultDelegate):
    """
    Delegate class for bluepy
    Getting bytes from peripheral and build packets
    """

    def __init__(self):
        super().__init__()
        self.data = []
        self.packets = {}
        self._is_escaping = False

    @property
    def is_escaping(self) -> bool:
        return self._is_escaping

    @is_escaping.setter
    def is_escaping(self, value: bool):
        if value and self._is_escaping:
            raise PySpheroRuntimeError("Bad escaping byte position")
        self._is_escaping = value

    def build_packet(self):
        """
        Create and save packet from raw bytes
        """
        logger.debug(f"Starting of packet build")

        packet = Packet.from_response(self.data)
        self.packets[packet.id] = packet
        self.data = []

    def handleNotification(self, handle: int, data: List[int]):
        """
        handleNotification getting raw data from peripheral and save it.
        This function may be called several times. Therefore, the state is stored inside the class.

        :param handle:
        :param data: raw data
        :return:
        """
        for b in data:
            logger.debug(f"Received {b:#04x}")
            # packet always starting from start byte
            if len(self.data) == 0 and b != Packet.start:
                raise PySpheroRuntimeError(f"Invalid first byte {b:#04x}")

            # escaping byte allowing escaping start/end/escaping bytes
            if b == Packet.escape:
                # next byte is escaping
                self.is_escaping = True
                continue

            if self.is_escaping:
                self.is_escaping = False
                if b not in Packet.escaped_bytes:
                    raise PySpheroRuntimeError(f"Bad escaping byte {b:#04x}")
                b |= Packet.escape_mask

            self.data.append(b)

            # packet always ending with end byte
            if b == Packet.end:
                if len(self.data) < 6:
                    raise PySpheroRuntimeError(f"Very small packet {[hex(x) for x in self.data]}")
                self.build_packet()


class SpheroCore:
    """
    Core class for communication with peripheral device
    In the future, another bluetooth library can be replaced.
    """

    def __init__(self, mac_address: str):
        logger.debug("Init Sphero Core")
        self.mac_address = mac_address
        self.delegate = SpheroDelegate()
        self.peripheral = Peripheral(self.mac_address, ADDR_TYPE_RANDOM)
        self.peripheral.setDelegate(self.delegate)

        self.ch_api_v2 = self.get_characteristic(uuid=SpheroCharacteristic.api_v2.value)
        # Initial api descriptor
        # Need for getting response from sphero
        desc = self.get_descriptor(self.ch_api_v2, GenericCharacteristic.client_characteristic_configuration.value)
        desc.write(b"\x01\x00", withResponse=True)

        self._sequence = 0
        logger.debug("Sphero Core: successful initialization")

    def __del__(self):
        # ignoring any exception
        # because it does not matter
        with contextlib.suppress(Exception):
            self.peripheral.disconnect()

    @property
    def sequence(self) -> int:
        """
        Autoincrement sequence number of packet
        """
        self._sequence = (self._sequence + 1) % 256
        return self._sequence

    def get_characteristic(self, uuid: int or str) -> Characteristic:
        return self.peripheral.getCharacteristics(uuid=uuid)[0]

    def get_descriptor(self, characteristic: Characteristic, uuid: int or str) -> Descriptor:
        return characteristic.getDescriptors(forUUID=uuid)[0]

    def request(self, packet: Packet, with_api_error: bool = True, timeout: int = 10) -> Packet:
        """
        Method allow send request packet and get response packet

        :param packet: request packet
        :param with_api_error: error code check
        :param timeout: timeout for waiting response from device
        :return Packet: response packet
        """
        logger.debug(f"Send {packet}")
        packet.sequence = self.sequence
        self.ch_api_v2.write(packet.build(), withResponse=True)

        sleep = 0.1  # must be small for correct calculate timeout
        while timeout > 0:
            response = self.delegate.packets.pop(packet.id, None)
            if response:
                if with_api_error and response.api_error is not Api2Error.success:
                    raise PySpheroApiError(response.api_error)
                return response

            timeout -= sleep
            self.peripheral.waitForNotifications(sleep)

        raise PySpheroTimeoutError(f"Timeout error for response of {packet}")


class Sphero:
    """
    High-level API for communicate with sphero toy
    """

    def __init__(self, mac_address: str):
        self.sphero_core = SpheroCore(mac_address)

    @property
    def name(self) -> str:
        device_name = self.sphero_core.get_characteristic(uuid=GenericCharacteristic.device_name.value)
        name: bytes = device_name.read()
        return name.decode("utf-8")

    @property
    def peripheral_preferred_connection_parameters(self) -> PeripheralPreferredConnectionParameters:
        ppcp = self.sphero_core.get_characteristic(
            uuid=GenericCharacteristic.peripheral_preferred_connection_parameters.value)
        data: bytes = ppcp.read()
        return PeripheralPreferredConnectionParameters(*struct.unpack("HHHH", data))

    @cached_property
    def system_info(self) -> SystemInfo:
        return SystemInfo(sphero_core=self.sphero_core)

    @cached_property
    def power(self) -> Power:
        return Power(sphero_core=self.sphero_core)

    @cached_property
    def driving(self) -> Driving:
        return Driving(sphero_core=self.sphero_core)

    @cached_property
    def api_processor(self) -> ApiProcessor:
        return ApiProcessor(sphero_core=self.sphero_core)
