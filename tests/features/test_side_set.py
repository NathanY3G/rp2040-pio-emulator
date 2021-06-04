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


def test_side_set_is_not_mistaken_for_delay():
    opcode = 0xF001  # set pins, 1 side 1

    _, new_state = next(
        emulate(
            [opcode],
            stop_when=clock_cycles_reached(1),
            side_set_base=1,
            side_set_count=1,
        )
    )

    assert new_state.clock == 1


@pytest.mark.parametrize(
    "opcode, pin_base, pin_count, initial_pin_values, expected_pin_values",
    [
        pytest.param(0xE001, 1, 1, 0, 1, id="set pins, 1 side 0"),
        pytest.param(0xF001, 1, 1, 0, 3, id="set pins, 1 side 1"),
        pytest.param(0x0000, 1, 1, 3, 1, id="jmp 0 side 0"),
        pytest.param(0x1000, 1, 1, 1, 3, id="jmp 0 side 1"),
        pytest.param(0xBC42, 5, 3, 0, 0xE0, id="nop side 7"),
    ],
)
def test_side_set_changes_pin_values(
    opcode, pin_base, pin_count, initial_pin_values, expected_pin_values
):
    _, new_state = next(
        emulate(
            [opcode],
            initial_state=State(pin_values=initial_pin_values),
            stop_when=clock_cycles_reached(1),
            side_set_base=pin_base,
            side_set_count=pin_count,
        )
    )

    assert new_state.pin_values == expected_pin_values
