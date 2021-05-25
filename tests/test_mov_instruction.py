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
        "mov pins null",
        0xA003,
        State(),
        State(pin_values=0x0000_0000),
    ),
    instruction_param(
        "mov x ~ osr",
        0xA02F,
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0), x_register=0x0000_0000),
    ),
    instruction_param(
        "mov y y",
        0xA042,
        State(y_register=0xFFFF_FFFF),
        State(y_register=0xFFFF_FFFF),
    ),
    instruction_param(
        "mov osr x",
        0xA0E1,
        State(x_register=0xFFFF_FFFF),
        State(x_register=0xFFFF_FFFF, output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
    ),
    instruction_param(
        "mov isr ~ pins",
        0xA0C8,
        State(pin_values=0x1_0000_0000),
        State(pin_values=0x1_0000_0000, input_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
    ),
    instruction_param(
        "mov pins ~ isr",
        0xA00E,
        State(input_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(input_shift_register=ShiftRegister(0xFFFF_FFFF, 0), pin_values=0x0000_0000),
    ),
    instruction_param(
        "mov x pins",
        0xA020,
        State(pin_values=0x1_0000_0000),
        State(pin_values=0x1_0000_0000, x_register=0x0000_0000),
    ),
    instruction_param(
        "mov y ~ pins",
        0xA048,
        State(pin_values=0xFFFF_FFFF),
        State(pin_values=0xFFFF_FFFF, y_register=0x0000_0000),
    ),
    instruction_param(
        "mov osr ~ pins",
        0xA0E8,
        State(pin_values=0x1_0000_0000),
        State(pin_values=0x1_0000_0000, output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
    ),
    instruction_param(
        "mov isr ~ x",
        0xA0C9,
        State(x_register=0xFFFF_FFFF),
        State(x_register=0xFFFF_FFFF, input_shift_register=ShiftRegister(0x0000_0000, 0)),
    ),
    instruction_param(
        "mov pins ~ y",
        0xA00A,
        State(y_register=0x1_0000_0000),
        State(y_register=0x1_0000_0000, pin_values=0xFFFF_FFFF),
    ),
    instruction_param(
        "mov x ~ null",
        0xA02B,
        State(),
        State(x_register=0xFFFF_FFFF),
    ),
    instruction_param(
        "mov x isr",
        0xA026,
        State(input_shift_register=ShiftRegister(0x1_0000_0000, 0)),
        State(input_shift_register=ShiftRegister(0x1_0000_0000, 0), x_register=0x0000_0000),
    ),
    instruction_param(
        "mov pins osr",
        0xA007,
        State(output_shift_register=ShiftRegister(0x1_0000_0000, 0)),
        State(output_shift_register=ShiftRegister(0x1_0000_0000, 0), pin_values=0x0000_0000),
    ),
    instruction_param(
        "mov y ~ x",
        0xA049,
        State(x_register=0x1_0000_0000),
        State(x_register=0x1_0000_0000, y_register=0xFFFF_FFFF),
    ),
    instruction_param(
        "mov isr osr",
        0xA0C7,
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0), input_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
    ),
    instruction_param(
        "mov osr ~ osr",
        0xA0EF,
        State(output_shift_register=ShiftRegister(0x1_0000_0000, 0)),
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
    ),
    instruction_param(
        "mov y osr",
        0xA047,
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0), y_register=0xFFFF_FFFF),
    ),
    instruction_param(
        "mov osr ~ isr",
        0xA0EE,
        State(input_shift_register=ShiftRegister(0x1_0000_0000, 0)),
        State(input_shift_register=ShiftRegister(0x1_0000_0000, 0), output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
    ),
    instruction_param(
        "mov isr ~ isr",
        0xA0CE,
        State(input_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(input_shift_register=ShiftRegister(0x0000_0000, 0)),
    ),
    instruction_param(
        "mov isr ~ y",
        0xA0CA,
        State(y_register=0xFFFF_FFFF),
        State(y_register=0xFFFF_FFFF, input_shift_register=ShiftRegister(0x0000_0000, 0)),
    ),
    instruction_param(
        "mov isr ~ null",
        0xA0CB,
        State(),
        State(input_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
    ),
    instruction_param(
        "mov pins ~ pins",
        0xA008,
        State(pin_values=0x1_0000_0000),
        State(pin_values=0xFFFF_FFFF),
    ),
    instruction_param(
        "mov x y",
        0xA022,
        State(y_register=0x1_0000_0000),
        State(y_register=0x1_0000_0000, x_register=0x0000_0000),
    ),
    instruction_param(
        "mov y null",
        0xA043,
        State(),
        State(y_register=0x0000_0000),
    ),
    instruction_param(
        "mov osr ~ null",
        0xA0EB,
        State(),
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
    ),
    instruction_param(
        "mov pins ~ x",
        0xA009,
        State(x_register=0xFFFF_FFFF),
        State(x_register=0xFFFF_FFFF, pin_values=0x0000_0000),
    ),
    instruction_param(
        "mov x x",
        0xA021,
        State(x_register=0xFFFF_FFFF),
        State(x_register=0xFFFF_FFFF),
    ),
    instruction_param(
        "mov y isr",
        0xA046,
        State(input_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(input_shift_register=ShiftRegister(0xFFFF_FFFF, 0), y_register=0xFFFF_FFFF),
    ),
    instruction_param(
        "mov osr ~ y",
        0xA0EA,
        State(y_register=0x1_0000_0000),
        State(y_register=0x1_0000_0000, output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
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
