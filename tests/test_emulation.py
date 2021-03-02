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
        emulate_opcode(0xE0E0, State())


def test_program_counter_is_incremented():
    initial_state = State(program_counter=0)

    new_state = emulate_opcode(0xE081, initial_state)  # set pindirs, 1

    assert new_state.program_counter == 1


def test_emulation_stops_after_last_opcode():
    opcodes = [0xE021, 0xE022, 0xE023]  # set x, 1 to 3 inclusive
    initial_state = State()

    x_register_changes = [
        state.x_register for _, state in emulate_opcodes(opcodes, initial_state)
    ]

    assert x_register_changes == [1, 2, 3]


def test_jump_always_forward():
    initial_state = State(program_counter=3)

    new_state = emulate_opcode(0x0007, initial_state)  # jmp

    assert new_state.program_counter == 7


def test_set_pins_directions():
    initial_state = State(pin_directions=0x1F)

    new_state = emulate_opcode(0xFF81, initial_state)  # set pindirs, 1 [31]

    assert new_state.pin_directions == 1


def test_set_pins_values():
    initial_state = State(pin_values=30)

    new_state = emulate_opcode(0xFF1F, initial_state)  # set pins, 31 [31]

    assert new_state.pin_values == 31


def test_set_x_register():
    initial_state = State(x_register=0)

    new_state = emulate_opcode(0xE03F, initial_state)  # set x, 31

    assert new_state.x_register == 31


def test_set_y_register():
    initial_state = State(y_register=0)

    new_state = emulate_opcode(0xE042, initial_state)  # set y, 2

    assert new_state.y_register == 2


@pytest.mark.parametrize(
    "opcode, initial_state",
    [
        pytest.param(0x2080, State(pin_values=0), id="wait 1 gpio, 0"),
        pytest.param(0x2020, State(pin_values=1), id="wait 0 pin, 0"),
    ],
)
def test_wait_stalls_when_condition_not_met(opcode, initial_state):
    new_state = emulate_opcode(opcode, initial_state)

    assert new_state.program_counter == 0


@pytest.mark.parametrize(
    "opcode, initial_state",
    [
        pytest.param(0x2080, State(pin_values=1), id="wait 1 gpio, 0"),
        pytest.param(0x2020, State(pin_values=0), id="wait 0 pin, 0"),
    ],
)
def test_wait_advances_when_condition_met(opcode, initial_state):
    new_state = emulate_opcode(opcode, initial_state)

    assert new_state.program_counter == 1


def emulate_opcode(opcode, initial_state):
    _, new_state = next(emulate_opcodes([opcode], initial_state))
    return new_state
