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
from pioemu import emulate_opcodes, State


def test_emulation_stops_when_unsupported_opcode_is_reached():
    with pytest.raises(StopIteration):
        next(emulate_opcodes([0xE0E0]))


def test_program_counter_is_incremented():
    opcodes = [0xE042, 0x0000]  # set y, 2 and jmp

    program_counter_changes = [
        state.program_counter
        for _, state in emulate_opcodes(opcodes, max_clock_cycles=3)
    ]

    assert program_counter_changes == [1, 0, 1]


def test_runs_until_maximum_clock_cycles_reached():
    opcodes = [0xE042, 0x0000]  # set y, 2 and jmp

    clock_changes = [
        state.clock for _, state in emulate_opcodes(opcodes, max_clock_cycles=3)
    ]

    assert clock_changes == [1, 2, 3]
