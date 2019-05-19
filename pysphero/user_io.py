from enum import Enum

from pysphero.device_api import DeviceApiABC, DeviceId


class Led(Enum):
    front_red = 0x01
    front_green = 0x02
    front_blue = 0x04
    back_red = 0x08
    back_green = 0x10
    back_blue = 0x20
    all = front_red | front_green | front_blue | back_red | back_green | back_blue


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
    set_led_matrix_one_color = 0x2f


class UserIO(DeviceApiABC):
    device_id = DeviceId.user_io

    def set_all_leds_8_bit_mask(
            self,
            front_red: int = 0x00,
            front_green: int = 0x00,
            front_blue: int = 0x00,
            back_red: int = 0x00,
            back_green: int = 0x00,
            back_blue: int = 0x00,
    ):
        """
        Set leds colors

        note: this command is supported Sphero Bolt.
        For another toys use set_all_leds

        :param front_red:
        :param front_green:
        :param front_blue:
        :param back_red:
        :param back_green:
        :param back_blue:
        :return:
        """
        leds = Led.all.value
        self.request(
            command_id=UserIOCommand.set_all_leds_8_bit_mask,
            data=[leds, front_red, front_green, front_blue, back_red, back_green, back_blue],
            target_id=0x11,
        )
