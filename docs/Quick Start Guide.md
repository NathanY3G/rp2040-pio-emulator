# Quick Start Guide

The PIO program below counts down from nine by using the scratch register X.
It is a contrived example, however, it should offer a good starting point.

```python
program = """
.program quickstart_example
  set x 9
loop:
  jmp x-- loop
  wait 1 gpio 0
"""
```

First we need to assemble the above program. This can be done by using the [Raspberry Pi Pico SDK](https://github.com/raspberrypi/pico-sdk)
or by using [Adafruit's](https://www.adafruit.com) handy [PIOASM](https://github.com/adafruit/Adafruit_CircuitPython_PIOASM)
package. The example below uses the later.

```python
from pioemu import emulate
from adafruit_pioasm import assemble

# uses the program string from above

generator = emulate(assemble(program), stop_when=lambda _, state: state.x_register < 0)

for before, after in generator:
  print(f"[{after.clock}] X register: {before.x_register} -> {after.x_register}")
```

When run, the Python code above should produce output similar to the following:

```
[1] X register: 0 -> 9
[2] X register: 9 -> 8
[3] X register: 8 -> 7
[4] X register: 7 -> 6
[5] X register: 6 -> 5
[6] X register: 5 -> 4
[7] X register: 4 -> 3
[8] X register: 3 -> 2
[9] X register: 2 -> 1
[10] X register: 1 -> 0
[11] X register: 0 -> -1
```

NB: The above output highlights that the X register is actually decremented past
zero by the final invocation of the `jmp x--` instruction.
