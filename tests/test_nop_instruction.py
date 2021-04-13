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
    pytest.param(0xA042, State(), State(clock=1, program_counter=1), id="nop"),
    pytest.param(0xBF42, State(), State(clock=32, program_counter=1), id="nop [31]"),
]


@pytest.mark.parametrize("opcode, initial_state, expected_state", instructions_to_test)
def test_no_operation(opcode, initial_state, expected_state):
    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state == expected_state
