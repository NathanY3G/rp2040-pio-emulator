# Copyright 2021, 2022 Nathan Young
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
from pioemu import emulate, State
from ..support import emulate_single_instruction
from ..opcodes import Opcodes


def test_jump_always_forward():
    new_state = emulate_single_instruction(0x0007)  # jmp 7

    assert new_state.program_counter == 7


@pytest.mark.parametrize(
    "opcode, initial_state, expected_program_counter",
    [
        pytest.param(0x0020, State(x_register=0), 0, id="jmp !x 0 when x is 0"),
        pytest.param(0x0020, State(x_register=1), 1, id="jmp !x 0 when x is 1"),
        pytest.param(0x0062, State(y_register=0), 2, id="jmp !y 2 when y is 0"),
        pytest.param(0x0062, State(y_register=1), 1, id="jmp !y 2 when y is 1"),
        pytest.param(
            0x00BF,
            State(x_register=1, y_register=1),
            1,
            id="jmp x!=y when both x and y are 1",
        ),
        pytest.param(
            0x00BF,
            State(x_register=1, y_register=2),
            31,
            id="jmp x!=y when x is 1 and y is 2",
        ),
    ],
)
def test_jump_for_scratch_register_conditions(
    opcode, initial_state, expected_program_counter
):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state.program_counter == expected_program_counter


def test_jump_when_x_is_non_zero_post_decrement():
    opcodes = [0xE023, 0x0041, Opcodes.nop()]  # set x 3, jmp x-- and nop

    x_register_series = [
        state.x_register
        for state, _ in emulate(
            opcodes, stop_when=lambda _, state: state.program_counter == 2
        )
    ]

    assert x_register_series == [0, 3, 2, 1, 0]


def test_jump_when_y_is_non_zero_post_decrement():
    opcodes = [0xE043, 0x0081, Opcodes.nop()]  # set y 3, jmp y-- and nop

    y_register_series = [
        state.y_register
        for state, _ in emulate(
            opcodes, stop_when=lambda _, state: state.program_counter == 2
        )
    ]

    assert y_register_series == [0, 3, 2, 1, 0]


@pytest.mark.parametrize(
    "opcode, initial_state, expected_clock_cycles",
    [
        pytest.param(0x0000, State(), 1, id="jmp 0"),
        pytest.param(0x0102, State(), 2, id="jmp 1 [1]"),
        pytest.param(0x0A80, State(y_register=0), 11, id="jmp y-- [10]"),
        pytest.param(0x0A80, State(y_register=3), 11, id="jmp y-- [10]"),
    ],
)
def test_jump_consumes_expected_clock_cycles(
    opcode, initial_state, expected_clock_cycles
):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state.clock == expected_clock_cycles
