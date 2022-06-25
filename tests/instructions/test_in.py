# Copyright 2022 Nathan Young
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
from pioemu import clock_cycles_reached, emulate, ShiftRegister, State
from ..support import instruction_param
from ..opcodes import Opcodes

# fmt: off
instructions_to_test_with_right_shift = [
    instruction_param(
        "in pins, 32",
        0x4000,
        State(pin_values=0xDEAD_BEEF, input_shift_register=ShiftRegister(0x0000_0000, 0)),
        State(pin_values=0xDEAD_BEEF, input_shift_register=ShiftRegister(0xDEAD_BEEF, 32)),
    ),
    instruction_param(
        "in x, 16",
        0x4030,
        State(x_register=0x1234_4567, input_shift_register=ShiftRegister(0x0000_0000, 0)),
        State(x_register=0x1234_4567, input_shift_register=ShiftRegister(0x4567_0000, 16)),
    ),
    instruction_param(
        "in y, 16",
        0x4050,
        State(y_register=0x0000_0123, input_shift_register=ShiftRegister(0x4567_0000, 16)),
        State(y_register=0x0000_0123, input_shift_register=ShiftRegister(0x0123_4567, 32)),
    ),
    instruction_param(
        "in null, 31",
        0x407F,
        State(input_shift_register=ShiftRegister(0xFFFF_FFFF, 1)),
        State(input_shift_register=ShiftRegister(0x0000_0001, 32)),
    ),
    instruction_param(
        "in isr, 1",
        0x40C1,
        State(input_shift_register=ShiftRegister(0x0000_0001, 1)),
        State(input_shift_register=ShiftRegister(0x8000_0000, 2)),
    ),
    instruction_param(
        "in osr, 24",
        0x40F8,
        State(output_shift_register=ShiftRegister(0xAAAA_5555, 0), input_shift_register=ShiftRegister(0x0000_0000, 0)),
        State(output_shift_register=ShiftRegister(0xAAAA_5555, 0), input_shift_register=ShiftRegister(0xAA55_5500, 24)),
    ),
]

@pytest.mark.parametrize(
    "opcode, initial_state, expected_state", instructions_to_test_with_right_shift
)
def test_in_instruction_when_shifting_right(opcode, initial_state, expected_state):
    _, new_state = next(
        emulate(
            [opcode, Opcodes.nop()],
            initial_state=initial_state,
            stop_when=clock_cycles_reached(1),
            shift_isr_right=True,
        )
    )

    assert new_state == expected_state
