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
from pioemu import clock_cycles_reached, emulate, State


def test_emulation_stops_when_unsupported_opcode_is_reached():
    with pytest.raises(StopIteration):
        next(emulate([0xE0E0]))


def test_program_counter_is_incremented():
    opcodes = [0xE021, 0xE022, 0xE022]  # set x, 1 to 3

    program_counter_changes = [
        state.program_counter
        for state, _ in emulate(
            opcodes, stop_condition=lambda state: state.program_counter > 2
        )
    ]

    assert program_counter_changes == [0, 1, 2]


def test_executes_instructions_until_stop_condition_met():
    opcodes = [0xE042, 0x0000]  # set y, 2 and jmp

    *_, clock_cycles = (
        state.clock
        for _, state in emulate(opcodes, stop_condition=clock_cycles_reached(3))
    )

    assert clock_cycles == 3
