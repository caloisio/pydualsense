from enum import IntFlag


class ConnectionType(IntFlag):
    BT = 0x0
    USB = 0x1
    ERROR = 0xFF


class LedOptions(IntFlag):
    Off = 0x0
    PlayerLedBrightness = 0x1
    UninterrumpableLed = 0x2
    Both = 0x01 | 0x02


class PulseOptions(IntFlag):
    Off = 0x0
    FadeBlue = 0x1
    FadeOut = 0x2


class Brightness(IntFlag):
    high = 0x0
    medium = 0x1
    low = 0x2


class PlayerID(IntFlag):
    PLAYER_1 = 4
    PLAYER_2 = 10
    PLAYER_3 = 21
    PLAYER_4 = 27
    ALL = 31


class TriggerModes(IntFlag):
    Off = 0x0  # no resistance
    Rigid = 0x1  # continous resistance
    Pulse = 0x2  # section resistance
    Rigid_A = 0x1 | 0x20
    Rigid_B = 0x1 | 0x04
    Rigid_AB = 0x1 | 0x20 | 0x04
    Pulse_A = 0x2 | 0x20
    Pulse_B = 0x2 | 0x04
    Pulse_AB = 0x2 | 0x20 | 0x04
    Calibration = 0xFC

    # Adaptive-trigger "effect" mode bytes used by the zone-packed effects in
    # `pydualsense.trigger_effects` (a port of Nielk1's TriggerEffectGenerator).
    # These are the raw firmware mode values; several overlap the Rigid/Pulse bit
    # combos above and so become aliases. They are declared here so that
    # `TriggerModes(effect_data[0])` -- used by `DSTrigger.setTriggerEffect` --
    # always resolves, including the 0x10 "Limited" bit that no other member owns.
    Feedback = 0x21
    Weapon = 0x25
    Vibration = 0x26
    Bow = 0x22
    Galloping = 0x23
    Machine = 0x27
    Effect_Off = 0x05          # generator "off" mode byte (distinct from Off = 0x0)
    Simple_Feedback = 0x01     # alias of Rigid
    Simple_Weapon = 0x02       # alias of Pulse
    Simple_Vibration = 0x06
    Limited_Feedback = 0x11
    Limited_Weapon = 0x12


class BatteryState(IntFlag):
    POWER_SUPPLY_STATUS_DISCHARGING = 0x0
    POWER_SUPPLY_STATUS_CHARGING = 0x1
    POWER_SUPPLY_STATUS_FULL = 0x2
    POWER_SUPPLY_STATUS_NOT_CHARGING = 0xB
    POWER_SUPPLY_STATUS_ERROR = 0xF
    POWER_SUPPLY_TEMP_OR_VOLTAGE_OUT_OF_RANGE = 0xA
    POWER_SUPPLY_STATUS_UNKNOWN = 0x0
