from enum import Enum


class SecondaryMcuFirmwareUpdateCommand(Enum):
    begin_reflash = 0x00
    here_is_page = 0x01
    jump_to_main_app = 0x02
    is_page_blank = 0x03
    erase_user_config = 0x04
    jump_to_bootloader = 0x05
    prepare_for_firmware_update = 0x06
    ready_for_firmware_update = 0x07
    complete_firmware_update = 0x08
    firmware_update_complete = 0x09
    application_identification = 0x0a
    request_application_id = 0x0b
    set_pending_update_flags = 0x0c
    get_pending_update_flags = 0x0d
