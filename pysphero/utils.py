import logging
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from threading import Event
from time import time
from typing import NamedTuple, Generator

from bluepy.btle import DefaultDelegate, Scanner, ScanEntry

from pysphero.constants import Toy, TOY_BY_PREFIX
from pysphero.core import Sphero
from pysphero.exceptions import PySpheroNotFoundError

logger = logging.getLogger(__name__)


class _ScanItem(NamedTuple):
    mac_address: str
    toy_type: Toy
    name: str


class _ScanDelegate(DefaultDelegate):

    def __init__(self):
        super().__init__()
        self.queue = Queue()

    def handleDiscovery(self, dev: ScanEntry, isNewDev: bool, isNewData: bool):
        name = dev.getValue(ScanEntry.COMPLETE_LOCAL_NAME) or ""
        toy_type = TOY_BY_PREFIX.get(name[:3])
        if toy_type:
            self.queue.put_nowait(_ScanItem(dev.addr, toy_type, name))


class _ContextScanner(Scanner):
    def __enter__(self, passive=False):
        self.clear()
        self.start(passive=passive)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def _queue_iter(queue: Queue, timeout: float) -> Generator[_ScanItem, None, None]:
    stop_time = time() + timeout
    while time() <= stop_time:
        try:
            scan_item: _ScanItem = queue.get(timeout=0.2)
        except Empty:
            continue

        logger.debug("Found toy %s", scan_item)
        yield scan_item


def _scanner(delegate: _ScanDelegate, timeout: float, event: Event):
    stop_time = time() + timeout
    scanner = _ContextScanner().withDelegate(delegate)
    with scanner:
        while event.is_set() and time() <= stop_time:
            scanner.process(0.2)


def toy_scanner(*, toy_type: Toy = None, name: str = None, timeout: float = 5.0) -> Sphero:
    delegate = _ScanDelegate()
    running_event = Event()
    running_event.set()

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(_scanner, delegate, timeout, running_event)
        for scan_item in _queue_iter(delegate.queue, timeout):

            # none when time is out
            if not scan_item:
                break

            if (
                    (not name and not toy_type) or
                    (name and name == scan_item.name) or
                    (toy_type and scan_item.toy_type == toy_type)
            ):
                running_event.clear()
                return Sphero(
                    mac_address=scan_item.mac_address,
                    toy_type=scan_item.toy_type,
                )

    raise PySpheroNotFoundError("Toy not found")
