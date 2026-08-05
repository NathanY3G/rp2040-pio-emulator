# Copyright 2021, 2022, 2023 Nathan Young
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
from dataclasses import replace

import pytest

from pioemu import State

from ..support import emulate_single_instruction


def test_set_pins_directions():
    opcode = 0xFF81  # set pindirs, 1 [31]

    _, new_state = emulate_single_instruction(
        opcode, initial_state=State(pin_directions=0x1F)
    )

    assert new_state.pin_directions == 1


def test_set_pins_values():
    opcode = 0xFF1F  # set pins, 31 [31]

    _, new_state = emulate_single_instruction(
        opcode, initial_state=State(pin_values=30)
    )

    assert new_state.pin_values == 31


def test_set_x_register():
    opcode = 0xE03F  # set x, 31

    _, new_state = emulate_single_instruction(opcode, initial_state=State(x_register=0))

    assert new_state.x_register == 31


def test_set_y_register():
    opcode = 0xE042  # set y, 2

    _, new_state = emulate_single_instruction(opcode, initial_state=State(y_register=0))

    assert new_state.y_register == 2


# fmt: off
@pytest.mark.parametrize("opcode, set_base, set_count, initial_state, expected_state", [
    pytest.param(
        0xE001,  # set pins, 1
        3,
        1,
        State(pin_values=0x0000_0000),
        State(pin_values=0x0000_0008),
        id="set pins honours set_base and set_count",
    ),
    pytest.param(
        0xE003,  # set pins, 3 (0b11)
        0,
        1,
        State(pin_values=0x0000_0000),
        State(pin_values=0x0000_0001),
        id="set pins masks bits outside set_count",
    ),
])
# fmt: on
def test_set_to_pins(
    opcode, set_base: int, set_count: int, initial_state: State, expected_state: State
):
    _, new_state = emulate_single_instruction(
        opcode, initial_state=initial_state, set_base=set_base, set_count=set_count
    )

    assert replace(new_state, clock=0) == expected_state


# fmt: off
@pytest.mark.parametrize("opcode, set_base, set_count, initial_state, expected_state", [
    pytest.param(
        0xE081,  # set pindirs, 1
        3,
        1,
        State(pin_directions=0x0000_0000),
        State(pin_directions=0x0000_0008),
        id="set pindirs honours set_base and set_count",
    ),
    pytest.param(
        0xE083,  # set pindirs, 3 (0b11)
        0,
        1,
        State(pin_directions=0x0000_0000),
        State(pin_directions=0x0000_0001),
        id="set pindirs masks bits outside set_count",
    ),
])
# fmt: on
def test_set_to_pin_directions(
    opcode, set_base: int, set_count: int, initial_state: State, expected_state: State
):
    _, new_state = emulate_single_instruction(
        opcode, initial_state=initial_state, set_base=set_base, set_count=set_count
    )

    assert replace(new_state, clock=0) == expected_state
