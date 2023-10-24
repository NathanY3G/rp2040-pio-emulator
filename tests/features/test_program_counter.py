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
import pytest

from pioemu.state import State
from tests.support import emulate_single_instruction


@pytest.mark.parametrize(
    "opcode",
    [
        pytest.param(0xE022, id="set x, 2"),
        pytest.param(0x6283, id="out pindirs, 3 [2]"),
        pytest.param(0x6708, id="out pins, 8 [7]"),
        pytest.param(0x6023, id="out x, 3"),
        pytest.param(0x7F40, id="out y, 32 [31]"),
    ],
)
def test_program_counter_is_incremented(opcode: int):
    initial_state = State(program_counter=0)

    _, new_state = emulate_single_instruction(
        opcode, initial_state=initial_state, advance_program_counter=True
    )

    assert new_state.program_counter == 1


@pytest.mark.parametrize(
    "opcode, initial_state",
    [pytest.param(0x2080, State(pin_values=0), id="wait 1 gpio, 0")],
)
def test_program_counter_remains_unchanged_when_stalled(
    opcode: int, initial_state: State
):
    previous_state, new_state = emulate_single_instruction(
        opcode, initial_state=initial_state
    )

    assert new_state.clock == previous_state.clock + 1
    assert new_state.program_counter == previous_state.program_counter
