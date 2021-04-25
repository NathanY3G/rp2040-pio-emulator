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
from pioemu import State
from .support import emulate_single_instruction


instructions_to_test = [
    pytest.param(
        0xA021,
        State(x_register=1),
        State(clock=1, program_counter=1, x_register=1),
        id="mov x, x",
    ),
    pytest.param(
        0xA022,
        State(y_register=1),
        State(clock=1, program_counter=1, x_register=1, y_register=1),
        id="mov x, y",
    ),
    pytest.param(
        0xA041,
        State(x_register=2),
        State(clock=1, program_counter=1, x_register=2, y_register=2),
        id="mov y, x",
    ),
    pytest.param(
        0xA042,
        State(y_register=3),
        State(clock=1, program_counter=1, y_register=3),
        id="mov y, y",
    ),
    pytest.param(
        0xA001,
        State(x_register=3),
        State(clock=1, program_counter=1, pin_values=3, x_register=3),
        id="mov pins, x",
    ),
    pytest.param(
        0xA120,
        State(pin_values=2),
        State(clock=2, program_counter=1, pin_values=2, x_register=2),
        id="mov x, pins [1]",
    ),
    pytest.param(
        0xA002,
        State(y_register=3),
        State(clock=1, program_counter=1, pin_values=3, y_register=3),
        id="mov pins, y",
    ),
    pytest.param(
        0xA140,
        State(pin_values=4),
        State(clock=2, program_counter=1, pin_values=4, y_register=4),
        id="mov y, pins [1]",
    ),
    pytest.param(
        0xA0E1,
        State(x_register=0xFFFF_FFFF),
        State(
            clock=1,
            program_counter=1,
            output_shift_register=0xFFFF_FFFF,
            output_shift_counter=0,
            x_register=0xFFFF_FFFF,
        ),
        id="mov osr, x",
    ),
]


@pytest.mark.parametrize("opcode, initial_state, expected_state", instructions_to_test)
def test_mov_instruction(opcode, initial_state, expected_state):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state == expected_state
