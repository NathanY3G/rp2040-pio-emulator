"""
Example: Using TX and RX FIFOs with pioemu

Demonstrates the full FIFO data path by emulating a loopback PIO program:

    pull block      ; 0: Pull value from TX FIFO into OSR
    out pins, 32    ; 1: Write OSR to pins (all 32 bits)
    in pins, 32     ; 2: Read pins into ISR (reads back what we just wrote)
    push block      ; 3: Push ISR contents to RX FIFO

Data flows: TX FIFO -> OSR -> pins -> ISR -> RX FIFO

The TX FIFO (transmit_fifo) is pre-loaded with values in the initial State,
simulating what the CPU would write. After emulation, the RX FIFO
(receive_fifo) contains the results, which the CPU would normally read.
"""

from collections import deque

from pioemu import State, emulate, clock_cycles_reached

# PIO opcodes (assembled from the program above)
PULL_BLOCK = 0x80A0  # pull block
OUT_PINS_32 = 0x6000  # out pins, 32
IN_PINS_32 = 0x4000  # in pins, 32
PUSH_BLOCK = 0x8020  # push block

program = [PULL_BLOCK, OUT_PINS_32, IN_PINS_32, PUSH_BLOCK]

# Pre-load the TX FIFO with values for the PIO program to consume.
# The TX FIFO (transmit_fifo) is written by the CPU and read by PIO via PULL.
initial_state = State(
    transmit_fifo=deque([0xDEAD_BEEF, 0xCAFE_BABE, 0x1234_5678]),
)

# Run the emulation for enough cycles to process all three values.
# Each iteration of the 4-instruction loop takes 4 clock cycles.
# 3 values * 4 instructions = 12 cycles, plus a final stall on PULL.
generator = emulate(
    program,
    initial_state=initial_state,
    stop_when=clock_cycles_reached(14),
    out_base=0,
    out_count=32,
)

print("Emulating PIO loopback: TX FIFO -> pins -> RX FIFO")
print(f"TX FIFO starts with: {[hex(v) for v in initial_state.transmit_fifo]}")
print()

final_state = initial_state
for before, after in generator:
    opcode = program[before.program_counter]
    instruction_names = {
        PULL_BLOCK: "pull block",
        OUT_PINS_32: "out pins, 32",
        IN_PINS_32: "in pins, 32",
        PUSH_BLOCK: "push block",
    }
    name = instruction_names.get(opcode, f"??? ({opcode:#06x})")

    # Show what changed
    prefix = f"clock {after.clock:2d}  PC={before.program_counter}"
    print(f"{prefix}  {name:14s}", end="  ")

    stalled = (
        before.program_counter == after.program_counter
        and opcode == PULL_BLOCK
    )
    if stalled:
        print("[stalled - TX FIFO empty]")
    elif opcode == PULL_BLOCK:
        print(f"OSR <- {hex(after.output_shift_register.contents)}")
    elif opcode == OUT_PINS_32:
        print(f"pins <- {hex(after.pin_values)}")
    elif opcode == IN_PINS_32:
        print(f"ISR <- {hex(after.input_shift_register.contents)}")
    elif opcode == PUSH_BLOCK:
        print(f"RX FIFO <- {[hex(v) for v in after.receive_fifo]}")
    else:
        print()
    final_state = after

print()
print(f"TX FIFO remaining: {[hex(v) for v in final_state.transmit_fifo]}")
print(f"RX FIFO contents:  {[hex(v) for v in final_state.receive_fifo]}")
print()

# Verify the loopback: RX FIFO should contain the same values we put in TX FIFO
expected = [0xDEAD_BEEF, 0xCAFE_BABE, 0x1234_5678]
actual = list(final_state.receive_fifo)
assert actual == expected, f"Expected {expected}, got {actual}"
print("Loopback verified: all values passed through correctly!")
