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
from collections import deque

import pytest

from pioemu import State

from ..support import emulate_single_instruction


# fmt: off
@pytest.mark.parametrize(
    "opcode, initial_state, expected_clock_cycles",
    [
        pytest.param(0x0000, State(), 1, id="jmp 0"),
        pytest.param(0x0102, State(), 2, id="jmp 1 [1]"),
        pytest.param(0x0A80, State(y_register=0), 11, id="jmp y-- [10]"),
        pytest.param(0x0A80, State(y_register=3), 11, id="jmp y-- [10]"),
        pytest.param(0xA120, State(), 2, id="mov x, pins [1]"),
        pytest.param(0xA140, State(), 2, id="mov y, pins [1]"),
        pytest.param(0x6283, State(), 3, id="out pindirs, 3 [2]"),
        pytest.param(0x6708, State(), 8, id="out pins, 8 [7]"),
        pytest.param(0x6023, State(), 1, id="out x, 3"),
        pytest.param(0x7F40, State(), 32, id="out y, 32 [31]"),
        pytest.param(0x8080, State(), 1, id="pull noblock"),
        pytest.param(0x9F80, State(), 32, id="pull noblock [31]"),
        pytest.param(0x9FA0, State(transmit_fifo=deque([1])), 32, id="pull block [31]"),
        pytest.param(0x9FA0, State(transmit_fifo=deque()), 1, id="pull block [31] when fifo empty"),
        pytest.param(0xE102, State(), 2, id="set pins, 2 [1]"),
        pytest.param(0xE03F, State(), 1, id="set x, 31"),
        pytest.param(0xFF40, State(), 32, id="set y, 0 [31]"),
        pytest.param(0x3F81, State(), 1, id="wait 1 gpio 1 [31] when condition not met"),
        pytest.param(0x3F81, State(pin_values=2), 32, id="wait 1 gpio 1 [31] when condition met"),
    ],
)
# fmt: on
def test_instruction_consumes_expected_clock_cycles(
    opcode, initial_state, expected_clock_cycles
):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state.clock == expected_clock_cycles
