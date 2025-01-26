# Copyright 2025 Nathan Young
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
from collections import deque

import pytest

from pioemu import State, clock_cycles_reached, emulate
from pioemu.shift_register import ShiftRegister

from ..opcodes import Opcodes
from ..support import instruction_param


# fmt: off
@pytest.mark.parametrize(
    "opcode, initial_state, expected_state",
    [
        # Test PIO stalls when auto-push threshold reached with full FIFO
        instruction_param(
            "in null, 32",
            0x4060,
            State(receive_fifo=deque([1, 2, 3, 4]), input_shift_register=ShiftRegister(5, 32)),
            State(receive_fifo=deque([1, 2, 3, 4]), input_shift_register=ShiftRegister(5, 32)),
            expected_program_counter=0,  # Should stall when threshold reached
        ),

        instruction_param(
            "in null, 32",
            0x4060,
            State(receive_fifo=deque(), input_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
            State(receive_fifo=deque([0]), input_shift_register=ShiftRegister(0, 0)),
        ),

        instruction_param(
            "in pins, 8",
            0x4008,
            State(pin_values=0x0000_00FF, receive_fifo=deque(), input_shift_register=ShiftRegister(0xFFFF_FF00, 24)),
            State(pin_values=0x0000_00FF, receive_fifo=deque([0xFFFF_FFFF]), input_shift_register=ShiftRegister(0, 0)),
        ),
    ]
)
# fmt: on
def test_auto_push(opcode: int, initial_state: State, expected_state: State):
    _, new_state = next(
        emulate(
            [opcode, Opcodes.nop()],
            initial_state=initial_state,
            stop_when=clock_cycles_reached(1),
            auto_push=True,
        )
    )

    assert new_state == expected_state
