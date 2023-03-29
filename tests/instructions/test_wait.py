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

from pioemu import State

from ..support import emulate_single_instruction


@pytest.mark.parametrize(
    "opcode, initial_state",
    [
        pytest.param(0x2080, State(pin_values=0), id="wait 1 gpio, 0"),
        pytest.param(0x2020, State(pin_values=1), id="wait 0 pin, 0"),
    ],
)
def test_wait_stalls_when_condition_not_met(opcode: int, initial_state: State):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state.program_counter == 0


@pytest.mark.parametrize(
    "opcode, initial_state",
    [
        pytest.param(0x2080, State(pin_values=1), id="wait 1 gpio, 0"),
        pytest.param(0x2020, State(pin_values=0), id="wait 0 pin, 0"),
    ],
)
def test_wait_advances_when_condition_met(opcode: int, initial_state: State):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state.program_counter == 1
