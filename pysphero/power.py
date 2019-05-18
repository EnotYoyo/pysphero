from enum import Enum

from pysphero.device_api import DeviceApiABC, DeviceId
from pysphero.helpers import UnknownEnumMixing


class BatteryVoltageStates(UnknownEnumMixing, Enum):
    ok = 0x01
    low = 0x02
    critical = 0x03


class ChargerStates(UnknownEnumMixing, Enum):
    not_charging = 0x01
    charging = 0x02
    charged = 0x03


class PowerCommand(Enum):
    enter_deep_sleep = 0x00
    enter_soft_sleep = 0x01
    get_usb_state = 0x02
    get_battery_voltage = 0x03
    # get_battery_state = 0x04  # old? value from Core library
    enable_battery_state_change_notification = 0x05
    # battery_state_changed = 0x06  # old? value from Core library
    wake = 0x0d
    get_battery_percentage = 0x10
    set_power_options = 0x12
    get_power_options = 0x13
    get_battery_state = 0x17
    will_sleep_async = 0x19
    sleep_async = 0x1a
    battery_state_changed = 0x1f


class Power(DeviceApiABC):
    device_id = DeviceId.power

    def enter_deep_sleep(self):
        """
        Send shutdown command to toy

        :return None:
        """

        self.request(PowerCommand.enter_deep_sleep)

    def enter_soft_sleep(self):
        """
        Send sleep command to toy (normal condition of toy)

        :return None:
        """

        self.request(PowerCommand.enter_soft_sleep)

    def get_battery_voltage(self) -> float:
        """
        Returns battery voltage. Allows to determine the level of charge

        :float return: battery voltage in volts
        """

        response = self.request(PowerCommand.get_battery_voltage)
        return int.from_bytes(response.data, "big") / 100

    def wake(self):
        """
        Wake up toys

        :return None:
        """

        self.request(PowerCommand.wake)

    def get_battery_state(self) -> BatteryVoltageStates:
        """
        Get battery state without known voltage constants

        :return BatteryVoltageStates:
        """

        response = self.request(PowerCommand.get_battery_state)
        return BatteryVoltageStates(response.data[0])

    def battery_state_changed(self) -> ChargerStates:
        """
        Charging status information

        :return ChargerStates:
        """

        response = self.request(PowerCommand.battery_state_changed)
        return ChargerStates(response.data[0])
