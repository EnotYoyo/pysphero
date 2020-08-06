from enum import Enum
from typing import List, Tuple

from pysphero.constants import Api2Error
from pysphero.exceptions import PySpheroRuntimeError
from pysphero.helpers import cached_property


class Flag(Enum):
    """
    Flag bits
    """
    response = 0x1
    requests_response = 0x2
    requests_only_error_response = 0x4
    resets_inactivity_timeout = 0x8
    command_has_target_id = 0x10
    command_has_source_id = 0x20


class Packet:
    """
    Packet structure:
    ---------------------------------
    - start      [1 byte]
    - flags      [1 byte]
    - source_id  [1 byte] (optional)
    - target_id  [1 byte] (optional)
    - device_id  [1 byte]
    - command_id [1 byte]
    - data       [n byte]
    - checksum   [1 byte]
    - end        [1 byte]
    ---------------------------------
    Usually the first data byte is the api_v2 response code
    """

    _sequence = 0x00

    start = 0x8d
    end = 0xd8

    escape = 0xab
    escape_mask = 0x88
    escaped_bytes = start & ~escape_mask, end & ~escape_mask, escape & ~escape_mask
    bad_bytes = start, end, escape

    def __init__(
            self,
            device_id: int,
            command_id: int,
            flags: int = None,
            target_id: int = None,
            source_id: int = None,
            sequence: int = None,
            data: List[int] = None,
    ):
        # For LMQ a notification with flag 0x00 is sent once audio has been played
        self.flags = flags
        if flags is None:
            self.flags = (Flag.requests_response.value | Flag.resets_inactivity_timeout.value)
        if flags is None and source_id is not None:
            self.flags |= Flag.command_has_source_id.value
        if flags is None and target_id is not None:
            self.flags |= Flag.command_has_target_id.value

        self.target_id = target_id
        self.source_id = source_id
        self.device_id = device_id
        self.command_id = command_id
        self.sequence = sequence if sequence is not None else self.generate_sequence()
        self.data = data or []
    
    @classmethod
    def generate_sequence(cls):
        """
        Autoincrement sequence number of packet
        """
        cls._sequence = (cls._sequence + 1) % 256
        return cls._sequence

    @property
    def id(self) -> Tuple:
        return self.device_id, self.command_id

    def __str__(self) -> str:
        return f"Packet(flg: {self.flags:#04x} did: {self.device_id:#04x} cid: {self.command_id:#04x} " \
               f"seq: {self.sequence:#04x})"

    def __repr__(self) -> str:
        return f"Packet(flg: {self.flags:#04x} tid: {self.target_id or 0x0:#04x} sid: {self.source_id or 0x0:#04x} " \
               f"did: {self.device_id:#04x} cid: {self.command_id:#04x} " \
               f"seq: {self.sequence:#04x}) data: {[hex(i) for i in self.data]} chs: {self.checksum:#04x})"

    @cached_property
    def api_error(self) -> Api2Error:
        if self.flags & Flag.response.value and len(self.data) > 0:
            return Api2Error(self.data.pop(0))  # delete first byte from data
        return Api2Error.success

    @staticmethod
    def _unescape_response_data(response_data) -> List[int]:
        raw_data = []

        iter_response_data = iter(response_data)
        for b in iter_response_data:
            # escaping byte allowing escaping start/end/escaping bytes
            if b == Packet.escape:
                # next byte is escaping
                b = next(iter_response_data, None)
                if b not in Packet.escaped_bytes:
                    raise PySpheroRuntimeError(f"Bad escaping byte {b:#04x}")

                b |= Packet.escape_mask

            raw_data.append(b)

        return raw_data

    @classmethod
    def from_response(cls, response_data: List[int]) -> "Packet":
        """
        Create packet from raw data
        :param response_data: raw data from peripheral
        :return Packet: response packet
        """
        response_data = Packet._unescape_response_data(response_data)
        start, flags, *data, checksum, end = response_data
        if start != cls.start or end != cls.end:
            raise PySpheroRuntimeError(
                f"Bad response packet: wrong start or end byte (start: {start:#04x}, end: {end:#04x})"
            )

        target_id = None
        if flags & Flag.command_has_target_id.value:
            target_id = data.pop(0)

        source_id = None
        if flags & Flag.command_has_source_id.value:
            source_id = data.pop(0)

        device_id, command_id, sequence, *data = data

        packet = cls(
            flags=flags,
            target_id=target_id,
            source_id=source_id,
            device_id=device_id,
            command_id=command_id,
            sequence=sequence,
            data=data,
        )

        calc_checksum = packet.checksum
        if calc_checksum != checksum:
            raise PySpheroRuntimeError(
                f"Bad response checksum. (Expected: {checksum:#04x}, obtained: {calc_checksum:#04x})"
            )

        return packet

    @property
    def packet_payload(self) -> List[int]:
        head = [self.flags]

        if self.target_id is not None:
            head.append(self.target_id)

        if self.source_id is not None:
            head.append(self.source_id)

        return [
            *head,
            self.device_id,
            self.command_id,
            self.sequence,
            *self.data,
        ]

    @property
    def checksum(self) -> int:
        return 0xff - (sum(self.packet_payload) & 0xff)

    def build(self) -> bytes:
        full_packet = [
            *self.packet_payload,
            self.checksum,
        ]

        escaped_full_packet = []
        for i in full_packet:
            if i in self.bad_bytes:
                escaped_full_packet.extend([self.escape, i & ~self.escape_mask])
            else:
                escaped_full_packet.append(i)

        return b"".join(i.to_bytes(1, byteorder="big") for i in [self.start, *escaped_full_packet, self.end])
