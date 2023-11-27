# (In)Frequently Asked Questions

## How can incoming signals be modelled?

The `emulate()` function takes an optional `input_source` parameter to a
function or other callable object. This will be invoked before each instruction
and is expected to return the values that are present on _all_ of the GPIO pins
at that time. The example below toggles the value present on GPIO pin 0 with
each clock cycle.

```python
from pioemu import emulate

program = [0xA020]  # mov pins, x

def incoming_signals(clock: int) -> int:
    return 1 - (clock % 2)  # Toggle the value present on GPIO 0

for before, after in emulate(
    program, input_source=incoming_signals, stop_when=lambda _, state: state.clock > 3
):
    print(f"[{after.clock}] GPIO: {before.pin_values:b} -> {after.pin_values:b}")
```
