import abc
import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Callable, Optional

from pysphero.bluetooth.packet_collector import PacketCollector
from pysphero.exceptions import PySpheroRuntimeError
from pysphero.packet import Packet

logger = logging.getLogger(__name__)

STOP_NOTIFY = object()


class AbstractBleAdapter(abc.ABC):
    def __init__(self, mac_address, max_workers=2):
        self.mac_address = mac_address
        self.packet_collector = PacketCollector()

        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._running = Event()  # disable receiver thread
        self._running.set()
        self._notify_future = None

    def close(self):
        self._running.clear()
        self._executor.shutdown(wait=False)

    def write(self, packet: Packet, *, timeout: float = 10, raise_api_error: bool = True) -> Optional[Packet]:
        """
         Method allow send request packet and get response packet

         :param packet: request packet
         :param timeout: timeout waiting for a response from sphero
         :param raise_api_error: raise exception when receive api error
         :return Packet: response packet
         """

    def start_notify(self, packet: Packet, callback: Callable, timeout: float = 10):
        self._notify_future = self._executor.submit(
            self.notify_worker,
            callback,
            packet,
            timeout,
        )
        return self._notify_future

    def stop_notify(self):
        if self._notify_future is None:
            raise PySpheroRuntimeError("Future not found")

        logger.debug(f"[NOTIFY_WORKER] Cancel")
        self._notify_future.cancel()
        self._notify_future = None

    def notify_worker(self, callback: Callable, packet: Packet, timeout: float):
        logger.debug(f"[NOTIFY_WORKER] Start {packet}")

        while self._running.is_set():
            response = self.packet_collector.get_response(packet, raise_api_error=False, timeout=timeout)
            logger.debug(f"[NOTIFY_WORKER] Received {response}")
            if callback(response) is STOP_NOTIFY:
                logger.debug(f"[NOTIFY_WORKER] Received STOP_NOTIFY")
                self._notify_future = None
                break
