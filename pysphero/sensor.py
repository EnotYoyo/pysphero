from enum import Enum
from typing import NamedTuple, Callable, Type, Tuple, List

from pysphero.device_api import DeviceApiABC, DeviceId
from pysphero.helpers import float_from_bytes, grouper
from pysphero.packet import Packet


class SensorParameter(NamedTuple):
    flag: int
    min_value: float
    max_value: float
    modifier: Callable = None


class _Sensor(Enum):
    """Parent class for all sensors"""

    @classmethod
    def mask(cls) -> int:
        _mask = 0x0
        for parameter in cls:
            _mask |= parameter.value.flag

        return _mask


# next sensors class created for Sphero Bolt
# todo: refactoring this for all Sphero Toys
class Quaternion(_Sensor):
    x = SensorParameter(0x2000000, -1.0, 1.0)
    y = SensorParameter(0x1000000, -1.0, 1.0)
    z = SensorParameter(0x800000, -1.0, 1.0)
    w = SensorParameter(0x400000, -1.0, 1.0)


class Attitude(_Sensor):
    pitch = SensorParameter(0x40000, -179.0, 180.0)
    roll = SensorParameter(0x20000, -179.0, 180.0)
    yaw = SensorParameter(0x10000, -179.0, 180.0)


class Accelerometer(_Sensor):
    x = SensorParameter(0x8000, -8.19, 8.19)
    y = SensorParameter(0x4000, -8.19, 8.19)
    z = SensorParameter(0x2000, -8.19, 8.19)


class AccelOne(_Sensor):
    accel_one = SensorParameter(0x200, 0.0, 8000.0)


class Locator(_Sensor):
    x = SensorParameter(0x40, -32768.0, 32767.0, lambda x: x * 100)
    y = SensorParameter(0x20, -32768.0, 32767.0, lambda x: x * 100)


class Velocity(_Sensor):
    x = SensorParameter(0x10, -32768.0, 32767.0, lambda x: x * 100)
    y = SensorParameter(0x08, -32768.0, 32767.0, lambda x: x * 100)


class Speed(_Sensor):
    speed = SensorParameter(0x04, 0.0, 32767.0)


class CoreTime(_Sensor):
    core_time = SensorParameter(0x02, 0.0, 0.0)


class Gyroscope(_Sensor):
    x = SensorParameter(0x2000000, -20000.0, 20000.0)
    y = SensorParameter(0x1000000, -20000.0, 20000.0)
    z = SensorParameter(0x800000, -20000.0, 20000.0)


class AmbientLight(_Sensor):
    ambient_light = SensorParameter(0x40000, 0.0, 120000.0)


class SensorCommand(Enum):
    set_sensor_streaming_mask = 0x00
    get_sensor_streaming_mask = 0x01
    sensor_streaming_data = 0x02
    run_accel_gyro_self_test = 0x06
    set_extended_sensor_streaming_mask = 0x0c
    get_extended_sensor_streaming_mask = 0x0d
    set_gyro_max_async = 0x0f
    gyro_max_async = 0x10
    configure_collision_detection = 0x11
    collision_detected_async = 0x12
    reset_locator = 0x13
    enable_collision_detected_async = 0x14
    subscribe_maneuver_async_notification = 0x15
    maneuver_detection_async = 0x16
    set_locator_flags = 0x17
    enable_accelerometer_activity_notify = 0x19
    accelerometer_activity_notify = 0x1a
    magnetometer_calibrate_to_north = 0x25
    magnetometer_north_yaw_notify = 0x26
    get_ambient_light_sensor_value = 0x30


class Sensor(DeviceApiABC):
    device_id = DeviceId.sensors

    def _set_sensor_streaming_mask(self, mask, interval: int = 250, count: int = 0):
        self.request(
            command_id=SensorCommand.set_sensor_streaming_mask,
            data=[*interval.to_bytes(2, "big"),  # interval
                  count & 0xff,  # count,
                  *mask.to_bytes(4, "big"),  # 0x00, 0x00, 0x80, 0x00  # mask
                  ],
            target_id=0x12,
        )

    def set_notify(
            self,
            callback: Callable,
            *sensors: Type[_Sensor],
            interval: int = 250,
            count: int = 0,
            timeout: float = 1,
    ):
        parameters = []
        mask = 0x0
        for sensor in sensors:
            parameters.extend(parameter for parameter in sensor)
            mask |= sensor.mask()

        parameters = sorted(parameters, key=lambda p: p.value.flag, reverse=True)

        def callback_wrapper(response: Packet):
            callback_data = {}
            for i, data in enumerate(grouper(response.data, 4, fillvalue=0x00)):
                value: float = float_from_bytes(data)

                parameter: Enum = parameters[i]
                if parameter.value.modifier:
                    value = parameter.value.modifier(value)

                callback_data[parameter] = value

            return callback(callback_data)

        self.notify(SensorCommand.sensor_streaming_data, callback_wrapper, sleep_time=interval / 1000, timeout=timeout)
        self._set_sensor_streaming_mask(mask, interval, count)

    def cancel_notify_sensors(self):
        self.cancel_notify(SensorCommand.sensor_streaming_data)

    def get_sensor_streaming_mask(self) -> Tuple[int, int, List[SensorParameter]]:
        response = self.request(
            command_id=SensorCommand.get_sensor_streaming_mask,
            target_id=0x12,
        )

        interval = int.from_bytes(response.data[:2], "big")
        count = int.from_bytes(response.data[2:3], "big")
        mask = int.from_bytes(response.data[3:], "big")

        parameters = []
        for sensor in _Sensor.__subclasses__():
            for parameter in sensor:
                if parameter.value.flag & mask:
                    parameters.append(parameter)

        return interval, count, parameters

    def get_ambient_light_sensor_value(self) -> float:
        response = self.request(
            command_id=SensorCommand.get_ambient_light_sensor_value,
            target_id=0x12,
        )

        return float_from_bytes(response.data)

    def magnetometer_calibrate_to_north(self):
        self.request(
            command_id=SensorCommand.magnetometer_calibrate_to_north,
            target_id=0x12,
        )
