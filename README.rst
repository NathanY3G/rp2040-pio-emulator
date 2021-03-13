====================================================================================
Emulator for the PIO Blocks within the Raspberry Pi Microcontroller (Python Edition)
====================================================================================

About
=====
An emulator for the Programmable Input/Output blocks that are present within
the Raspberry Pi Foundation's RP2040 Microcontroller.

Limitations
===========
1. Emulates a State Machine within a PIO block and not an entire PIO block

2. Limited set of operations supported:

   * JMP (unconditional)
   * SET
   * WAIT (IRQ variant not implemented)

3. No support for pin sets

4. No support for delay values
