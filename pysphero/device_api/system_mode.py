from enum import Enum


class SystemModeCommand(Enum):
    set_system_mode = 0x00
    get_system_mode = 0x01
    enable_system_mode_notification = 0x02
    system_mode_changed = 0x03
    set_max_speed = 0x04
    get_max_speed = 0x05
    set_current_weapon = 0x06
    get_current_weapon = 0x07
    set_aiming_mode = 0x08
    get_playmode_unlock_mask = 0x09
    set_playmode_unlock_mask = 0x0a
    enable_menu_item_change_notification = 0x0b
    menu_item_changed = 0x0c
    get_enabled_weapons_mask = 0x0d
    set_enabled_weapons_mask = 0x0e
    get_holocron_counts = 0x10
    dec_holocron_count = 0x13
    clear_holocron_count = 0x14
    find_holocron_now = 0x15
    enable_force_awareness_reporting = 0x16
    force_awareness_event_async = 0x17
    set_category_rarity = 0x18
    get_angle_to_holocron = 0x19
    set_fa_disturbance_timeout = 0x1a
    set_audio_header = 0x1b
    set_audio_header_async = 0x1c
    enable_robot_bas_app_report = 0x20
    robot_bad_app_report = 0x21
    get_pending_action_list = 0x22
    get_audio_info = 0x23
