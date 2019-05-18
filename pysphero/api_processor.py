from enum import Enum

from pysphero.device_api import DeviceApiABC, DeviceId


class ApiProcessorCommand(Enum):
    echo = 0x00


class ApiProcessor(DeviceApiABC):
    device_id = DeviceId.api_processor

    def echo(self):
        """
        Send ping
        :return None:
        """

        self.request(ApiProcessorCommand.echo)
