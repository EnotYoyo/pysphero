from enum import Enum

from pysphero.device_api import DeviceApiABC, DeviceId


class AnimatronicsCommand(Enum):
    play_animation = 0x05
    perform_leg_action = 0x0d
    set_head_position = 0x0f
    play_animation_complete_notify = 0x11
    get_head_position = 0x14
    set_leg_position = 0x15
    get_leg_position = 0x16
    get_leg_action = 0x25
    leg_action_complete_notify = 0x26
    stop_animation = 0x2b
    get_trophy_mode_enabled = 0x2e


class Animatronics(DeviceApiABC):
    device_id = DeviceId.animatronics

    def play_animation(self, animation_id):
        self.request(
            AnimatronicsCommand.play_animation,
            data=[animation_id],
            target_id=0x12,
        )


