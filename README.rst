====================================================================================
Emulator for the PIO Blocks within the Raspberry Pi Microcontroller (Python Edition)
====================================================================================

About
=====
A proof-of-concept emulator for the Programmable Input/Output blocks that are
present within the Raspberry Pi Foundation's RP2040 Microcontroller.

Example Jupyter Notebook
========================
The emulator can even be used from within Jupyter Notebooks to visualize the
output of PIO programs. The screenshot below is taken from the ``square_wave_example.ipynb``
notebook that is included in this repository.

.. image:: ./docs/images/jupyter_example.png
   :alt: Screenshot of Jupyter Notebook example

Limitations
===========
1. Emulates a State Machine within a PIO block and not an entire PIO block

2. Limited set of operations supported:

   * JMP (PIN and !OSRE variants not implemented)
   * NOP (MOV Y, Y)
   * OUT (NULL, PC, ISR and EXEC destinations not implemented)
   * PULL (IfEmpty not implemented)
   * SET
   * WAIT (IRQ variant not implemented)

3. No support for pin sets

4. Transmit FIFO is not immutable
