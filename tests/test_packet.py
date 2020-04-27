import pytest

from pysphero.constants import Api2Error
from pysphero.exceptions import PySpheroRuntimeError
from pysphero.packet import Packet


def test_packet_init():
    packet = Packet(0x23, 0x42)
    assert packet.device_id == 0x23
    assert packet.command_id == 0x42
    assert packet.flags == 0x0a
    assert packet.target_id is None
    assert packet.source_id is None
    assert packet.sequence == Packet._sequence
    assert packet.data == []


def test_packet_source_id():
    packet = Packet(0x23, 0x42, source_id=0x01)
    assert packet.device_id == 0x23
    assert packet.command_id == 0x42
    assert packet.flags == 0x2a
    assert packet.target_id is None
    assert packet.source_id == 0x01
    assert packet.sequence == Packet._sequence
    assert packet.data == []


def test_packet_target_id():
    packet = Packet(0x23, 0x42, target_id=0x01)
    assert packet.device_id == 0x23
    assert packet.command_id == 0x42
    assert packet.flags == 0x1a
    assert packet.target_id == 0x01
    assert packet.source_id is None
    assert packet.sequence == Packet._sequence
    assert packet.data == []


def test_packet_flags():
    packet = Packet(0x23, 0x42, flags=0x01)
    assert packet.device_id == 0x23
    assert packet.command_id == 0x42
    assert packet.flags == 0x01
    assert packet.target_id is None
    assert packet.source_id is None
    assert packet.sequence == Packet._sequence
    assert packet.data == []


def test_packet_flags_with_source_id():
    packet = Packet(0x23, 0x42, flags=0x01, source_id=0x02)
    assert packet.device_id == 0x23
    assert packet.command_id == 0x42
    assert packet.flags == 0x01
    assert packet.target_id is None
    assert packet.source_id == 0x02
    assert packet.sequence == Packet._sequence
    assert packet.data == []


def test_packet_flags_with_target_id():
    packet = Packet(0x23, 0x42, flags=0x01, target_id=0x02)
    assert packet.device_id == 0x23
    assert packet.command_id == 0x42
    assert packet.flags == 0x01
    assert packet.target_id == 0x02
    assert packet.source_id is None
    assert packet.sequence == Packet._sequence
    assert packet.data == []


def test_packet_id():
    packet = Packet(0x23, 0x42)
    assert packet.id == (0x23, 0x42)


def test_packet_sequence():
    Packet._sequence = 0x00
    packet1 = Packet(0x23, 0x42)
    packet2 = Packet(0x23, 0x42)
    assert packet1.sequence == 0x01
    assert packet2.sequence == 0x02
    assert Packet._sequence == 0x02


def test_packet_str_and_repr():
    """validate the correct works"""
    packet = Packet(0x23, 0x42)
    assert isinstance(str(packet), str)
    assert isinstance(repr(packet), str)


def test_packet_api_error():
    packet = Packet(0x23, 0x42, flags=0x01, data=[0x00, 0x16])
    assert packet.api_error is Api2Error.success
    assert len(packet.data) == 1

    # check cached property
    assert packet.api_error is Api2Error.success
    assert len(packet.data) == 1


def test_packet_api_error_without_flags():
    packet = Packet(0x23, 0x42, data=[0x00, 0x16])
    assert packet.api_error is Api2Error.success
    assert len(packet.data) == 2


def test_packet_api_error_unknown():
    packet = Packet(0x23, 0x42, flags=0x01, data=[0x15, 0x16])
    assert packet.api_error is Api2Error.unknown
    assert len(packet.data) == 1


def test_packet_payload():
    packet = Packet(0x23, 0x42, sequence=0x01, data=[0x15, 0x16])
    assert packet.packet_payload == [0x0a, 0x23, 0x42, 0x01, 0x15, 0x16]


def test_packet_payload_with_source_id():
    packet = Packet(0x23, 0x42, sequence=0x01, data=[0x15, 0x16], source_id=0x02)
    assert packet.packet_payload == [0x2a, 0x02, 0x23, 0x42, 0x01, 0x15, 0x16]


def test_packet_payload_with_target_id():
    packet = Packet(0x23, 0x42, sequence=0x01, data=[0x15, 0x16], target_id=0x03)
    assert packet.packet_payload == [0x1a, 0x03, 0x23, 0x42, 0x01, 0x15, 0x16]


def test_packet_checksum():
    packet = Packet(0x23, 0x42, sequence=0x01, data=[0x15, 0x16], target_id=0x03)
    assert packet.checksum == 0x51


def test_packet_build():
    packet = Packet(0x23, 0x42, sequence=0x01, data=[0x15, 0x16])
    raw_packet = [0x8d, 0x0a, 0x23, 0x42, 0x01, 0x15, 0x16, 0x64, 0xd8]
    assert packet.build() == b"".join(b.to_bytes(1, "big") for b in raw_packet)


def test_packet_build_with_escape():
    packet = Packet(0x23, 0x42, sequence=0x01, data=[0xab, 0x8d])
    raw_packet = [0x8d, 0x0a, 0x23, 0x42, 0x01, 0xab, 0x23, 0xab, 0x05, 0x57, 0xd8]
    assert packet.build() == b"".join(b.to_bytes(1, "big") for b in raw_packet)


def test_packet_from_response():
    raw_packet = [0x8d, 0x0a, 0x23, 0x42, 0x01, 0x15, 0x16, 0x64, 0xd8]
    packet = Packet.from_response(raw_packet)
    assert packet.flags == 0x0a
    assert packet.source_id is None
    assert packet.target_id is None
    assert packet.device_id == 0x23
    assert packet.command_id == 0x42
    assert packet.sequence == 0x01
    assert packet.data == [0x15, 0x16]
    assert packet.checksum == 0x64


def test_packet_from_response_with_escape_symbols():
    raw_packet = [0x8d, 0x0a, 0x23, 0x42, 0x01, 0xab, 0x23, 0xab, 0x05, 0x57, 0xd8]
    packet = Packet.from_response(raw_packet)
    assert packet.flags == 0x0a
    assert packet.source_id is None
    assert packet.target_id is None
    assert packet.device_id == 0x23
    assert packet.command_id == 0x42
    assert packet.sequence == 0x01
    assert packet.data == [0xab, 0x8d]
    assert packet.checksum == 0x57


def test_packet_from_response_with_target_id():
    raw_packet = [0x8d, 0x1a, 0xfe, 0x23, 0x42, 0x01, 0xab, 0x23, 0xab, 0x05, 0x49, 0xd8]
    packet = Packet.from_response(raw_packet)
    assert packet.flags == 0x1a
    assert packet.source_id is None
    assert packet.target_id == 0xfe
    assert packet.device_id == 0x23
    assert packet.command_id == 0x42
    assert packet.sequence == 0x01
    assert packet.data == [0xab, 0x8d]
    assert packet.checksum == 0x49


def test_packet_from_response_with_source_id():
    raw_packet = [0x8d, 0x2a, 0xfe, 0x23, 0x42, 0x01, 0xab, 0x23, 0xab, 0x05, 0x39, 0xd8]
    packet = Packet.from_response(raw_packet)
    assert packet.flags == 0x2a
    assert packet.source_id == 0xfe
    assert packet.target_id is None
    assert packet.device_id == 0x23
    assert packet.command_id == 0x42
    assert packet.sequence == 0x01
    assert packet.data == [0xab, 0x8d]
    assert packet.checksum == 0x39


def test_packet_from_response_bad_data():
    # bad start
    raw_packet = [0xad, 0x0a, 0x23, 0x42, 0x01, 0x15, 0x16, 0x64, 0xd8]
    with pytest.raises(PySpheroRuntimeError):
        Packet.from_response(raw_packet)

    # bad end
    raw_packet = [0x8d, 0x0a, 0x23, 0x42, 0x01, 0x15, 0x16, 0x64, 0xdd]
    with pytest.raises(PySpheroRuntimeError):
        Packet.from_response(raw_packet)

    # bad checksum
    raw_packet = [0x8d, 0x0a, 0x23, 0x42, 0x01, 0x15, 0x16, 0xff, 0xd8]
    with pytest.raises(PySpheroRuntimeError):
        Packet.from_response(raw_packet)
