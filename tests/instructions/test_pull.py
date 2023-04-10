# Copyright 2021, 2022, 2023 Nathan Young
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

@pytest.mark.parametrize("opcode, initial_state, expected_state", [
    instruction_param(
        "pull noblock when fifo not empty",
        0x8080,
        State(transmit_fifo=deque([0x1111_1111])),
        State(transmit_fifo=deque(), output_shift_register=ShiftRegister(0x1111_1111, 0)),
    ),
    instruction_param(
        "pull noblock when fifo empty",
        0x8080,
        State(transmit_fifo=deque(), x_register=0x2222_2222),
        State(transmit_fifo=deque(), output_shift_register=ShiftRegister(0x2222_2222, 0), x_register=0x2222_2222),
    ),
    instruction_param(
        "pull block when fifo not empty",
        0x80A0,
        State(transmit_fifo=deque([0x3333_3333])),
        State(transmit_fifo=deque(), output_shift_register=ShiftRegister(0x3333_3333, 0)),
    ),
    instruction_param(
        "pull block when fifo empty",
        0x80A0,
        State(transmit_fifo=deque()),
        State(transmit_fifo=deque()),
        expected_program_counter=0,
    ),
])
# fmt: on
def test_pull_instruction(opcode: int, initial_state: State, expected_state: State):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state == expected_state
