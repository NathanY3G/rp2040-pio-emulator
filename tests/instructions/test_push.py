# Copyright 2023 Nathan Young
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

from pioemu import ShiftRegister, State

from ..support import emulate_single_instruction, instruction_param


# fmt: off
@pytest.mark.parametrize("opcode, initial_state, expected_state", [
    instruction_param(
        "push noblock",
        0x8000,
        State(input_shift_register=ShiftRegister(72, 8)),
        State(input_shift_register=ShiftRegister(0, 0), receive_fifo=deque([72])),
    ),
    instruction_param(
        "push block",
        0x8020,
        State(input_shift_register=ShiftRegister(72, 8), receive_fifo=deque([108, 200, 288, 392])),
        State(input_shift_register=ShiftRegister(72, 8), receive_fifo=deque([108, 200, 288, 392])),
        expected_program_counter=0,
    ),
])
# fmt: on
def test_push_instruction(opcode: int, initial_state: State, expected_state: State):
    _, new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state == expected_state
