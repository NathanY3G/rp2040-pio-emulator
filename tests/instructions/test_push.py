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
        "push noblock when FIFO not full",
        0x8000,
        State(input_shift_register=ShiftRegister(108, 8), receive_fifo=deque([72])),
        State(input_shift_register=ShiftRegister(0, 0), receive_fifo=deque([72, 108])),
    ),
    instruction_param(
        "push noblock when FIFO full",
        0x8000,
        State(input_shift_register=ShiftRegister(72, 8), receive_fifo=deque([108, 200, 288, 392])),
        State(input_shift_register=ShiftRegister(0, 0), receive_fifo=deque([108, 200, 288, 392])),
    ),
    instruction_param(
        "push block when FIFO not full",
        0x8020,
        State(input_shift_register=ShiftRegister(108, 8), receive_fifo=deque([72])),
        State(input_shift_register=ShiftRegister(0, 0), receive_fifo=deque([72, 108])),
    ),
    instruction_param(
        "push block when FIFO full",
        0x8020,
        State(input_shift_register=ShiftRegister(72, 8), receive_fifo=deque([108, 200, 288, 392])),
        State(input_shift_register=ShiftRegister(72, 8), receive_fifo=deque([108, 200, 288, 392])),
        expected_program_counter=0,
    ),
    instruction_param(
        "push iffull noblock when ISR not full and FIFO not full",
        0x8040,
        State(input_shift_register=ShiftRegister(0, 1), receive_fifo=deque([72, 108])),
        State(input_shift_register=ShiftRegister(0, 1), receive_fifo=deque([72, 108])),
    ),
    instruction_param(
        "push iffull noblock when ISR not full and FIFO full",
        0x8040,
        State(input_shift_register=ShiftRegister(432, 31), receive_fifo=deque([108, 200, 288, 392])),
        State(input_shift_register=ShiftRegister(432, 31), receive_fifo=deque([108, 200, 288, 392])),
    ),
    instruction_param(
        "push iffull noblock when ISR full and FIFO not full",
        0x8040,
        State(input_shift_register=ShiftRegister(288, 32), receive_fifo=deque([72, 108])),
        State(input_shift_register=ShiftRegister(0, 0), receive_fifo=deque([72, 108, 288])),
    ),
    instruction_param(
        "push iffull noblock when ISR full and FIFO full",
        0x8040,
        State(input_shift_register=ShiftRegister(432, 32), receive_fifo=deque([108, 200, 288, 392])),
        State(input_shift_register=ShiftRegister(0, 0), receive_fifo=deque([108, 200, 288, 392])),
    ),
    instruction_param(
        "push iffull block when ISR full and FIFO not full",
        0x8060,
        State(input_shift_register=ShiftRegister(288, 32), receive_fifo=deque([72, 108])),
        State(input_shift_register=ShiftRegister(0, 0), receive_fifo=deque([72, 108, 288])),
    ),
    instruction_param(
        "push iffull block when ISR full and FIFO full",
        0x8060,
        State(input_shift_register=ShiftRegister(432, 32), receive_fifo=deque([108, 200, 288, 392])),
        State(input_shift_register=ShiftRegister(432, 32), receive_fifo=deque([108, 200, 288, 392])),
        expected_program_counter=0,
    ),
])
# fmt: on
def test_push_instruction(opcode: int, initial_state: State, expected_state: State):
    _, new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state == expected_state


def test_receive_fifo_in_before_state_remains_unaffected():
    initial_state = State(
        receive_fifo=deque(), input_shift_register=ShiftRegister(0xDEAD_BEEF, 0)
    )

    before_state, _ = emulate_single_instruction(0x8000, initial_state)  # push noblock

    assert before_state.receive_fifo == deque()
