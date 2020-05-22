from enum import Enum

from pysphero.helpers import UnknownEnumMixing


class GenericCharacteristic(Enum):
    device_name = 0x2a00
    client_characteristic_configuration = 0x2902
    peripheral_preferred_connection_parameters = 0x2a04


class SpheroCharacteristic(Enum):
    force_band = "00020005-574f-4f20-5370-6865726f2121"
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


class Toy(Enum):
    unknown = "Unknown"

    sphero_sprk = "Sphero SPRK+"
    sphero_bolt = "Sphero Bolt"
    sphero_mini = "Sphero MINI"
    ollie = "Ollie"
    r2d2 = "R2D2"
    r2q5 = "R2Q5"
    bb8 = "BB8"
    bb9e = "BB9E"
    lmq = "LightningMcQueen"


TOY_BY_PREFIX = {
    "SK-": Toy.sphero_sprk,
    "SB-": Toy.sphero_bolt,
    "SM-": Toy.sphero_mini,
    "2B-": Toy.ollie,
    "D2-": Toy.r2d2,
    "Q5-": Toy.r2q5,
    "BB-": Toy.bb8,
    "GB-": Toy.bb9e,
    "LM-": Toy.lmq,
}
