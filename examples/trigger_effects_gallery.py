"""Interactive adaptive-trigger effect gallery.

Walks every :class:`TriggerEffectGenerator` effect, applying each to **both**
triggers so you can feel it. Squeeze L2/R2, press Enter for the next effect,
``q`` + Enter to quit. The trigger is set back to Off on exit.

Run with a DualSense connected over USB or Bluetooth, from a checkout::

    python examples/trigger_effects_gallery.py

(or ``pip install pydualsense`` first and run it from anywhere).
"""

import os
import sys
import time

# Allow running straight from a checkout without installing the package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydualsense import pydualsense, TriggerEffectGenerator as G  # noqa: E402


def apply(trigger, factory, **kwargs):
    """Fill an 11-byte effect array with `factory` and set it on `trigger`.

    The controller's background report thread (started by ``init()``) sends the
    trigger state every cycle, so setting the object is enough -- do not call
    ``sendReport()`` from here; that method *is* the background loop and would
    trap this thread forever.
    """
    data = [0] * 11
    ok = factory(data, 0, **kwargs)
    trigger.setTriggerEffect(data)
    return ok, data


# (label, factory, kwargs). Params chosen to be clearly feelable.
EFFECTS = [
    ("feedback  - resist past zone 5",
     G.feedback, dict(position=5, strength=6)),
    ("weapon    - gun trigger, resist zone 2..7 then release",
     G.weapon, dict(start_position=2, end_position=7, strength=8)),
    ("vibration - buzz past zone 0 @ 40Hz  (uses upper param 9)",
     G.vibration, dict(position=0, amplitude=7, frequency=40)),
    ("multiple_position_feedback - rising wall of resistance",
     G.multiple_position_feedback, dict(strength=[0, 1, 2, 3, 4, 5, 6, 7, 8, 8])),
    ("slope_feedback - linear ramp of resistance",
     G.slope_feedback, dict(start_position=0, end_position=9,
                            start_strength=1, end_strength=8)),
    ("multiple_position_vibration - buzz pattern @ 40Hz",
     G.multiple_position_vibration, dict(frequency=40,
                                         amplitude=[0, 2, 4, 6, 8, 8, 6, 4, 2, 0])),
    ("bow       - resist zone 1..6 with snap-back  (unofficial)",
     G.bow, dict(start_position=1, end_position=6, strength=6, snap_force=6)),
    ("galloping - rhythmic oscillation @ 8Hz  (unofficial)",
     G.galloping, dict(start_position=0, end_position=9,
                       first_foot=2, second_foot=5, frequency=8)),
    ("machine   - two-amplitude buzz @ 25Hz  (unofficial)",
     G.machine, dict(start_position=1, end_position=9, amplitude_a=2,
                     amplitude_b=7, frequency=25, period=4)),
    ("simple_feedback  - leftover simple resistance",
     G.simple_feedback, dict(position=5, strength=6)),
    ("simple_weapon    - leftover simple gun trigger",
     G.simple_weapon, dict(start_position=2, end_position=7, strength=6)),
    ("simple_vibration - leftover simple buzz @ 40Hz",
     G.simple_vibration, dict(position=0, amplitude=6, frequency=40)),
    ("limited_feedback - stricter simple resistance",
     G.limited_feedback, dict(position=5, strength=6)),
    ("limited_weapon   - stricter simple gun trigger",
     G.limited_weapon, dict(start_position=0x10, end_position=0x20, strength=6)),
]


def main():
    ds = pydualsense()
    ds.init()
    print(f"connected ({ds.conType.name}). {len(EFFECTS)} effects. "
          "Enter = next, q + Enter = quit.\n")
    try:
        for i, (label, factory, kwargs) in enumerate(EFFECTS, 1):
            ok, data = apply(ds.triggerR, factory, **kwargs)
            apply(ds.triggerL, factory, **kwargs)
            print(f"[{i:2}/{len(EFFECTS)}] {label}")
            print(f"        mode=0x{data[0]:02x} bytes={data}  ok={ok}")
            if input("        > ").strip().lower() == "q":
                break
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        for trig in (ds.triggerL, ds.triggerR):
            apply(trig, G.off)
        time.sleep(0.1)  # let the report thread flush the Off state
        ds.close()
        print("\neffects off. done.")


if __name__ == "__main__":
    main()
