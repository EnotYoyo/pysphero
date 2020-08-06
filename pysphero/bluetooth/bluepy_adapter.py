import contextlib
import logging
from typing import List, Optional

from bluepy.btle import DefaultDelegate, Peripheral, ADDR_TYPE_RANDOM, Characteristic, Descriptor

from pysphero.bluetooth.ble_adapter import AbstractBleAdapter
from pysphero.bluetooth.packet_collector import PacketCollector
from pysphero.constants import SpheroCharacteristic, GenericCharacteristic
from pysphero.packet import Packet

logger = logging.getLogger(__name__)


class BluepyDelegate(DefaultDelegate):
    """
    Delegate class for bluepy
    Getting bytes from peripheral and build packets
    """

    def __init__(self, packet_collector: PacketCollector):
        super().__init__()
        self.packet_collector = packet_collector

    def handleNotification(self, handle: int, data: List[int]):
        """
        handleNotification getting raw data from peripheral and save it.
        This function may be called several times. Therefore, the state is stored inside the class.

        :param handle:
        :param data: raw data
        :return:
        """
        self.packet_collector.append_raw_data(data)


class BluepyAdapter(AbstractBleAdapter):
    STOP_NOTIFY = object()

    def __init__(self, mac_address):
        logger.debug("Init Bluepy Adapter")
        super().__init__(mac_address)
        self.delegate = BluepyDelegate(self.packet_collector)
        self.peripheral = Peripheral(self.mac_address, ADDR_TYPE_RANDOM)
        self.peripheral.setDelegate(self.delegate)

        self.ch_api_v2 = self._get_characteristic(uuid=SpheroCharacteristic.api_v2.value)
        # Initial api descriptor
        # Need for getting response from sphero
        desc = self._get_descriptor(self.ch_api_v2, GenericCharacteristic.client_characteristic_configuration.value)
        desc.write(b"\x01\x00", withResponse=True)

        self._executor.submit(self._receiver)
        logger.debug("Bluepy Adapter: successful initialization")

    def close(self):
        super().close()
        # ignoring any exception
        # because it does not matter
        with contextlib.suppress(Exception):
            self.peripheral.disconnect()

    def write(self, packet: Packet, *, timeout: float = 10, raise_api_error: bool = True) -> Optional[Packet]:
        logger.debug(f"Send {packet}")
        self.ch_api_v2.write(packet.build(), withResponse=True)
        return self.packet_collector.get_response(packet, raise_api_error, timeout=timeout)

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
