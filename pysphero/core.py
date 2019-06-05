import contextlib
import logging
import struct
import time
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, NamedTuple, Callable

from bluepy.btle import ADDR_TYPE_RANDOM, Characteristic, DefaultDelegate, Descriptor, Peripheral

from pysphero.api_processor import ApiProcessor
from pysphero.constants import Api2Error, GenericCharacteristic, SpheroCharacteristic
from pysphero.driving import Driving
from pysphero.exceptions import PySpheroApiError, PySpheroRuntimeError, PySpheroTimeoutError, PySpheroException
from pysphero.helpers import cached_property
from pysphero.packet import Packet
from pysphero.power import Power
from pysphero.sensor import Sensor
from pysphero.system_info import SystemInfo
from pysphero.user_io import UserIO

logger = logging.getLogger(__name__)


class PeripheralPreferredConnectionParameters(NamedTuple):
    min_con_interval: int
    max_con_interval: int
    slave_latency: int
    connection_supervision_timeout_multiplier: int


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
                if b not in Packet.escaped_bytes:
                    raise PySpheroRuntimeError(f"Bad escaping byte {b:#04x}")

                self.data.append(b | Packet.escape_mask)
                self.is_escaping = False
                continue

            self.data.append(b)

            # packet always ending with end byte
            if b == Packet.end:
                if len(self.data) < 6:
                    raise PySpheroRuntimeError(f"Very small packet {[hex(x) for x in self.data]}")
                self.build_packet()


class SpheroCore:
    STOP_NOTIFY = object()
    """
    Core class for communication with peripheral device
    In the future, another bluetooth library can be replaced.
    """

    def __init__(self, mac_address: str, max_workers: int = 10):
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

        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._running = True  # disable receiver thread
        self._notify_futures = {}  # features of notify
        self._executor.submit(self._receiver)
        logger.debug("Sphero Core: successful initialization")

    def close(self):
        self._running = False
        self._executor.shutdown(wait=False)
        # ignoring any exception
        # because it does not matter
        with contextlib.suppress(Exception):
            self.peripheral.disconnect()

    def _receiver(self):
        logger.debug("Start receiver")

        sleep = 0.05
        while self._running:
            self.peripheral.waitForNotifications(sleep)

        logger.debug("Stop receiver")

    def _get_response(self, packet: Packet, sleep_time: float = 0.1, timeout: float = 10):
        while self._running:
            response = self.delegate.packets.pop(packet.id, None)
            if response:
                return response

            timeout -= sleep_time or 0.01  # protect of 0 sleep_time
            if timeout <= 0:
                raise PySpheroTimeoutError(f"Timeout error for response of {packet}")

            time.sleep(sleep_time)

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

    def notify(self, packet: Packet, callback: Callable, sleep_time: float = 0.1, timeout: float = 10):
        packet_id = packet.id
        if packet_id in self._notify_futures:
            raise PySpheroRuntimeError("Notify thread already exists")

        def worker():
            logger.debug(f"[NOTIFY_WORKER {packet}] Start")

            while self._running:
                response = self._get_response(packet, sleep_time=sleep_time, timeout=timeout)
                logger.debug(f"[NOTIFY_WORKER {packet}] Received {response}")
                if callback(response) is SpheroCore.STOP_NOTIFY:
                    logger.debug(f"[NOTIFY_WORKER {packet}] Received STOP_NOTIFY")
                    self._notify_futures.pop(packet_id, None)
                    break

        future = self._executor.submit(worker)
        self._notify_futures[packet_id] = future
        return future

    def cancel_notify(self, packet: Packet):
        future: Future = self._notify_futures.pop(packet.id, None)
        if future is None:
            raise PySpheroRuntimeError("Future not found")

        logger.debug(f"[NOTIFY_WORKER {packet}] Cancel")
        future.cancel()

    def request(self, packet: Packet, with_api_error: bool = True, timeout: float = 10) -> Packet:
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

        response = self._get_response(packet, timeout=timeout)
        if with_api_error and response.api_error is not Api2Error.success:
            raise PySpheroApiError(response.api_error)
        return response


class Sphero:
    """
    High-level API for communicate with sphero toy
    """

    def __init__(self, mac_address: str):
        self.mac_address = mac_address
        self._sphero_core = None

    @property
    def sphero_core(self):
        if self._sphero_core is None:
            raise PySpheroException("Use Sphero as context manager")
        return self._sphero_core

    @sphero_core.setter
    def sphero_core(self, value):
        self._sphero_core = value

    def __enter__(self):
        self.sphero_core = SpheroCore(self.mac_address)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sphero_core.close()

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

    @cached_property
    def user_io(self) -> UserIO:
        return UserIO(sphero_core=self.sphero_core)

    @cached_property
    def sensor(self) -> Sensor:
        return Sensor(sphero_core=self.sphero_core)
