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

## Documentation
A [Tour of pioemu](./docs/Tour%20of%20pioemu.md) provides a more detailed explanation than the
[Quick Start Guide](./docs/Quick%20Start%20Guide.md) offers. In addition, there is a
[FAQ](./docs/FAQ.md) available that might contain an answer to your question. However, if none
of these provides you with the necessary information then please consider creating a
[new issue](https://github.com/NathanY3G/rp2040-pio-emulator/issues) - thanks!

## Additional Examples
Some additional examples are available within the [rp2040-pio-emulator-examples](https://github.com/NathanY3G/rp2040-pio-emulator-examples)
repository, including:

1. [TDD](https://en.wikipedia.org/wiki/Test-driven_development) example for the
   [Pimoroni Blinkt!](https://shop.pimoroni.com/products/blinkt)

1. Tool to create Fast Signal Trace (FST) files suitable for analysis by
   [GTKWave](https://gtkwave.sourceforge.net/)

1. Visualisation of square wave program using a
   [Jupyter Notebook](https://jupyter-notebook.readthedocs.io/en/latest/)

## Supported Instructions

Instruction | Supported                         | Notes
:-----------| :---------------------------------| :----
JMP         | :heavy_check_mark:                | 
WAIT        | :heavy_check_mark: :warning:      | IRQ variant is not supported
IN          | :heavy_check_mark:                |
OUT         | :heavy_check_mark: :construction: | EXEC destination not implemented
PUSH        | :heavy_check_mark:                | 
PULL        | :heavy_check_mark:                | 
MOV         | :heavy_check_mark: :construction: | Some variants and operations not implemented
IRQ         | :heavy_multiplication_x:          |
SET         | :heavy_check_mark:                |

## Known Limitations
This software is under development and currently has limitations - the notable ones are:

1. Not all of the available instructions are supported - please refer to the table above.

1. No support for pin-sets associated with `OUT`, `SET` or `IN`; all pin numbers are with respect to GPIO 0.

1. Pin-sets do not wrap after GPIO 31.

1. `PULL IFEMPTY` and `PUSH IFFULL` do not respect the pull and push thresholds.

1. No direct support for the concurrent running of multiple PIO programs;
   a single State Machine is emulated and not an entire PIO block.

## Thanks To
* [aaronjamt](https://github.com/aaronjamt) for contributing features and fixes.
* [Josverl](https://github.com/Josverl) for contributing features.
* [winnylourson](https://github.com/winnylourson) for contributing a bug fix.
