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
from collections import deque
from pioemu import State
from .support import emulate_single_instruction


def test_pull_loads_osr_from_non_empty_fifo():
    initial_state = State(transmit_fifo=deque([0x1111_1111]))

    new_state = emulate_single_instruction(0x8080, initial_state)  # pull noblock

    assert new_state.output_shift_register == 0x1111_1111


def test_pull_copies_x_to_osr_when_nonblocking_and_fifo_empty():
    initial_state = State(x_register=0x2222_2222)

    new_state = emulate_single_instruction(0x8080, initial_state)  # pull noblock

    assert new_state.output_shift_register == 0x2222_2222


def test_pull_stalls_when_blocking_and_fifo_empty():
    initial_state = State(output_shift_register=0x3333_3333)

    new_state = emulate_single_instruction(0x80A0, initial_state)  # pull block

    assert new_state.program_counter == 0
    assert new_state.output_shift_register == 0x3333_3333


@pytest.mark.parametrize(
    "opcode",
    [
        pytest.param(0x8080, id="pull noblock"),
        pytest.param(0x80A0, id="pull block"),
    ],
)
def test_pull_clears_the_output_shift_register(opcode):
    initial_state = State(transmit_fifo=deque([0]))

    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state.output_shift_counter == 0


@pytest.mark.parametrize(
    "opcode, initial_state, expected_clock_cycles",
    [
        pytest.param(0x8080, State(), 1, id="pull noblock"),
        pytest.param(0x9F80, State(), 32, id="pull noblock [31]"),
        pytest.param(0x9FA0, State(transmit_fifo=deque([1])), 32, id="pull block [31]"),
        pytest.param(
            0x9FA0,
            State(transmit_fifo=deque()),
            1,
            id="pull block [31] when fifo empty",
        ),
    ],
)
def test_pull_consumes_expected_clock_cycles(
    opcode, initial_state, expected_clock_cycles
):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state.clock == expected_clock_cycles
