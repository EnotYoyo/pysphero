import contextlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor, Future
from threading import Event
from typing import List, Callable

from bluepy.btle import DefaultDelegate, Peripheral, ADDR_TYPE_RANDOM, Characteristic, Descriptor

from pysphero.bluetooth.ble_adapter import AbstractBleAdapter
from pysphero.constants import SpheroCharacteristic, GenericCharacteristic, Api2Error
from pysphero.exceptions import PySpheroRuntimeError, PySpheroTimeoutError, PySpheroApiError
from pysphero.packet import Packet

logger = logging.getLogger(__name__)


class BluepyDelegate(DefaultDelegate):
    """
    Delegate class for bluepy
    Getting bytes from peripheral and build packets
    """

    def __init__(self):
        super().__init__()
        self.data = []
        self.packets = {}

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
            self.data.append(b)

            # packet always ending with end byte
            if b == Packet.end:
                if len(self.data) < 6:
                    raise PySpheroRuntimeError(f"Very small packet {[hex(x) for x in self.data]}")
                self.build_packet()


class BluepyAdapter(AbstractBleAdapter):
    STOP_NOTIFY = object()

    def __init__(self, mac_address, check_response_delta: float = 0.1):
        logger.debug("Init Bluepy Adapter")
        super().__init__(mac_address)
        self.check_response_delta = check_response_delta or 0.01  # protect of 0 sleep_time
        self.delegate = BluepyDelegate()
        self.peripheral = Peripheral(self.mac_address, ADDR_TYPE_RANDOM)
        self.peripheral.setDelegate(self.delegate)

        self.ch_api_v2 = self._get_characteristic(uuid=SpheroCharacteristic.api_v2.value)
        # Initial api descriptor
        # Need for getting response from sphero
        desc = self._get_descriptor(self.ch_api_v2, GenericCharacteristic.client_characteristic_configuration.value)
        desc.write(b"\x01\x00", withResponse=True)

        self._executor = ThreadPoolExecutor(max_workers=2)
        self._running = Event()  # disable receiver thread
        self._running.set()
        self._notify_futures = {}  # features of notify
        self._executor.submit(self._receiver)
        logger.debug("Bluepy Adapter: successful initialization")

    def close(self):
        self._running.clear()
        self._executor.shutdown(wait=False)
        # ignoring any exception
        # because it does not matter
        with contextlib.suppress(Exception):
            self.peripheral.disconnect()

    def start_notify(self, packet: Packet, callback: Callable, timeout: float = 10):
        packet_id = packet.id
        if packet_id in self._notify_futures:
            raise PySpheroRuntimeError("Notify thread already exists")

        def worker():
            logger.debug(f"[NOTIFY_WORKER {packet}] Start")

            while self._running.is_set():
                response = self._get_response(packet, timeout=timeout)
                logger.debug(f"[NOTIFY_WORKER {packet}] Received {response}")
                if callback(response) is BluepyAdapter.STOP_NOTIFY:
                    logger.debug(f"[NOTIFY_WORKER {packet}] Received STOP_NOTIFY")
                    self._notify_futures.pop(packet_id, None)
                    break

        future = self._executor.submit(worker)
        self._notify_futures[packet_id] = future
        return future

    def stop_notify(self, packet: Packet):
        future: Future = self._notify_futures.pop(packet.id, None)
        if future is None:
            raise PySpheroRuntimeError("Future not found")

        logger.debug(f"[NOTIFY_WORKER {packet}] Cancel")
        future.cancel()

    def write(self, packet: Packet, *, timeout: float = 10, raise_api_error: bool = True) -> Packet:
        logger.debug(f"Send {packet}")
        self.ch_api_v2.write(packet.build(), withResponse=True)

        response = self._get_response(packet, timeout=timeout)
        if raise_api_error and response.api_error is not Api2Error.success:
            raise PySpheroApiError(response.api_error)
        return response

    def _get_response(self, packet: Packet, timeout: float = 10):
        while True:
            response = self.delegate.packets.pop(packet.id, None)
            if response:
                return response

            timeout -= self.check_response_delta
            if timeout <= 0:
                raise PySpheroTimeoutError(f"Timeout error for response of {packet}")

            time.sleep(self.check_response_delta)

    def _receiver(self):
        logger.debug("Start receiver")

        sleep = 0.05
        while self._running.is_set():
            self.peripheral.waitForNotifications(sleep)

        logger.debug("Stop receiver")

    def _get_characteristic(self, uuid: int or str) -> Characteristic:
        return self.peripheral.getCharacteristics(uuid=uuid)[0]

    def _get_descriptor(self, characteristic: Characteristic, uuid: int or str) -> Descriptor:
        return characteristic.getDescriptors(forUUID=uuid)[0]
