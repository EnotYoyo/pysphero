from enum import Enum
from typing import NamedTuple

from pysphero.device_api import DeviceApiABC, DeviceId


class Version(NamedTuple):
    major: int
    minor: int
    revision: int


class SystemInfoCommand(Enum):
    get_main_application_version = 0x00
    get_bootloader_version = 0x01
    get_main_application_build_info = 0x02
    get_board_revision = 0x03
    config_block_write = 0x04
    config_block_write_complete = 0x05
    get_mac_address = 0x06
    get_user_configblock = 0x07
    set_user_configblock = 0x08
    set_user_configblock_complete = 0x09
    disable_factory_mode = 0x0a
    get_log_status = 0x0b
    get_log_chunk = 0x0c
    clear_log = 0x0d
    get_nordic_temperature = 0x0e
    startup_async = 0x0f
    get_model_number = 0x12
    get_stats_id = 0x13
    set_device_mode = 0x14
    get_device_mode = 0x15
    get_device_mode_async = 0x16
    get_secondary_mcu_version = 0x17
    get_secondary_mcu_version_async = 0x18
    get_animation_version = 0x19
    get_animation_version_async = 0x1a
    set_audio_crc = 0x22
    get_audio_crc = 0x23
    get_level_one_diagnostics = 0x26
    level_one_diagnostics_async = 0x27
    # get_sku = 0x28
    get_secondary_mcu_status = 0x29
    secondary_mcu_status_async = 0x2a
    get_sku = 0x38


class SystemInfo(DeviceApiABC):
    device_id = DeviceId.system_info

    def get_main_application_version(self) -> Version:
        """
        Get version of toys firmware

        :return Version:
        """

        response = self.request(SystemInfoCommand.get_main_application_version)
        return Version(
            major=int.from_bytes(response.data[:2], "big"),
            minor=int.from_bytes(response.data[2:4], "big"),
            revision=int.from_bytes(response.data[4:], "big"),
        )

    def get_bootloader_version(self) -> Version:
        """
        Get version of toys bootloader

        :return Version:
        """

        response = self.request(SystemInfoCommand.get_bootloader_version)
        return Version(
            major=int.from_bytes(response.data[:2], "big"),
            minor=int.from_bytes(response.data[2:4], "big"),
            revision=int.from_bytes(response.data[4:], "big"),
        )

    def get_mac_address(self) -> str:
        """
        Get toy's mac address as "aa:bb:cc:dd:ee:ff"

        :return str:
        """

        response = self.request(SystemInfoCommand.get_mac_address)
        return ":".join(chr(b1) + chr(b2) for b1, b2 in zip(response.data[0::2], response.data[1::2]))

    def get_nordic_temperature(self) -> int:
        """
        ???

        :return str:
        """

        response = self.request(SystemInfoCommand.get_nordic_temperature)
        return int.from_bytes(response.data, "big")

    def get_stats_id(self) -> int:
        """
        ???

        :return:
        """

        response = self.request(SystemInfoCommand.get_stats_id, target_id=0x11)
        return int.from_bytes(response.data, "big")

    def get_sku(self) -> str:
        response = self.request(SystemInfoCommand.get_sku, target_id=0x11)
        return "".join(chr(b) for b in response.data)
