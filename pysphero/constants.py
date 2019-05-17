from enum import Enum

from pysphero.helpers import UnknownEnumMixing


class GenericCharacteristic(Enum):
    device_name = 0x2a00
    client_characteristic_configuration = 0x2902
    peripheral_preferred_connection_parameters = 0x2a04


class SpheroCharacteristic(Enum):
    api_v2 = "00010002-574f-4f20-5370-6865726f2121"


class Api2Error(UnknownEnumMixing, Enum):
    success = 0x00
    bad_device_id = 0x01
    bad_command_id = 0x02
    not_yet_implemented = 0x03
    command_is_restricted = 0x04
    bad_data_length = 0x05
    command_failed = 0x06
    bad_parameter_value = 0x07
    busy = 0x08
    bad_target_id = 0x09
    target_unavailable = 0x0a
    unknown = 0xff
