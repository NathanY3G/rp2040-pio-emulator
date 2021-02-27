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
from pioemu import emulate_opcodes, State


def test_none_is_returned_for_unsupported_opcodes():
    instruction = emulate_opcode(0xE0E0)
    assert instruction is None


def test_program_counter_is_incremented():
    state = State(program_counter=0)
    instruction = emulate_opcode(0xE081)  # set pindirs, 1

    state = instruction(state)

    assert state.program_counter == 1


def test_emulation_stops_after_last_opcode():
    opcodes = [0xE021, 0xE022, 0xE023]  # set x, 1 to 3 inclusive
    state = State()

    for instruction in emulate_opcodes(opcodes):
        state = instruction(state)

    assert state.x_register == 3


def test_set_pins_directions():
    instruction = emulate_opcode(0xFF81)  # set pindirs, 1 [31]

    state = instruction(State())

    assert state.pin_directions == 1


def test_set_pins_values():
    instruction = emulate_opcode(0xFF1F)  # set pins, 31 [31]

    state = instruction(State())

    assert state.pin_values == 31


def test_set_x_register():
    instruction = emulate_opcode(0xE03F)  # set x, 31

    state = instruction(State())

    assert state.x_register == 31


def test_set_y_register():
    instruction = emulate_opcode(0xE042)  # set y, 2

    state = instruction(State())

    assert state.y_register == 2


def emulate_opcode(opcode):
    return next(emulate_opcodes([opcode]))
