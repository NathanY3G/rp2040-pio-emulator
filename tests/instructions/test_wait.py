# Copyright 2021, 2022, 2023 Nathan Young
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
import pytest

from pioemu import State, clock_cycles_reached, emulate

from ..opcodes import Opcodes
from ..support import emulate_single_instruction


@pytest.mark.parametrize(
    "opcode, initial_state",
    [
        pytest.param(0x2080, State(pin_values=0), id="wait 1 gpio, 0"),
        pytest.param(0x2020, State(pin_values=1), id="wait 0 pin, 0"),
    ],
)
def test_wait_stalls_when_condition_not_met(opcode: int, initial_state: State):
    _, new_state = emulate_single_instruction(
        opcode, initial_state=initial_state, advance_program_counter=True
    )

    assert new_state.program_counter == 0


@pytest.mark.parametrize(
    "opcode, initial_state",
    [
        pytest.param(0x2080, State(pin_values=1), id="wait 1 gpio, 0"),
        pytest.param(0x2020, State(pin_values=0), id="wait 0 pin, 0"),
    ],
)
def test_wait_advances_when_condition_met(opcode: int, initial_state: State):
    _, new_state = emulate_single_instruction(
        opcode, initial_state=initial_state, advance_program_counter=True
    )

    assert new_state.program_counter == 1


# ---------------------------------------------------------------------------
# WAIT IRQ variant
# ---------------------------------------------------------------------------

# Opcode helpers: WAIT base = 0x2000, IRQ source = bits[6:5] = 2 → 0x40
_WAIT_BASE = 0x2000
_WAIT_IRQ_SRC = 0x40  # source=2 (IRQ)
_WAIT_POL1 = 0x80  # polarity=1


def _wait_irq(index: int, polarity: int) -> int:
    """Return a WAIT IRQ opcode."""
    return _WAIT_BASE | (polarity << 7) | _WAIT_IRQ_SRC | (index & 0x1F)


def test_wait_1_irq_stalls_when_flag_not_set():
    """wait 1 irq 0 stalls when IRQ flag 0 is not set."""
    _, state = next(
        emulate(
            [_wait_irq(0, 1), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
            initial_state=State(irq_flags=0),
        )
    )
    assert state.program_counter == 0


def test_wait_1_irq_advances_and_clears_flag():
    """wait 1 irq 0 advances when flag is set, then clears the flag."""
    _, state = next(
        emulate(
            [_wait_irq(0, 1), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
            initial_state=State(irq_flags=0x01),
        )
    )
    assert state.program_counter == 1
    assert state.irq_flags == 0x00


def test_wait_0_irq_stalls_when_flag_set():
    """wait 0 irq 0 stalls when IRQ flag 0 is set."""
    _, state = next(
        emulate(
            [_wait_irq(0, 0), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
            initial_state=State(irq_flags=0x01),
        )
    )
    assert state.program_counter == 0


def test_wait_0_irq_advances_when_flag_not_set():
    """wait 0 irq 0 advances when flag is not set."""
    _, state = next(
        emulate(
            [_wait_irq(0, 0), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
            initial_state=State(irq_flags=0),
        )
    )
    assert state.program_counter == 1


def test_wait_1_irq_correct_flag_index():
    """wait 1 irq 3 checks and clears the correct flag bit."""
    _, state = next(
        emulate(
            [_wait_irq(3, 1), Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
            initial_state=State(irq_flags=0x0F),
        )
    )
    assert state.program_counter == 1
    # Flag 3 should be cleared; flags 0-2 remain
    assert state.irq_flags == 0x07
