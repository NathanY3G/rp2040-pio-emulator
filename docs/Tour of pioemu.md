# Tour of pioemu

## Introduction
Welcome to a tour of the `pioemu` library! Let's begin by exploring the example from the
[Quick Start Guide](./Quick%20Start%20Guide.md) in more depth. This example has been divided into
logical sections with an explanation added to each. The exception to this is the import statements
which have been omitted.


## PIO Program
```python
program = """
.program quickstart_example
  set x 9
loop:
  jmp x-- loop
  wait 1 gpio 0
"""
```

The example begins by defining the PIO program that is to be run as a multi-line string. This is
later converted to opcodes using [Adafruit's](https://www.adafruit.com) handy
[PIOASM](https://github.com/adafruit/Adafruit_CircuitPython_PIOASM) package. However, there is no
requirement to use this package or even to use strings - the emulator itself only uses opcodes.


### Initialization
```python
generator = emulate(assemble(program), stop_when=lambda _, state: state.x_register < 0)
```

The `emulate()` function is the main entry-point into the `pioemu` library. It effectively
configures a new instance of the emulator to run a specific PIO program. Although it supports a
number of options only two are mandatory / required:

1. PIO program - a sequence of opcodes (typically `int`'s)
2. Stop condition - a predicate function returning either `True` or `False`

At this point in the example, none of the program's instructions have been executed. The
`emulate()` function is a [generator function](https://wiki.python.org/moin/Generators) which gives
you a great detail of freedom over *when* to execute an instruction if at all!


### Main Loop
```python
for before, after in generator:
  print(f"[{after.clock}] X register: {before.x_register} -> {after.x_register}")
```

During each iteration of the example's `for` loop the next PIO instruction is emulated and a tuple
returned. This tuple contains two `pioemu.State` objects - one representing the state *before* the
instruction was executed and one *after*. These `State` objects include register values, shift
register contents, pin values and more. This approach allows you to identify what changes have
occurred. The example above simply outputs the before and after values for scratch register `X`.

The stop condition that was passed to the `emulate()` function prevents the example from looping
indefinitely. This function is called before each instruction is executed. In the example the lambda
`state.x_register < 0` returns `True` when the new value for scratch register `X` has been
decremented past zero.


### Summary
In this tour we have examined the example program from the [Quick Start Guide](./Quick%20Start%20Guide.md)
in more depth. However, if this tour was too brief or unclear for your then please consider creating
a [new issue](https://github.com/NathanY3G/rp2040-pio-emulator/issues) - thanks!
