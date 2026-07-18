"""Adaptive-trigger effects demo.

Builds effects with :class:`TriggerEffectGenerator` and applies them through the
base ``DSTrigger.setTriggerEffect``.

Every generator effect is reproduced exactly -- the mode + all 10 trigger
parameter bytes are sent as a contiguous block, so effects that use the upper
parameters (Vibration/Bow/Galloping/Machine) apply fully too.

Run with a DualSense connected over USB or Bluetooth, from a checkout::

    python examples/trigger_effects_demo.py

(or ``pip install pydualsense`` first and run it from anywhere).
"""

import os
import sys
import time

# Allow running straight from a checkout without installing the package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydualsense import pydualsense, TriggerEffectGenerator  # noqa: E402


def apply(trigger, factory, *args, **kwargs) -> None:
    """Fill an effect array with `factory` and set it on `trigger`.

    The controller's background report thread (started by ``init()``) sends the
    trigger state every cycle, so setting the object is enough -- do not call
    ``sendReport()`` from here; that method *is* the background loop and would
    trap this thread forever.
    """
    data = [0] * 11
    factory(data, 0, *args, **kwargs)
    trigger.setTriggerEffect(data)


def main() -> None:
    ds = pydualsense()
    ds.init()
    try:
        # R2: resist movement past the halfway point (Feedback).
        apply(ds.triggerR, TriggerEffectGenerator.feedback, position=5, strength=6)
        # L2: gun-trigger feel -- resist from zone 2 to 7, then release (Weapon).
        apply(ds.triggerL, TriggerEffectGenerator.weapon,
              start_position=2, end_position=7, strength=6)
        print("Feedback on R2, Weapon on L2 -- squeeze the triggers. Ctrl-C to stop.")
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for trig in (ds.triggerL, ds.triggerR):
            apply(trig, TriggerEffectGenerator.off)
        time.sleep(0.1)  # let the report thread flush the Off state
        ds.close()


if __name__ == "__main__":
    main()
