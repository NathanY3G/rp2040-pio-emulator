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

## Examples
This repository includes the following examples:

1. Visualisation of square wave program using Jupyter Notebooks
1. Example for the Pimoroni Blinkt! with Unit Test

In addition, the [pico-pio-examples](https://github.com/NathanY3G/pico-pio-examples)
repository contains an evolution of the example for the Pimoroni Blinkt!

![Screenshot of square-wave program in Jupyter Notebooks](./examples/jupyter-notebook/jupyter_example.png)

## Limitations
This software is under development and currently has limitations - the notable ones are:

1. Only supports a sub-set of the available instructions:

   * JMP (PIN and !OSRE variants not implemented)
   * MOV (some variants and operations not implemented)
   * OUT (PC, ISR and EXEC destinations not implemented)
   * PULL (IfEmpty not implemented)
   * SET
   * WAIT (IRQ variant not implemented)

1. No support for OUT, SET or IN pin-sets; all pin numbers are with respect to Pin 0.

1. Pin-sets do not wrap after GPIO 31.

1. No direct support for the concurrent running of multiple PIO programs;
   a single State Machine is emulated and not an entire PIO block.
