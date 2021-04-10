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
from collections import deque
from pioemu import State
from tests.support import emulate_single_instruction


@pytest.mark.parametrize(
    "opcode, expected_register_value, expected_counter_value",
    [
        pytest.param(0x6023, 0x1FFF_FFFF, 3, id="out x, 3"),
        pytest.param(0x6040, 0x0000_0000, 32, id="out y, 32"),
    ],
)
def test_out_updates_shift_register(
    opcode, expected_register_value, expected_counter_value
):
    initial_state = State(output_shift_register=0xFFFF_FFFF, output_shift_counter=0)

    new_state = emulate_single_instruction(opcode, initial_state)

    assert new_state.output_shift_register == expected_register_value
    assert new_state.output_shift_counter == expected_counter_value


def test_out_updates_pin_directions():
    initial_state = State(
        pin_directions=0, output_shift_register=0x0000_0004, output_shift_counter=0
    )

    new_state = emulate_single_instruction(0x6083, initial_state)  # out pindirs, 3

    assert new_state.pin_directions == 4


def test_out_updates_pin_values():
    initial_state = State(
        pin_values=0, output_shift_register=0x0000_01FF, output_shift_counter=0
    )

    new_state = emulate_single_instruction(0x6008, initial_state)  # out pins, 8

    assert new_state.pin_values == 0xFF


def test_out_updates_x_register():
    initial_state = State(
        x_register=0, output_shift_register=0xFFFF_FFFF, output_shift_counter=0
    )

    new_state = emulate_single_instruction(0x6023, initial_state)  # out x, 3

    assert new_state.x_register == 7


def test_out_updates_y_register():
    initial_state = State(
        y_register=0, output_shift_register=0xFFFF_FFFF, output_shift_counter=0
    )

    new_state = emulate_single_instruction(0x6040, initial_state)  # out y, 32

    assert new_state.y_register == 0xFFFF_FFFF


@pytest.mark.parametrize(
    "opcode, expected_clock_cycles",
    [
        pytest.param(0x6283, 3, id="out pindirs, 3 [2]"),
        pytest.param(0x6708, 8, id="out pins, 8 [7]"),
        pytest.param(0x6023, 1, id="out x, 3"),
        pytest.param(0x7f40, 32, id="out y, 32 [31]"),
    ],
)
def test_out_consumes_expected_clock_cycles(opcode, expected_clock_cycles):
    new_state = emulate_single_instruction(opcode, State(output_shift_counter=0))

    assert new_state.clock == expected_clock_cycles
