"""
DualSense Trigger Effect Generator for Python

Converted from C# TriggerEffectGenerator.cs by John "Nielk1" Klein
Original MIT License preserved.

This module provides functions to generate adaptive trigger effect data
for Sony DualSense controllers. Effects can be applied to create various
haptic feedback sensations on the L2/R2 triggers.

Usage:
    effect_data = [0] * 11
    TriggerEffectGenerator.feedback(effect_data, 0, position=5, strength=6)
    # Apply effect_data to controller trigger
"""

from enum import IntEnum
from typing import List


class TriggerEffectType(IntEnum):
    """
    Actual effect byte values sent to the controller.
    More complex effects may be built through the combination of these values and specific parameters.
    """
    # Officially recognized modes
    Off       = 0x05  # 00 00 0 101
    Feedback  = 0x21  # 00 10 0 001
    Weapon    = 0x25  # 00 10 0 101
    Vibration = 0x26  # 00 10 0 110

    # Unofficial but unique effects left in the firmware
    Bow       = 0x22  # 00 10 0 010
    Galloping = 0x23  # 00 10 0 011
    Machine   = 0x27  # 00 10 0 111

    # Leftover versions of official modes with simpler logic
    Simple_Feedback  = 0x01  # 00 00 0 001
    Simple_Weapon    = 0x02  # 00 00 0 010
    Simple_Vibration = 0x06  # 00 00 0 110

    # Leftover versions of official modes with limited parameter ranges
    Limited_Feedback = 0x11  # 00 01 0 001
    Limited_Weapon   = 0x12  # 00 01 0 010


class TriggerEffectGenerator:
    """
    DualSense controller trigger effect generators.
    
    All effect factories return True on success and False on failure.
    If parameters would result in zero effect, the Off effect is applied instead.
    """

    # ========== Official Effects ==========
    
    @staticmethod
    def off(destination: List[int], index: int = 0) -> bool:
        """
        Turn the trigger effect off and return the trigger stop to neutral position.
        This is an official effect expected to be present in future DualSense firmware.
        
        Args:
            destination: The list that receives the data (must have at least index+11 elements)
            index: Index in the destination list where storing begins (default: 0)
            
        Returns:
            True on success
        """
        destination[index + 0] = TriggerEffectType.Off
        for i in range(1, 11):
            destination[index + i] = 0x00
        return True

    @staticmethod
    def feedback(destination: List[int], index: int = 0, position: int = 0, strength: int = 0) -> bool:
        """
        Trigger will resist movement beyond the start position.
        The trigger status will report 0 before effect and 1 when in effect.
        This is an official effect expected to be present in future DualSense firmware.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            position: Starting zone of trigger effect (0-9 inclusive)
            strength: Force of resistance (0-8 inclusive, 0=off)
            
        Returns:
            True on success, False if parameters are invalid
        """
        if position > 9:
            return False
        if strength > 8:
            return False
        
        if strength > 0:
            force_value = (strength - 1) & 0x07
            force_zones = 0
            active_zones = 0
            
            for i in range(position, 10):
                force_zones |= (force_value << (3 * i))
                active_zones |= (1 << i)
            
            destination[index + 0] = TriggerEffectType.Feedback
            destination[index + 1] = (active_zones >> 0) & 0xFF
            destination[index + 2] = (active_zones >> 8) & 0xFF
            destination[index + 3] = (force_zones >> 0) & 0xFF
            destination[index + 4] = (force_zones >> 8) & 0xFF
            destination[index + 5] = (force_zones >> 16) & 0xFF
            destination[index + 6] = (force_zones >> 24) & 0xFF
            destination[index + 7] = 0x00
            destination[index + 8] = 0x00
            destination[index + 9] = 0x00
            destination[index + 10] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)

    @staticmethod
    def weapon(destination: List[int], index: int = 0, start_position: int = 2, 
               end_position: int = 7, strength: int = 0) -> bool:
        """
        Trigger will resist movement beyond start position until end position.
        The trigger status will report 0 before effect, 1 when in effect, 
        and 2 after until again before start position.
        This is an official effect expected to be present in future DualSense firmware.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            start_position: Starting zone of trigger effect (2-7 inclusive)
            end_position: Ending zone of trigger effect (start_position+1 to 8 inclusive)
            strength: Force of resistance (0-8 inclusive, 0=off)
            
        Returns:
            True on success, False if parameters are invalid
        """
        if start_position > 7 or start_position < 2:
            return False
        if end_position > 8:
            return False
        if end_position <= start_position:
            return False
        if strength > 8:
            return False
        
        if strength > 0:
            start_stop_zones = (1 << start_position) | (1 << end_position)
            
            destination[index + 0] = TriggerEffectType.Weapon
            destination[index + 1] = (start_stop_zones >> 0) & 0xFF
            destination[index + 2] = (start_stop_zones >> 8) & 0xFF
            destination[index + 3] = strength - 1
            destination[index + 4] = 0x00
            destination[index + 5] = 0x00
            destination[index + 6] = 0x00
            destination[index + 7] = 0x00
            destination[index + 8] = 0x00
            destination[index + 9] = 0x00
            destination[index + 10] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)

    @staticmethod
    def vibration(destination: List[int], index: int = 0, position: int = 0, 
                  amplitude: int = 0, frequency: int = 0) -> bool:
        """
        Trigger will vibrate with the input amplitude and frequency beyond start position.
        The trigger status will report 0 before effect and 1 when in effect.
        This is an official effect expected to be present in future DualSense firmware.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            position: Starting zone of trigger effect (0-9 inclusive)
            amplitude: Strength of automatic cycling action (0-8 inclusive, 0=off)
            frequency: Frequency of automatic cycling action in Hz (0-255)
            
        Returns:
            True on success, False if parameters are invalid
        """
        if position > 9:
            return False
        if amplitude > 8:
            return False
        
        if amplitude > 0 and frequency > 0:
            strength_value = (amplitude - 1) & 0x07
            amplitude_zones = 0
            active_zones = 0
            
            for i in range(position, 10):
                amplitude_zones |= (strength_value << (3 * i))
                active_zones |= (1 << i)
            
            destination[index + 0] = TriggerEffectType.Vibration
            destination[index + 1] = (active_zones >> 0) & 0xFF
            destination[index + 2] = (active_zones >> 8) & 0xFF
            destination[index + 3] = (amplitude_zones >> 0) & 0xFF
            destination[index + 4] = (amplitude_zones >> 8) & 0xFF
            destination[index + 5] = (amplitude_zones >> 16) & 0xFF
            destination[index + 6] = (amplitude_zones >> 24) & 0xFF
            destination[index + 7] = 0x00
            destination[index + 8] = 0x00
            destination[index + 9] = frequency
            destination[index + 10] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)

    @staticmethod
    def multiple_position_feedback(destination: List[int], index: int = 0, 
                                   strength: List[int] = None) -> bool:
        """
        Trigger will resist movement at varying strengths in 10 regions.
        This is an official effect expected to be present in future DualSense firmware.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            strength: Array of 10 resistance values for zones 0-9 (0-8 inclusive each)
            
        Returns:
            True on success, False if parameters are invalid
        """
        if strength is None or len(strength) != 10:
            return False
        
        if any(s > 0 for s in strength):
            force_zones = 0
            active_zones = 0
            
            for i in range(10):
                if strength[i] > 0:
                    force_value = (strength[i] - 1) & 0x07
                    force_zones |= (force_value << (3 * i))
                    active_zones |= (1 << i)
            
            destination[index + 0] = TriggerEffectType.Feedback
            destination[index + 1] = (active_zones >> 0) & 0xFF
            destination[index + 2] = (active_zones >> 8) & 0xFF
            destination[index + 3] = (force_zones >> 0) & 0xFF
            destination[index + 4] = (force_zones >> 8) & 0xFF
            destination[index + 5] = (force_zones >> 16) & 0xFF
            destination[index + 6] = (force_zones >> 24) & 0xFF
            destination[index + 7] = 0x00
            destination[index + 8] = 0x00
            destination[index + 9] = 0x00
            destination[index + 10] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)

    @staticmethod
    def slope_feedback(destination: List[int], index: int = 0, start_position: int = 0,
                      end_position: int = 9, start_strength: int = 1, end_strength: int = 8) -> bool:
        """
        Trigger will resist movement at a linear range of strengths.
        This is an official effect expected to be present in future DualSense firmware.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            start_position: Starting zone of trigger effect (0-8 inclusive)
            end_position: Ending zone of trigger effect (start_position+1 to 9 inclusive)
            start_strength: Force of resistance at start (1-8 inclusive)
            end_strength: Force of resistance at end (1-8 inclusive)
            
        Returns:
            True on success, False if parameters are invalid
        """
        if start_position > 8 or start_position < 0:
            return False
        if end_position > 9:
            return False
        if end_position <= start_position:
            return False
        if start_strength > 8 or start_strength < 1:
            return False
        if end_strength > 8 or end_strength < 1:
            return False
        
        strength = [0] * 10
        slope = (end_strength - start_strength) / (end_position - start_position)
        
        for i in range(start_position, 10):
            if i <= end_position:
                strength[i] = round(start_strength + slope * (i - start_position))
            else:
                strength[i] = end_strength
        
        return TriggerEffectGenerator.multiple_position_feedback(destination, index, strength)

    @staticmethod
    def multiple_position_vibration(destination: List[int], index: int = 0, 
                                   frequency: int = 0, amplitude: List[int] = None) -> bool:
        """
        Trigger will vibrate at varying amplitudes and one frequency in 10 regions.
        This is an official effect expected to be present in future DualSense firmware.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            frequency: Frequency of automatic cycling action in Hz (0-255)
            amplitude: Array of 10 strength values for zones 0-9 (0-8 inclusive each)
            
        Returns:
            True on success, False if parameters are invalid
        """
        if amplitude is None or len(amplitude) != 10:
            return False
        
        if frequency > 0 and any(a > 0 for a in amplitude):
            strength_zones = 0
            active_zones = 0
            
            for i in range(10):
                if amplitude[i] > 0:
                    strength_value = (amplitude[i] - 1) & 0x07
                    strength_zones |= (strength_value << (3 * i))
                    active_zones |= (1 << i)
            
            destination[index + 0] = TriggerEffectType.Vibration
            destination[index + 1] = (active_zones >> 0) & 0xFF
            destination[index + 2] = (active_zones >> 8) & 0xFF
            destination[index + 3] = (strength_zones >> 0) & 0xFF
            destination[index + 4] = (strength_zones >> 8) & 0xFF
            destination[index + 5] = (strength_zones >> 16) & 0xFF
            destination[index + 6] = (strength_zones >> 24) & 0xFF
            destination[index + 7] = 0x00
            destination[index + 8] = 0x00
            destination[index + 9] = frequency
            destination[index + 10] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)

    # ========== Unofficial but Unique Effects ==========
    
    @staticmethod
    def bow(destination: List[int], index: int = 0, start_position: int = 0,
            end_position: int = 8, strength: int = 0, snap_force: int = 0) -> bool:
        """
        Effect resembles Weapon but with snap-back force that attempts to reset the trigger.
        This is NOT an official effect and may be removed in future DualSense firmware.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            start_position: Starting zone of trigger effect (0-8 inclusive)
            end_position: Ending zone of trigger effect (start_position+1 to 8 inclusive)
            strength: Force of resistance (0-8 inclusive, 0=off)
            snap_force: Force of snap-back (0-8 inclusive, 0=off)
            
        Returns:
            True on success, False if parameters are invalid
        """
        if start_position > 8:
            return False
        if end_position > 8:
            return False
        if start_position >= end_position:
            return False
        if strength > 8:
            return False
        if snap_force > 8:
            return False
        
        if end_position > 0 and strength > 0 and snap_force > 0:
            start_stop_zones = (1 << start_position) | (1 << end_position)
            force_pair = (((strength - 1) & 0x07) << 0) | (((snap_force - 1) & 0x07) << 3)
            
            destination[index + 0] = TriggerEffectType.Bow
            destination[index + 1] = (start_stop_zones >> 0) & 0xFF
            destination[index + 2] = (start_stop_zones >> 8) & 0xFF
            destination[index + 3] = (force_pair >> 0) & 0xFF
            destination[index + 4] = (force_pair >> 8) & 0xFF
            destination[index + 5] = 0x00
            destination[index + 6] = 0x00
            destination[index + 7] = 0x00
            destination[index + 8] = 0x00
            destination[index + 9] = 0x00
            destination[index + 10] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)

    @staticmethod
    def galloping(destination: List[int], index: int = 0, start_position: int = 0,
                 end_position: int = 9, first_foot: int = 0, second_foot: int = 7, 
                 frequency: int = 0) -> bool:
        """
        Trigger will oscillate in a rhythmic pattern resembling galloping.
        Effect is only discernible at low frequency values.
        This is NOT an official effect and may be removed in future DualSense firmware.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            start_position: Starting zone of trigger effect (0-8 inclusive)
            end_position: Ending zone of trigger effect (start_position+1 to 9 inclusive)
            first_foot: Position of first foot in cycle (0-6 inclusive)
            second_foot: Position of second foot in cycle (first_foot+1 to 7 inclusive)
            frequency: Frequency of automatic cycling action in Hz (0-255)
            
        Returns:
            True on success, False if parameters are invalid
        """
        if start_position > 8:
            return False
        if end_position > 9:
            return False
        if start_position >= end_position:
            return False
        if second_foot > 7:
            return False
        if first_foot > 6:
            return False
        if first_foot >= second_foot:
            return False
        
        if frequency > 0:
            start_stop_zones = (1 << start_position) | (1 << end_position)
            time_and_ratio = ((second_foot & 0x07) << 0) | ((first_foot & 0x07) << 3)
            
            destination[index + 0] = TriggerEffectType.Galloping
            destination[index + 1] = (start_stop_zones >> 0) & 0xFF
            destination[index + 2] = (start_stop_zones >> 8) & 0xFF
            destination[index + 3] = (time_and_ratio >> 0) & 0xFF
            destination[index + 4] = frequency
            destination[index + 5] = 0x00
            destination[index + 6] = 0x00
            destination[index + 7] = 0x00
            destination[index + 8] = 0x00
            destination[index + 9] = 0x00
            destination[index + 10] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)

    @staticmethod
    def machine(destination: List[int], index: int = 0, start_position: int = 0,
               end_position: int = 9, amplitude_a: int = 0, amplitude_b: int = 0,
               frequency: int = 0, period: int = 0) -> bool:
        """
        Effect resembles Vibration but oscillates between two amplitudes.
        This is NOT an official effect and may be removed in future DualSense firmware.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            start_position: Starting zone of trigger effect (0-8 inclusive)
            end_position: Ending zone of trigger effect (start_position to 9 inclusive)
            amplitude_a: Primary strength of cycling action (0-7 inclusive)
            amplitude_b: Secondary strength of cycling action (0-7 inclusive)
            frequency: Frequency of automatic cycling action in Hz (0-255)
            period: Period of oscillation between amplitudes in tenths of a second
            
        Returns:
            True on success, False if parameters are invalid
        """
        if start_position > 8:
            return False
        if end_position > 9:
            return False
        if end_position <= start_position:
            return False
        if amplitude_a > 7:
            return False
        if amplitude_b > 7:
            return False
        
        if frequency > 0:
            start_stop_zones = (1 << start_position) | (1 << end_position)
            strength_pair = ((amplitude_a & 0x07) << 0) | ((amplitude_b & 0x07) << 3)
            
            destination[index + 0] = TriggerEffectType.Machine
            destination[index + 1] = (start_stop_zones >> 0) & 0xFF
            destination[index + 2] = (start_stop_zones >> 8) & 0xFF
            destination[index + 3] = (strength_pair >> 0) & 0xFF
            destination[index + 4] = frequency
            destination[index + 5] = period
            destination[index + 6] = 0x00
            destination[index + 7] = 0x00
            destination[index + 8] = 0x00
            destination[index + 9] = 0x00
            destination[index + 10] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)

    # ========== Simple Effects (Not recommended, use official versions) ==========
    
    @staticmethod
    def simple_feedback(destination: List[int], index: int = 0, position: int = 0, 
                       strength: int = 0) -> bool:
        """
        Simplistic Feedback effect data generator.
        NOT recommended - use feedback() instead. May be removed in future firmware.
        """
        destination[index + 0] = TriggerEffectType.Simple_Feedback
        destination[index + 1] = position
        destination[index + 2] = strength
        for i in range(3, 11):
            destination[index + i] = 0x00
        return True

    @staticmethod
    def simple_weapon(destination: List[int], index: int = 0, start_position: int = 0,
                     end_position: int = 0, strength: int = 0) -> bool:
        """
        Simplistic Weapon effect data generator.
        NOT recommended - use weapon() instead. May be removed in future firmware.
        """
        destination[index + 0] = TriggerEffectType.Simple_Weapon
        destination[index + 1] = start_position
        destination[index + 2] = end_position
        destination[index + 3] = strength
        for i in range(4, 11):
            destination[index + i] = 0x00
        return True

    @staticmethod
    def simple_vibration(destination: List[int], index: int = 0, position: int = 0,
                        amplitude: int = 0, frequency: int = 0) -> bool:
        """
        Simplistic Vibration effect data generator.
        NOT recommended - use vibration() instead. May be removed in future firmware.
        """
        if frequency > 0 and amplitude > 0:
            destination[index + 0] = TriggerEffectType.Simple_Vibration
            destination[index + 1] = frequency
            destination[index + 2] = amplitude
            destination[index + 3] = position
            for i in range(4, 11):
                destination[index + i] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)

    # ========== Limited Effects (Not recommended, use official versions) ==========
    
    @staticmethod
    def limited_feedback(destination: List[int], index: int = 0, position: int = 0,
                        strength: int = 0) -> bool:
        """
        Simplistic Feedback with stricter parameter limits.
        NOT recommended - use feedback() instead. May be removed in future firmware.
        """
        if strength > 10:
            return False
        
        if strength > 0:
            destination[index + 0] = TriggerEffectType.Limited_Feedback
            destination[index + 1] = position
            destination[index + 2] = strength
            for i in range(3, 11):
                destination[index + i] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)

    @staticmethod
    def limited_weapon(destination: List[int], index: int = 0, start_position: int = 0x10,
                      end_position: int = 0x10, strength: int = 0) -> bool:
        """
        Simplistic Weapon with stricter parameter limits.
        NOT recommended - use weapon() instead. May be removed in future firmware.
        """
        if start_position < 0x10:
            return False
        if end_position < start_position or (start_position + 100) < end_position:
            return False
        if strength > 10:
            return False
        
        if strength > 0:
            destination[index + 0] = TriggerEffectType.Limited_Weapon
            destination[index + 1] = start_position
            destination[index + 2] = end_position
            destination[index + 3] = strength
            for i in range(4, 11):
                destination[index + i] = 0x00
            return True
        
        return TriggerEffectGenerator.off(destination, index)


# Convenience wrapper for Apple-style API (mimics GCDualSenseAdaptiveTrigger)
class AppleStyleTriggerEffects:
    """
    Interface adapters patterned after Apple's GCDualSenseAdaptiveTrigger class.
    All position, strength, and amplitude parameters are normalized floats [0-1].
    """
    
    @staticmethod
    def set_mode_off(destination: List[int], index: int = 0) -> bool:
        """Turn off the adaptive trigger effect."""
        return TriggerEffectGenerator.off(destination, index)
    
    @staticmethod
    def set_mode_feedback_with_start_position(destination: List[int], index: int = 0,
                                             start_position: float = 0.0, 
                                             resistive_strength: float = 0.0) -> bool:
        """
        Sets adaptive trigger to feedback mode.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            start_position: Normalized float [0-1] for trigger depression
            resistive_strength: Normalized float [0-1] for effect strength
        """
        pos = round(start_position * 9.0)
        strength = round(resistive_strength * 8.0)
        return TriggerEffectGenerator.feedback(destination, index, int(pos), int(strength))
    
    @staticmethod
    def set_mode_weapon_with_start_position(destination: List[int], index: int = 0,
                                           start_position: float = 0.0,
                                           end_position: float = 1.0,
                                           resistive_strength: float = 0.0) -> bool:
        """
        Sets adaptive trigger to weapon mode.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            start_position: Normalized float [0-1] for trigger depression
            end_position: Normalized float [0-1] for trigger depression (must be > start_position)
            resistive_strength: Normalized float [0-1] for effect strength
        """
        start_pos = round(start_position * 9.0)
        end_pos = round(end_position * 9.0)
        strength = round(resistive_strength * 8.0)
        return TriggerEffectGenerator.weapon(destination, index, int(start_pos), 
                                            int(end_pos), int(strength))
    
    @staticmethod
    def set_mode_vibration_with_start_position(destination: List[int], index: int = 0,
                                              start_position: float = 0.0,
                                              amplitude: float = 0.0,
                                              frequency: float = 0.0) -> bool:
        """
        Sets adaptive trigger to vibration mode.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            start_position: Normalized float [0-1] for trigger depression
            amplitude: Normalized float [0-1] for effect strength
            frequency: Normalized float [0-1] for vibration frequency
        """
        pos = round(start_position * 9.0)
        amp = round(amplitude * 8.0)
        freq = round(frequency * 255.0)
        return TriggerEffectGenerator.vibration(destination, index, int(pos), 
                                               int(amp), int(freq))
    
    @staticmethod
    def set_mode_slope_feedback(destination: List[int], index: int = 0,
                               start_position: float = 0.0,
                               end_position: float = 1.0,
                               start_strength: float = 0.125,
                               end_strength: float = 1.0) -> bool:
        """
        Sets adaptive trigger to feedback mode with strength slope.
        
        Args:
            destination: The list that receives the data
            index: Index in destination list where storing begins
            start_position: Normalized float [0-1] for trigger depression
            end_position: Normalized float [0-1] for trigger depression (must be > start_position)
            start_strength: Normalized float [0-1] for initial effect strength
            end_strength: Normalized float [0-1] for final effect strength
        """
        start_pos = round(start_position * 9.0)
        end_pos = round(end_position * 9.0)
        start_str = round(start_strength * 8.0)
        end_str = round(end_strength * 8.0)
        return TriggerEffectGenerator.slope_feedback(destination, index, int(start_pos),
                                                     int(end_pos), int(start_str), int(end_str))
