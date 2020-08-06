import logging
import time
from typing import List, Optional

from pysphero.constants import Api2Error
from pysphero.exceptions import PySpheroTimeoutError, PySpheroRuntimeError, PySpheroApiError
from pysphero.packet import Packet, Flag

logger = logging.getLogger(__name__)


class PacketCollector:
    def __init__(self, check_response_delta: float = 0.1):
        self._data = []
        self._packets = {}
        self._check_response_delta = check_response_delta or 0.01  # protect of 0 sleep_time

    def append_raw_data(self, data: List[int]):
        for b in data:
            logger.debug(f"Received {b:#04x}")
            self._data.append(b)

            # packet always ending with end byte
            if b == Packet.end:
                if len(self._data) < 6:
                    raise PySpheroRuntimeError(f"Very small packet {[hex(x) for x in self.data]}")
                self._build_packet()

    def _build_packet(self):
        """
        Create and save packet from raw bytes
        """
        logger.debug(f"Starting of packet build")

        packet = Packet.from_response(self._data)
        self._packets[packet.id] = packet
        self._data = []

    def get_response(self, packet: Packet, raise_api_error: bool = True, timeout: float = 10) -> Optional[Packet]:
        if (packet.flags & (Flag.requests_response.value | Flag.requests_only_error_response.value)) == 0:
            return

        while True:
            response = self._packets.pop(packet.id, None)
            if response:
                if raise_api_error and response.api_error is not Api2Error.success:
                    raise PySpheroApiError(response.api_error)

                return response

            timeout -= self._check_response_delta
            if timeout <= 0:
                raise PySpheroTimeoutError(f"Timeout error for response of {packet}")

            time.sleep(self._check_response_delta)
