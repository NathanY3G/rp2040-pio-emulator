# Copyright 2021 Nathan Young
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
from collections import deque
from pioemu import ShiftRegister, State
from .support import emulate_single_instruction, instruction_param


# fmt: off
instructions_to_test = [
    instruction_param(
        "out pindirs, 3",
        0x6083,
        State(pin_directions=0x0, output_shift_register=ShiftRegister(0x0000_0004, 5)),
        State(pin_directions=0x4, output_shift_register=ShiftRegister(0x0000_0000, 8)),
    ),
    instruction_param(
        "out pins, 8",
        0x6008,
        State(pin_values=0x00, output_shift_register=ShiftRegister(0x1FF, 0)),
        State(pin_values=0xFF, output_shift_register=ShiftRegister(0x001, 8)),
    ),
    instruction_param(
        "out x, 3",
        0x6023,
        State(x_register=0x0, output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(x_register=0x7, output_shift_register=ShiftRegister(0x1FFF_FFFF, 3)),
    ),
    instruction_param(
        "out y, 32",
        0x6040,
        State(y_register=0x0000_0000, output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(y_register=0xFFFF_FFFF, output_shift_register=ShiftRegister(0x0000_0000, 32)),
    ),
]
# fmt: on


@pytest.mark.parametrize("opcode, initial_state, expected_state", instructions_to_test)
def test_out_instruction(opcode, initial_state, expected_state):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state == expected_state


@pytest.mark.parametrize(
    "opcode, expected_clock_cycles",
    [
        pytest.param(0x6283, 3, id="out pindirs, 3 [2]"),
        pytest.param(0x6708, 8, id="out pins, 8 [7]"),
        pytest.param(0x6023, 1, id="out x, 3"),
        pytest.param(0x7F40, 32, id="out y, 32 [31]"),
    ],
)
def test_out_consumes_expected_clock_cycles(opcode, expected_clock_cycles):
    new_state = emulate_single_instruction(opcode)

    assert new_state.clock == expected_clock_cycles
