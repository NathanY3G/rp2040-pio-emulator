# Copyright 2021, 2022, 2023, 2025 Nathan Young
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

from pioemu import ShiftRegister, State
from ..support import emulate_single_instruction

# fmt: off
instructions_to_test_with_left_shift = [
    pytest.param(
        0x6083,
        State(pin_directions=0x0000_0000, output_shift_register=ShiftRegister(0x8000_0000, 5)),
        State(pin_directions=0x0000_0004, output_shift_register=ShiftRegister(0x0000_0000, 8)),
        id="out pindirs, 3",
    ),
    pytest.param(
        0x6008,
        State(pin_values=0x0000_0000, output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(pin_values=0x0000_00FF, output_shift_register=ShiftRegister(0xFFFF_FF00, 8)),
        id="out pins, 8",
    ),
    pytest.param(
        0x6063,
        State(output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(output_shift_register=ShiftRegister(0xFFFF_FFF8, 3)),
        id="out null, 3",
    ),
]

instructions_to_test_with_right_shift = [
    pytest.param(
        0x6083,
        State(pin_directions=0x0, output_shift_register=ShiftRegister(0x0000_0004, 5)),
        State(pin_directions=0x4, output_shift_register=ShiftRegister(0x0000_0000, 8)),
        id="out pindirs, 3",
    ),
    pytest.param(
        0x6008,
        State(pin_values=0x00, output_shift_register=ShiftRegister(0x1FF, 0)),
        State(pin_values=0xFF, output_shift_register=ShiftRegister(0x001, 8)),
        id="out pins, 8",
    ),
    pytest.param(
        0x6023,
        State(x_register=0x0, output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(x_register=0x7, output_shift_register=ShiftRegister(0x1FFF_FFFF, 3)),
        id="out x, 3",
    ),
    pytest.param(
        0x6040,
        State(y_register=0x0000_0000, output_shift_register=ShiftRegister(0xFFFF_FFFF, 0)),
        State(y_register=0xFFFF_FFFF, output_shift_register=ShiftRegister(0x0000_0000, 32)),
        id="out y, 32",
    ),
]
# fmt: on


@pytest.mark.parametrize(
    "opcode, initial_state, expected_state",
    instructions_to_test_with_left_shift,
)
def test_out_instruction_when_shifting_left(
    opcode: int,
    initial_state: State,
    expected_state: State,
):
    _, new_state = emulate_single_instruction(
        opcode,
        initial_state=initial_state,
        shift_osr_right=False,
    )

    assert replace(new_state, clock=0) == expected_state


@pytest.mark.parametrize(
    "opcode, initial_state, expected_state",
    instructions_to_test_with_right_shift,
)
def test_out_instruction_when_shifting_right(
    opcode: int,
    initial_state: State,
    expected_state: State,
):
    _, new_state = emulate_single_instruction(
        opcode,
        initial_state=initial_state,
        shift_osr_right=True,
    )

    assert replace(new_state, clock=0) == expected_state


# fmt: off
@pytest.mark.parametrize("opcode, initial_state, expected_state", [
    pytest.param(
        0x60A2,
        State(output_shift_register=ShiftRegister(0x0000_001F, 0)),
        State(output_shift_register=ShiftRegister(0x0000_0007, 2), program_counter=3),
        id="out pc, 2",
    ),

    pytest.param(
        0x60C5,
        State(output_shift_register=ShiftRegister(0xDEAD_BEEF, 0), input_shift_register=ShiftRegister(0x1234_4567, 32)),
        State(output_shift_register=ShiftRegister(0x06F5_6DF7, 5), input_shift_register=ShiftRegister(0x0000_000F, 5)),
        id="out isr, 5",
    ),
])
# fmt: on
def test_out_instruction(opcode, initial_state: State, expected_state: State):
    _, new_state = emulate_single_instruction(
        opcode,
        initial_state=initial_state,
    )

    assert replace(new_state, clock=0) == expected_state


# fmt: off
@pytest.mark.parametrize("opcode, out_base, out_count, initial_state, expected_state", [
    pytest.param(
        0x6000,
        0,
        32,
        State(pin_values=0xFFFF_0000, output_shift_register=ShiftRegister(0xEEEE_EEEE, 0)),
        State(pin_values=0xEEEE_EEEE, output_shift_register=ShiftRegister(0x0000_0000, 32),
        ),
        id="out pins, 32",
    ),
    pytest.param(
        0x600F,
        0,
        17,
        State(pin_values=0xFFFF_FFFF, output_shift_register=ShiftRegister(0xEEEE_EEEE, 0)),
        State(pin_values=0xFFFE_6EEE, output_shift_register=ShiftRegister(0x0001_DDDD, 15)),
        id="out pins, 15",
    ),
    pytest.param(
        0x600F,
        11,
        15,
        State(pin_values=0x0000_0000, output_shift_register=ShiftRegister(0x0001_DDDD, 15)),
        State(pin_values=0x02EE_E800, output_shift_register=ShiftRegister(0x0000_0003, 30)),
        id="out pins, 15",
    ),
])
# fmt: on
def test_out_to_pins(
    opcode, out_base: int, out_count: int, initial_state: State, expected_state: State
):
    _, new_state = emulate_single_instruction(
        opcode, initial_state=initial_state, out_base=out_base, out_count=out_count
    )

    assert replace(new_state, clock=0) == expected_state


# fmt: off
@pytest.mark.parametrize("opcode, out_base, out_count, initial_state, expected_state", [
    pytest.param(
        0x6098,
        0,
        24,
        State(pin_directions=0xFFFF_FFFF, output_shift_register=ShiftRegister(0xAAAA_AAAA, 0)),
        State(pin_directions=0xFFAA_AAAA, output_shift_register=ShiftRegister(0x0000_00AA, 24)),
        id="out pindirs, 24",
    ),
])
# fmt: on
def test_out_to_pin_directions(
    opcode, out_base: int, out_count: int, initial_state: State, expected_state: State
):
    _, new_state = emulate_single_instruction(
        opcode, initial_state=initial_state, out_base=out_base, out_count=out_count
    )

    assert replace(new_state, clock=0) == expected_state
