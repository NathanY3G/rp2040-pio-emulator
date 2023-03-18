# Emulator for the PIO Blocks within the RP2040 Microcontroller (Python Edition)

![Build Status](https://github.com/NathanY3G/rp2040-pio-emulator/actions/workflows/package-ci.yml/badge.svg) ![Coverage](./docs/images/coverage-badge.svg) [![PyPI](https://img.shields.io/pypi/v/rp2040-pio-emulator?color=informational)](https://pypi.org/project/rp2040-pio-emulator/)

## Introduction
An emulator for the Programmable Input/Output (PIO) blocks that are present
within the Raspberry Pi Foundation's RP2040 Microcontroller. It is designed
to assist in the analysis of PIO programs and to help you by:

* Enabling unit tests to be written.
* Answering questions such as: How many clock cycles are being consumed?
* Supporting the visualization of GPIO outputs over time.
* Providing alternatives to debugging on real hardware, which can be time consuming.

## Quick Start
Below is a slight variation of the example used within the [Quick Start Guide](./docs/Quick%20Start%20Guide.md).

```python
from pioemu import emulate

program = [0xE029, 0x0041, 0x2080]  # Count down from 9 using X register

generator = emulate(program, stop_when=lambda _, state: state.x_register < 0)

for before, after in generator:
  print(f"X register: {before.x_register} -> {after.x_register}")
```

## Additional Examples
Some additional examples include:

1. Visualisation of square wave program using Jupyter Notebooks within the `examples/` directory.

1. TDD example for the Pimoroni Blinkt! within the `examples/` directory.

1. [pico-pio-examples](https://github.com/NathanY3G/pico-pio-examples)

## Supported Instructions

Instruction | Supported                         | Notes
:-----------| :---------------------------------| :----
JMP         | :heavy_check_mark:                | 
WAIT        | :heavy_check_mark: :warning:      | IRQ variant is not supported
IN          | :heavy_check_mark:                |
OUT         | :heavy_check_mark: :construction: | PC, ISR and EXEC destinations not implemented
PUSH        | :heavy_check_mark: :construction: | IfEmpty variant not implemented
PULL        | :heavy_check_mark: :construction: | IfEmpty variant not implemented
MOV         | :heavy_check_mark: :construction: | Some variants and operations not implemented
IRQ         | :heavy_multiplication_x:          |
SET         | :heavy_check_mark:                |

## Known Limitations
This software is under development and currently has limitations - the notable ones are:

1. Not all of the available instructions are supported - please refer to the table above.

1. No support for pin-sets associated with OUT, SET or IN; all pin numbers are with respect to GPIO 0.

1. Pin-sets do not wrap after GPIO 31.

1. No direct support for the concurrent running of multiple PIO programs;
   a single State Machine is emulated and not an entire PIO block.

## Thanks To
* [aaronjamt](https://github.com/aaronjamt) for contributing features and fixes.
