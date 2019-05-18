from enum import Enum

from pysphero.device_api import DeviceApiABC, DeviceId
from pysphero.packet import Flag


class Direction(Enum):
    forward = 0x00
    reverse = 0x01


class DirectionRawMotor(Enum):
    disable = 0x00
    forward = 0x01
    reverse = 0x02


class StabilizationIndex(Enum):
    no_control_system = 0x00
    full_control_system = 0x01
    pitch_control_system = 0x02
    roll_control_system = 0x03
    yaw_control_system = 0x04
    speed_and_yaw_control_system = 0x05


class DrivingCommand(Enum):
    raw_motor = 0x01
    set_ackermann_steering_parameters = 0x02
    drift = 0x03
    absolute_yaw_steering = 0x04
    enable_flip_drive = 0x05
    reset_yaw = 0x06
    drive_with_heading = 0x07
    tank_drive = 0x08
    rc_car_drive = 0x09
    drive_to_position = 0x0a
    set_stabilization = 0x0c


class Driving(DeviceApiABC):
    device_id = DeviceId.driving

    def drive_with_heading(self, speed: int, heading: int, direction: Direction = Direction.forward):
        """

        :param int speed: speed from 0 to 255
        :param int heading: heading from 0 to 360
        :param Direction direction: motor rotation direction
        :return:
        """
        speed &= 0xff
        heading = heading.to_bytes(2, "big")
        direction = direction.value

        self.request(
            DrivingCommand.drive_with_heading,
            target_id=0x12,
            data=[speed, *heading, direction],
            flags=Flag.requests_response.value | Flag.command_has_target_id.value | Flag.resets_inactivity_timeout.value
        )

    def set_stabilization(self, stabilization_index: StabilizationIndex):
        """
        ???

        :param StabilizationIndex stabilization_index:
        :return:
        """
        self.request(
            DrivingCommand.set_stabilization,
            target_id=0x12,
            data=[stabilization_index.value],
        )

    def raw_motor(
            self,
            left_speed: int = 0x00,
            left_direction: DirectionRawMotor = DirectionRawMotor.forward,
            right_speed=0x00,
            right_direction: DirectionRawMotor = DirectionRawMotor.forward,
    ):
        """
        Control of each motor separately

        note: it works strange :) after wake up need sleeps

        :param int left_speed: speed of left motor from 0 to 255
        :param DirectionRawMotor left_direction:
        :param int right_speed: speed of right motor from 0 to 255
        :param DirectionRawMotor right_direction:
        :return:

        """
        left_direction = left_direction.value
        right_direction = right_direction.value

        self.request(
            DrivingCommand.raw_motor,
            target_id=0x12,
            data=[
                left_direction, left_speed & 0xff,
                right_direction, right_speed & 0xff,
            ],
        )

    def reset_yaw(self):
        """
        Reset of toys yaw

        :return:
        """
        self.request(
            DrivingCommand.reset_yaw,
            target_id=0x12,
        )
