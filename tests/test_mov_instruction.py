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
from pioemu import ShiftRegister, State
from .support import emulate_single_instruction, instruction_param


# fmt: off
instructions_to_test = [
    instruction_param(
        "mov x, x", 0xA021, State(x_register=1), State(x_register=1),
    ),
    instruction_param(
        "mov x, y", 0xA022, State(y_register=1), State(x_register=1, y_register=1),
    ),
    instruction_param(
        "mov y, x", 0xA041, State(x_register=2), State(x_register=2, y_register=2),
    ),
    instruction_param(
        "mov y, y", 0xA042, State(y_register=3), State(y_register=3),
    ),
    instruction_param(
        "mov pins, x", 0xA001, State(x_register=3), State(pin_values=3, x_register=3),
    ),
    instruction_param(
        "mov x, pins", 0xA020, State(pin_values=2), State(pin_values=2, x_register=2),
    ),
    instruction_param(
        "mov pins, y", 0xA002, State(y_register=3), State(pin_values=3, y_register=3),
    ),
    instruction_param(
        "mov y, pins", 0xA040, State(pin_values=4), State(pin_values=4, y_register=4),
    ),
    instruction_param(
        "mov osr, x",
        0xA0E1,
        State(x_register=0xFFFF_FFFF),
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0), x_register=0xFFFF_FFFF),
    ),
    instruction_param(
        "mov isr, osr",
        0xA0C7,
        State(input_shift_register=ShiftRegister(0x0000_0000, 31), output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(input_shift_register=ShiftRegister(0xFFFF_FFFF, 0), output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
    ),
    instruction_param(
        "mov osr, isr",
        0xA0E6,
        State(output_shift_register=ShiftRegister(0x0000_0000, 31), input_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0), input_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
    ),
]
# fmt: on


@pytest.mark.parametrize("opcode, initial_state, expected_state", instructions_to_test)
def test_mov_instruction(opcode, initial_state, expected_state):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state == expected_state


@pytest.mark.parametrize(
    "opcode, expected_clock_cycles",
    [
        pytest.param(0xA120, 2, id="mov x, pins [1]"),
        pytest.param(0xA140, 2, id="mov y, pins [1]"),
    ],
)
def test_mov_consumes_expected_clock_cycles(opcode, expected_clock_cycles):
    new_state = emulate_single_instruction(opcode)

    assert new_state.clock == expected_clock_cycles
