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


def test_stop_when_requires_value():
    with pytest.raises(ValueError):
        next(emulate([0x0000], stop_when=None))


def test_emulation_stops_when_unsupported_opcode_is_reached():
    with pytest.raises(StopIteration):
        next(emulate([0xE0E0], stop_when=lambda opcode, _: False))


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
def test_program_counter_is_incremented(opcode):
    initial_state = State(program_counter=0)

    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state.program_counter == 1
