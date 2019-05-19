from enum import Enum
from typing import NamedTuple

from pysphero.device_api import DeviceApiABC, DeviceId


class Color(NamedTuple):
    red: int = 0x00
    green: int = 0x00
    blue: int = 0x00

    def to_list(self):
        return [self.red & 0xff, self.green & 0xff, self.blue & 0xff]


class Pixel(NamedTuple):
    x: int = 0
    y: int = 0

    def to_list(self):
        return [self.x & 0x07, self.y & 0x07]


class Led(Enum):
    front_red = 0x01
    front_green = 0x02
    front_blue = 0x04
    back_red = 0x08
    back_green = 0x10
    back_blue = 0x20
    all = front_red | front_green | front_blue | back_red | back_green | back_blue


class FrameRotation(Enum):
    normal = 0x00
    degrees_90 = 0x01
    degrees_180 = 0x02
    degrees_270 = 0x03


class UserIOCommand(Enum):
    enable_gesture_event_notification = 0x00
    gesture_event = 0x01
    enable_button_event_notification = 0x02
    button_event = 0x03
    set_led = 0x04
    release_led_request = 0x05
    play_haptic_pattern = 0x06
    play_audio_file = 0x07
    set_audio_volume = 0x08
    get_audio_volume = 0x09
    stop_all_audio = 0x0a
    cap_touch_enable = 0x0b
    ambient_light_sensor_enable = 0x0c
    enable_ir = 0x0d
    set_all_leds = 0x0e
    set_backlight_intensity = 0x0f
    cap_touch_indication = 0x10
    enable_debug_data = 0x11
    assert_lcd_reset_pin = 0x12
    set_headlights = 0x13
    set_taillights = 0x14
    play_test_tone = 0x18
    start_idle_led = 0x19
    toy_commands = 0x20
    toy_events = 0x21
    set_user_profile = 0x22
    get_user_profile = 0x23
    set_all_leds_32_bit_mask = 0x1a
    set_all_leds_64_bit_mask = 0x1b
    set_all_leds_8_bit_mask = 0x1c
    set_led_matrix_pixel = 0x2d
    set_led_matrix_one_color = 0x2f
    set_led_matrix_frame_rotation = 0x3a
    set_led_matrix_text_scrolling = 0x3b
    set_led_matrix_text_scrolling_notify = 0x3c
    set_led_matrix_single_character = 0x42


class UserIO(DeviceApiABC):
    device_id = DeviceId.user_io

    def set_all_leds_8_bit_mask(
            self,
            front_color: Color = Color(),
            back_color: Color = Color(),
    ):
        """
        Set leds colors

        note: this command is supported Sphero Bolt.
        For another toys use set_all_leds

        :param Color front_color:
        :param Color back_color:
        :return:
        """
        leds = Led.all.value
        self.request(
            command_id=UserIOCommand.set_all_leds_8_bit_mask,
            data=[leds, *front_color.to_list(), *back_color.to_list()],
            target_id=0x11,
        )

    def set_led_matrix_one_color(self, color: Color = Color()):
        """
        Set matrix one color

        :param Color color:
        :return:
        """
        self.request(
            command_id=UserIOCommand.set_led_matrix_one_color,
            data=color.to_list(),
            target_id=0x12,
        )

    def set_led_matrix_pixel(self, pixel: Pixel, color: Color = Color()):
        """
        Put into pixel the color

        :param Pixel pixel:
        :param Color color:
        :return:
        """
        self.request(
            command_id=UserIOCommand.set_led_matrix_pixel,
            data=[*pixel.to_list(), *color.to_list()],
            target_id=0x12,
        )

    def set_led_matrix_single_character(self, symbol: str, color: Color):
        """
        Print symbol on matrix

        :param String symbol:
        :param Color color:
        :return:
        """
        self.request(
            command_id=UserIOCommand.set_led_matrix_single_character,
            data=[*color.to_list(), ord(symbol)],
            target_id=0x12,
        )

    def set_led_matrix_text_scrolling(self, string: str, color: Color, speed: int = 0x10, repeat: bool = True):
        """
        Print text on matrix

        :param str string: max length 6 symbols
        :param Color color:
        :param int speed: max value is 0x1e (30)
        :param bool repeat:
        :return:
        """
        self.request(
            command_id=UserIOCommand.set_led_matrix_text_scrolling,
            data=[
                *color.to_list(),
                speed % 0x1e,
                int(repeat),
                *[ord(c) for c in string[:7]],
                0x00,  # end line
            ],
            target_id=0x12,
        )

    def set_led_matrix_text_scrolling_notify(self):
        self.request(
            command_id=UserIOCommand.set_led_matrix_text_scrolling_notify,
            data=[0x00],  # todo: unknown
            target_id=0x11,
        )

    def set_led_matrix_frame_rotation(self, rotation: FrameRotation = FrameRotation.normal):
        self.request(
            command_id=UserIOCommand.set_led_matrix_frame_rotation,
            data=[rotation.value],
            target_id=0x11,
        )
