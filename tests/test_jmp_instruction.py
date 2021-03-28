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
from pioemu import emulate, State
from .support import emulate_single_instruction


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
    opcodes = [0xE023, 0x0041]  # set x, 3 and jmp x--

    state_changes = [
        (state.program_counter, state.x_register)
        for _, state in emulate(opcodes, max_clock_cycles=5)
    ]

    assert state_changes == [(1, 3), (1, 2), (1, 1), (1, 0), (2, -1)]


def test_jump_when_y_is_non_zero_post_decrement():
    opcodes = [0xE043, 0x0081]  # set y, 3 and jmp y--

    state_changes = [
        (state.program_counter, state.y_register)
        for _, state in emulate(opcodes, max_clock_cycles=5)
    ]

    assert state_changes == [(1, 3), (1, 2), (1, 1), (1, 0), (2, -1)]


@pytest.mark.parametrize(
    "opcode, expected_clock_cycles",
    [
        pytest.param(0x0000, 1, id="jmp 0"),
        pytest.param(0x0102, 2, id="jmp 1 [1]"),
    ],
)
def test_jump_consumes_expected_clock_cycles(opcode, expected_clock_cycles):
    new_state = emulate_single_instruction(opcode)

    assert new_state.clock == expected_clock_cycles
