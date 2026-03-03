# Copyright 2026 Ned Konz <ned@metamagix.tech>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from dataclasses import replace

import pytest

from pioemu import State, clock_cycles_reached, emulate

from ..opcodes import Opcodes

# IRQ opcode construction helpers.
# Bits [15:13] = 110 (= 6 << 13 = 0xC000), bit 7 = 0 (reserved).
# Bit 6 = Clear, bit 5 = Wait, bits [4:3] = IdxMode, bits [2:0] = Index.
_IRQ_BASE = 0xC000


def _irq_set(index: int, *, wait: bool = False, idx_mode: int = 0) -> int:
    """Return an IRQ-raise opcode for the given index."""
    return _IRQ_BASE | (idx_mode << 3) | (0x20 if wait else 0) | (index & 0x07)


def _irq_clear(index: int) -> int:
    """Return an IRQ-clear opcode for the given index."""
    return _IRQ_BASE | 0x40 | (index & 0x07)


# ---------------------------------------------------------------------------
# IRQ raise (no wait)
# ---------------------------------------------------------------------------

def test_irq_set_raises_flag():
    _, state = next(
        emulate(
            [_irq_set(0), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
        )
    )
    assert state.irq_flags == 0x01


def test_irq_set_advances_pc():
    _, state = next(
        emulate(
            [_irq_set(0), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
        )
    )
    assert state.program_counter == 1


@pytest.mark.parametrize("index", range(8))
def test_irq_set_correct_flag_bit(index):
    _, state = next(
        emulate(
            [_irq_set(index), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
        )
    )
    assert state.irq_flags == (1 << index)


def test_irq_set_calls_handler():
    called_with = []

    def handler(irq_index: int, state: State) -> State:
        called_with.append((irq_index, state.irq_flags))
        return state

    next(
        emulate(
            [_irq_set(3), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
            irq_handler=handler,
        )
    )

    assert called_with == [(3, 0x08)]


# ---------------------------------------------------------------------------
# IRQ clear (no wait)
# ---------------------------------------------------------------------------

def test_irq_clear_lowers_flag():
    initial_state = State(irq_flags=0xFF)
    _, state = next(
        emulate(
            [_irq_clear(0), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
            initial_state=initial_state,
        )
    )
    assert state.irq_flags == 0xFE


def test_irq_clear_advances_pc():
    initial_state = State(irq_flags=0x01)
    _, state = next(
        emulate(
            [_irq_clear(0), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
            initial_state=initial_state,
        )
    )
    assert state.program_counter == 1


# ---------------------------------------------------------------------------
# IRQ with wait
# ---------------------------------------------------------------------------

def test_irq_wait_stalls_until_handler_clears_flag():
    """IRQ+wait stalls for one cycle while the flag is set, then completes."""
    call_count = [0]

    def handler(irq_index: int, state: State) -> State:
        call_count[0] += 1
        if call_count[0] >= 2:
            # Clear flag on the second call to allow the stall to end
            return replace(state, irq_flags=state.irq_flags & ~(1 << irq_index))
        return state

    states = list(
        emulate(
            [_irq_set(0, wait=True), Opcodes.nop()],
            stop_when=clock_cycles_reached(3),
            irq_handler=handler,
        )
    )

    # Cycle 1: IRQ fires, flag raised, stall → irq_flags=1
    assert states[0][1].irq_flags == 0x01
    assert states[0][1].program_counter == 0

    # Cycle 2: handler clears flag, stall ends → irq_flags=0, PC advances
    assert states[1][1].irq_flags == 0x00
    assert states[1][1].program_counter == 1


def test_irq_wait_handler_called_each_stall_cycle():
    call_count = [0]

    def handler(irq_index: int, state: State) -> State:
        call_count[0] += 1
        return state  # Never clears; let stop_when terminate

    list(
        emulate(
            [_irq_set(0, wait=True)],
            stop_when=clock_cycles_reached(5),
            irq_handler=handler,
        )
    )

    assert call_count[0] == 5


def test_irq_wait_default_handler_stalls():
    """With no handler (default no-op), IRQ+wait stalls indefinitely."""
    states = list(
        emulate(
            [_irq_set(0, wait=True)],
            stop_when=clock_cycles_reached(3),
        )
    )

    # PC should never advance from 0
    for _, after in states:
        assert after.program_counter == 0
        assert after.irq_flags == 0x01


# ---------------------------------------------------------------------------
# REL indexing mode (idx_mode=2, equivalent to direct for state machine 0)
# ---------------------------------------------------------------------------

def test_irq_rel_mode_same_as_direct():
    opcode = _irq_set(2, idx_mode=2)
    _, state = next(
        emulate(
            [opcode, Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
        )
    )
    assert state.irq_flags == (1 << 2)


# ---------------------------------------------------------------------------
# Unsupported indexing modes (PREV=1, NEXT=3) → emulation stops immediately
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("idx_mode", [1, 3])
def test_irq_unsupported_idx_mode_stops_emulation(idx_mode):
    opcode = _irq_set(0, idx_mode=idx_mode)
    with pytest.raises(StopIteration):
        next(
            emulate(
                [opcode],
                stop_when=lambda _, __: False,
            )
        )
