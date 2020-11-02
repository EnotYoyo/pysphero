import logging
from typing import Optional

import pygatt

from pysphero.bluetooth.ble_adapter import AbstractBleAdapter
from pysphero.bluetooth.packet_collector import PacketCollector
from pysphero.constants import SpheroCharacteristic
from pysphero.exceptions import PySpheroRuntimeError
from pysphero.packet import Packet

logger = logging.getLogger(__name__)

class PygattDelegate():
    """
    Delegate class for Pygatt
    Getting bytes from peripheral and build packets
    """

    def __init__(self, packet_collector: PacketCollector):
        super().__init__()
        self.packet_collector = packet_collector

    def handleNotification(self, handle, data):
        """
        handleNotification getting raw data from peripheral and save it.
        This function may be called several times. Therefore, the state is stored inside the class.

        :param handle:
        :param data: raw data
        :return:
        """
        self.packet_collector.append_raw_data(data)

class PygattAdapter(AbstractBleAdapter):
    def __init__(self, mac_address):
        logger.debug("Init pygatt Adapter")
        super().__init__(mac_address)

        self.adapter = pygatt.BGAPIBackend()
        self.adapter.start()
        self.delegate = PygattDelegate(self.packet_collector)

        self._device = self.adapter.connect(self.mac_address, address_type=pygatt.BLEAddressType.random)

        ch_force_band = self._find_characteristic(SpheroCharacteristic.force_band.value)
        self._device.char_write(ch_force_band, b"usetheforce...band", wait_for_response=False)

        self.ch_api_v2 = self._find_characteristic(SpheroCharacteristic.api_v2.value)

        self._device.subscribe(self.ch_api_v2, callback = self.delegate.handleNotification)
        logger.debug("Pygatt Adapter: successful initialization")

    def _find_characteristic(self, characteristic: str):
        found_characteristic = None
        for uuid in self._device.discover_characteristics().keys():
            if str(uuid) == characteristic:
                found_characteristic = uuid

        if not found_characteristic:
            raise PySpheroRuntimeError(f"Characteristic {characteristic} not found")

        return found_characteristic


    def close(self):
        self._device.disconnect()
        self.adapter.stop()
        super().close()

    def write(self, packet: Packet, *, timeout: float = 10, raise_api_error: bool = True) -> Optional[Packet]:
        """
         Method allow send request packet and get response packet

         :param packet: request packet
         :param timeout: timeout waiting for a response from sphero
         :param raise_api_error: raise exception when receive api error
         :return Packet: response packet
        """
        logger.debug(f"Send {packet}")
        self._device.char_write(self.ch_api_v2, packet.build(), wait_for_response=True)
        return self.packet_collector.get_response(packet, raise_api_error, timeout)
