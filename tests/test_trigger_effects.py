"""Trigger-effect generator + DSTrigger.setTriggerEffect (no hardware needed)."""

import pytest

from pydualsense import DSTrigger, TriggerEffectGenerator, TriggerModes
from pydualsense.trigger_effects import TriggerEffectType


# -- generator byte layout ---------------------------------------------------
def test_off_layout():
    data = [0xFF] * 11
    assert TriggerEffectGenerator.off(data, 0) is True
    assert data[0] == TriggerEffectType.Off       # 0x05 mode byte
    assert data[1:11] == [0] * 10


def test_feedback_sets_mode_and_within_seven_params():
    data = [0] * 11
    assert TriggerEffectGenerator.feedback(data, 0, position=5, strength=6) is True
    assert data[0] == TriggerEffectType.Feedback  # 0x21
    # Feedback only fills params 0..5 (bytes 1..6); the upper params stay zero,
    # so it round-trips exactly through the 7-param report.
    assert data[7:11] == [0] * 4


def test_feedback_rejects_out_of_range():
    data = [0] * 11
    assert TriggerEffectGenerator.feedback(data, 0, position=10, strength=6) is False
    assert TriggerEffectGenerator.feedback(data, 0, position=5, strength=9) is False


def test_feedback_zero_strength_is_off():
    data = [0] * 11
    assert TriggerEffectGenerator.feedback(data, 0, position=5, strength=0) is True
    assert data[0] == TriggerEffectType.Off


# -- DSTrigger.setTriggerEffect ----------------------------------------------
def test_set_trigger_effect_maps_mode_and_forces():
    data = [0] * 11
    TriggerEffectGenerator.feedback(data, 0, position=5, strength=6)
    trig = DSTrigger()
    trig.setTriggerEffect(data)
    assert trig.mode.value == data[0]             # firmware mode byte carried
    assert trig.forces == data[1:11]              # all 10 params carried
    assert len(trig.forces) == 10


def test_set_trigger_effect_carries_upper_params():
    # Vibration puts frequency at param 9 -- previously truncated. It must now
    # survive into forces so prepareReport can send it.
    data = [0] * 11
    TriggerEffectGenerator.vibration(data, 0, position=0, amplitude=5, frequency=200)
    trig = DSTrigger()
    trig.setTriggerEffect(data)
    assert trig.forces[8] == data[9]              # frequency byte (param 9)
    assert trig.forces == data[1:11]


def test_set_trigger_effect_validates_length():
    trig = DSTrigger()
    with pytest.raises(ValueError):
        trig.setTriggerEffect([TriggerEffectType.Feedback, 0, 0])   # < 11 bytes


def test_set_trigger_effect_validates_type():
    trig = DSTrigger()
    with pytest.raises(TypeError):
        trig.setTriggerEffect("not a list")


# -- every generator mode byte resolves to a TriggerModes --------------------
@pytest.mark.parametrize("mode_byte", [m.value for m in TriggerEffectType])
def test_all_generator_modes_resolve(mode_byte):
    # setTriggerEffect does TriggerModes(effect_data[0]); it must not raise for
    # any mode a generator can emit (incl. the 0x10 "Limited" bit).
    assert TriggerModes(mode_byte).value == mode_byte
