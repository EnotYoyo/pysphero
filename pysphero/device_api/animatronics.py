import struct
import time
from enum import Enum
from typing import Optional, List

from pysphero.helpers import float_from_bytes
from pysphero.packet import Packet

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

class AnimatronicsLMQCommand(Enum):
    animate_eyes = 0x01
    animate_suspension = 0x03
    animate_mouth = 0x04
    execute_animation_profile = 0x05
    upload_animation_bundle = 0x06
    capacitive_touch_indication = 0x07
    upload_animation_bundle_result = 0x09
    enable_idle_animation = 0x0a
    enable_user_drive = 0x0b
    do_shoulder_action = 0x0d
    set_head_position = 0x0f
    execute_animation_bundle_complete = 0x11
    animate_steering = 0x12
    animation_upload_process_complete = 0x13
    get_head_position = 0x14
    set_shoulder_cam_position = 0x15
    get_shoulder_cam_position = 0x16
    set_shoulder_action = 0x25
    shoulder_action_complete = 0x26
    enable_shoulder_action_complete = 0x2a
    stop_animation = 0x2b

# ALL LMQUXXX have been found like that, sentences written are the french one
# will switch my device to english to provide the proper sentence, but if someone could
# do it will help.
class LMQAnimation(Enum):
    Oh_yeah_Lightning_is_ready_LMQ007 = 0x24
    Bien_joue_LMQU006 = 0x26
    Cool_LMQ012 = 0x28
    Thank_you_LMQ016 = 0x2b
    C_est_quoi_cette_odeur = 0x30 #Trig a force awareness async notif
    This_is_amazing_LMQ024 = 0x32
    Whoa_LMQ177 = 0x33
    Hey_c_mon_let_s_go_LMQ028 = 0x36
    Have_I_mentioned_that_I_love_your_garage_LMQ031 = 0x39
    Look_out_folks_Lightning_McQueen_is_back_LMQ039 = 0x3f
    I_am_so_ready_for_the_Piston_Cup_LMQ044 = 0x41
    Look_left_look_right_Yep_nothing_but_open_road_LMQ062 = 0x4e
    My_buddy_Filmore_makes_the_best_organic_fuel_in_the_world_loads_of_power_and_a_clean_burn_LMQ067 = 0x52
    The_road_is_calling_my_name_Hear_it_Lightning_oh_Lightning_LMQ069 = 0x54
    I_am_speed_LMQ432 = 0x5e  # je suis rapide
    I_ve_been_all_over_the_world_and_I_can_honestly_say_that_Flo_s_V_8_Cafe_serves_the_best_quart_of_oil_anywhere_LMQ074 = 0x58
    Crank_the_acceleration_LMQ083 = 0x59
    Focus_focus_LMQ089 = 0x5f
    The_crowd_loves_us_LMQ100 = 0x64
    Game_on_LMQ105 = 0x66
    Next_up_Lightning_McQueen_LMQ108 = 0x67
    Ka_Chow_LMQ113 = 0x69
    Yes_woo_LMQ116 = 0x6c
    Pay_attention_this_is_how_it_s_done_LMQ143 = 0x7b
    Je_suis_Flash_Mcqueen_LMQU008 = 0x7e
    Wow_LMQ025 = 0x82
    Ho_oui_Flash_Mcqueen_est_dans_la_place_LMQU003 = 0x8d
    Hey_LMQ237 = 0x9f
    Here_I_go_LMQ238 = 0xa0
    Woo_hoo_LMQ241 = 0xa2
    Ah_serieux_on_devrait_essayer_autre_chose_LMQU005 = 0xcd
    Ahhh_LMQ379 = 0xdc
    Tu_maitrises_mon_ami_LMQU010 = 0xce
    Gasp_LMQ403 = 0xf2
    Je_n_ai_jamais_ete_aussi_bien_prepare_LMQU009 = 0xf5
    Ah_Quels_souvenirs_LMQU007 = 0xf6
    J_adore_quand_elles_m_appellent_chouchou_LMQ008 = 0xfe
    Watch_this_I_call_it_The_Wave_LMQ431 = 0x107
    Groovin_LMQ457 = 0x111
    Watch_me_now_LMQ458 = 0x112
    Entendu_allons_y_je_veux_bien_passer_devant_la_camera_LMQU001 = 0x126
    Etre_un_champion_repose_sur_le_travail_d_equipe_ce_qui_implique_d_avoir_un_stand_de_ravitaillement_d_execption_LMQU002 = 0x128
    Je_suis_super_rapide_LMQU004 = 0x12c
    I_m_a_precision_instrument_of_speed_and_aerodynamics_LMQ433 = 0x12d
    Ahh_c_mon_LMQ125 = 0x12f
    Engine_Rev_LMQ_Start_2 = 0x130
    Engine_Start_LMQ_Start_3 = 0x131
    Engine_Idle_LMQ_Idle_Loop = 0x132

    # sentence in the app that not captured yet.
    # Woooo_Woo_What_a_blast_LMQ041 =
    # When_it_comes_to_medicated_bumper_ointment_Rust-eze_is_the_only_brand_I_trust_LMQ073 =
    # Dahh_LMQ394 =


class Animatronics(DeviceApiABC):
    device_id = DeviceId.animatronics

    def __init__(self, ble_adapter):
        super().__init__(ble_adapter)
        self._wait_for_play_animation = False
        self._animation: Optional[List[int]] = None

    def play_animation(self, animation_id: int, target_id=0x12):
        self.request(
            AnimatronicsCommand.play_animation,
            data=[*animation_id.to_bytes(2, "big")],
            target_id=target_id,
        )

    def play_animation_and_wait(self, animation_id: int, target_id=0x12, timeout: float = 10):
        self._animation = [*animation_id.to_bytes(2, "big")]
        self._wait_for_play_animation = True

        def callback_wrapper(response: Packet):
            if response.data == self._animation:
                self._wait_for_play_animation = False

        self.notify(AnimatronicsCommand.play_animation_complete_notify, callback_wrapper, timeout=timeout)
        self.request(
            AnimatronicsCommand.play_animation,
            data=self._animation,
            target_id=target_id,
        )

        sleep_time = 0.1
        while self._wait_for_play_animation:
            timeout -= sleep_time
            if timeout <= 0:
                self._wait_for_play_animation = False
            time.sleep(sleep_time)

        self.cancel_notify()

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
