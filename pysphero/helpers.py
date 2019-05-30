import struct
from typing import Callable


class cached_property:
    def __init__(self, func: Callable):
        self.func = func

    def __get__(self, instance, type=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


class UnknownEnumMixing:
    unknown = 0x00

    @classmethod
    def _missing_(cls, value):
        return cls.unknown


def float_from_bytes(data):
    return struct.unpack(">f", bytearray(data))[0]
