import logging
from typing import Optional

import gatt

from pysphero.bluetooth.ble_adapter import AbstractBleAdapter
from pysphero.bluetooth.packet_collector import PacketCollector
from pysphero.constants import SpheroCharacteristic
from pysphero.exceptions import PySpheroRuntimeError
from pysphero.packet import Packet

logger = logging.getLogger(__name__)


class Device(gatt.Device):

    def __init__(self, packet_collector: PacketCollector, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.packet_collector = packet_collector

    def characteristic_value_updated(self, characteristic, value):
        """
        Callback from gatt when value was updated, call the create packet function for received data.
        """
        self.packet_collector.append_raw_data(value)


class GattAdapter(AbstractBleAdapter):
    def __init__(self, mac_address):
        logger.debug("Init Gatt Adapter")
        super().__init__(mac_address)

        self.manager = gatt.DeviceManager("hci0")

        self._device = Device(
            self.packet_collector, mac_address=self.mac_address, manager=self.manager)
        self._device.connect()

        ch_force_band = self._find_characteristic(SpheroCharacteristic.force_band.value)
        ch_force_band.write_value(b"usetheforce...band")

        self.ch_api_v2 = self._find_characteristic(SpheroCharacteristic.api_v2.value)

        self.ch_api_v2.enable_notifications()
        self._executor.submit(self.manager.run)

    def _find_characteristic(self, characteristic: str):
        found_characteristic = None
        self._device.services_resolved()
        for service in self._device.services:
            for ch in service.characteristics:
                if str(ch.uuid) == characteristic:
                    found_characteristic = ch

        if not found_characteristic:
            raise PySpheroRuntimeError(f"Characteristic {characteristic} not found")

        return found_characteristic

    def close(self):
        self.manager.stop()
        self._device.disconnect()
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
        self.ch_api_v2.write_value(packet.build())
        return self.packet_collector.get_response(packet, raise_api_error, timeout)
