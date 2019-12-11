import struct
from enum import Enum

from pysphero.helpers import float_from_bytes

from .device_api import DeviceApiABC, DeviceId


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


class R2D2Animation(Enum):
    charger_1 = 0x00
    charger_2 = 0x01
    charger_3 = 0x02
    charger_4 = 0x03
    charger_5 = 0x04
    charger_6 = 0x05
    charger_7 = 0x06
    emote_alarm = 0x07
    emote_angry = 0x08
    emote_annoyed = 0x09
    emote_chatty = 0x0a
    emote_drive = 0x0b
    emote_excited = 0x0c
    emote_happy = 0x0d
    emote_ion_blast = 0x0e
    emote_laugh = 0x0f
    emote_no = 0x10
    emote_sad = 0x11
    emote_sassy = 0x12
    emote_scared = 0x13
    emote_spin = 0x14
    emote_yes = 0x15
    emote_scan = 0x16
    emote_sleep = 0x17
    emote_surprised = 0x18
    idle_1 = 0x19
    idle_2 = 0x1a
    idle_3 = 0x1b
    patrol_alarm = 0x1c
    patrol_hit = 0x1d
    patrol_patrolling = 0x1e
    wwm_angry = 0x1f
    wwm_anxious = 0x20
    wwm_bow = 0x21
    wwm_concern = 0x22
    wwm_curious = 0x23
    wwm_double_take = 0x24
    wwm_excited = 0x25
    wwm_fiery = 0x26
    wwm_frustrated = 0x27
    wwm_happy = 0x28
    wwm_jittery = 0x29
    wwm_laugh = 0x2a
    wwm_long_shake = 0x2b
    wwm_no = 0x2c
    wwm_ominous = 0x2d
    wwm_relieved = 0x2e
    wwm_sad = 0x2f
    wwm_scared = 0x30
    wwm_shake = 0x31
    wwm_surprised = 0x32
    wwm_taunting = 0x33
    wwm_whisper = 0x34
    wwm_yelling = 0x35
    wwm_yoohoo = 0x36
    motor = 0x37


class R2Q5Animation(Enum):
    charger_1 = 0x00
    charger_3 = 0x01
    charger_2 = 0x02
    charger_4 = 0x03
    charger_5 = 0x04
    charger_6 = 0x05
    charger_7 = 0x06
    emote_alarm = 0x07
    emote_angry = 0x08
    emote_attention = 0x09
    emote_frustrated = 0x0a
    emote_drive = 0x0b
    emote_excited = 0x0c
    emote_search = 0x0d
    emote_short_circuit = 0x0e
    emote_laugh = 0x0f
    emote_no = 0x10
    emote_retreat = 0x11
    emote_fiery = 0x12
    emote_understood = 0x13
    emote_yes = 0x15
    emote_scan = 0x16
    emote_surprised = 0x18
    idle_1 = 0x19
    idle_2 = 0x1a
    idle_3 = 0x1b
    wwm_angry = 0x1f
    wwm_anxious = 0x20
    wwm_bow = 0x21
    wwm_concern = 0x22
    wwm_curious = 0x23
    wwm_double_take = 0x24
    wwm_excited = 0x25
    wwm_fiery = 0x26
    wmm_frustrated = 0x27
    wwm_happy = 0x28
    wwm_jittery = 0x29
    wwm_laugh = 0x2a
    wwm_long_shake = 0x2b
    wwm_no = 0x2c
    wwm_ominous = 0x2d
    wwm_relieved = 0x2e
    wwm_sad = 0x2f
    wwm_scared = 0x30
    wwm_shake = 0x31
    wwm_surprised = 0x32
    wwm_taunting = 0x33
    wwm_whisper = 0x34
    wwm_yelling = 0x35
    wwm_yoohoo = 0x36


class BB9EAnimation(Enum):
    EMOTE_ALARM = 0x00
    EMOTE_NO = 0x01
    EMOTE_SCAN_SWEEP = 0x02
    EMOTE_SCARED = 0x03
    EMOTE_YES = 0x04
    EMOTE_AFFIRMATIVE = 0x05
    EMOTE_AGITATED = 0x06
    EMOTE_ANGRY = 0x07
    EMOTE_CONTENT = 0x08
    EMOTE_EXCITED = 0x09
    EMOTE_FIERY = 0x0a
    EMOTE_GREETINGS = 0x0b
    EMOTE_NERVOUS = 0x0c
    EMOTE_SLEEP = 0x0e
    EMOTE_SURPRISED = 0x0f
    EMOTE_UNDERSTOOD = 0x10
    HIT = 0x11
    WWM_ANGRY = 0x12
    WWM_ANXIOUS = 0x13
    WWM_BOW = 0x14
    WWM_CURIOUS = 0x16
    WWM_DOUBLE_TAKE = 0x17
    WWM_EXCITED = 0x18
    WWM_FIERY = 0x19
    WWM_HAPPY = 0x1a
    WWM_JITTERY = 0x1b
    WWM_LAUGH = 0x1c
    WWM_LONG_SHAKE = 0x1d
    WWM_NO = 0x1e
    WWM_OMINOUS = 0x1f
    WWM_RELIEVED = 0x20
    WWM_SAD = 0x21
    WWM_SCARED = 0x22
    WWM_SHAKE = 0x23
    WWM_SURPRISED = 0x24
    WWM_TAUNTING = 0x25
    WWM_WHISPER = 0x26
    WWM_YELLING = 0x27
    WWM_YOOHOO = 0x28
    WWM_FRUSTRATED = 0x29
    IDLE_1 = 0x2a
    IDLE_2 = 0x2b
    IDLE_3 = 0x2c
    EYE_1 = 0x2d
    EYE_2 = 0x2e
    EYE_3 = 0x2f
    EYE_4 = 0x30


class R2LegAction(Enum):
    stop = 0x00
    three_legs = 0x01
    two_legs = 0x02
    waddle = 0x03


class Animatronics(DeviceApiABC):
    device_id = DeviceId.animatronics

    def play_animation(self, animation_id: int):
        self.request(
            AnimatronicsCommand.play_animation,
            data=[*animation_id.to_bytes(2, "big")],
            target_id=0x12,
        )

    def perform_leg_action(self, leg_action: R2LegAction):
        self.request(
            AnimatronicsCommand.perform_leg_action,
            data=[*leg_action.value.to_bytes(2, "big")],
            target_id=0x12,
        )

    def set_head_position(self, position: float):
        self.request(
            AnimatronicsCommand.set_head_position,
            data=[*struct.pack("f", position)],
            target_id=0x12,
        )

    def get_head_position(self) -> float:
        response = self.request(
            AnimatronicsCommand.get_head_position,
            target_id=0x12,
        )
        return float_from_bytes(response.data)

    def set_leg_position(self, position: float):
        self.request(
            AnimatronicsCommand.set_leg_position,
            data=[*struct.pack("f", position)],
            target_id=0x12,
        )

    def get_leg_position(self) -> float:
        response = self.request(
            AnimatronicsCommand.get_leg_position,
            target_id=0x12,
        )
        return float_from_bytes(response.data)

    def get_leg_action(self) -> R2LegAction:
        response = self.request(
            AnimatronicsCommand.get_leg_action,
            target_id=0x12,
        )
        return R2LegAction(int.from_bytes(response.data[:2], "big"))

    def stop_animation(self):
        self.request(
            AnimatronicsCommand.stop_animation,
            target_id=0x12,
        )

    def get_trophy_mode_enabled(self) -> bool:
        response = self.request(
            AnimatronicsCommand.get_trophy_mode_enabled,
            target_id=0x12,
        )
        return bool(int.from_bytes(response.data, "big"))
