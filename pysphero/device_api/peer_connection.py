from enum import Enum


class PeerConnectionCommand(Enum):
    enable_peer_connection_event_notification = 0x00
    peer_connection_event = 0x01
    get_peer_connection_state = 0x02
    set_bluetooth_name = 0x03
    get_bluetooth_name = 0x04
