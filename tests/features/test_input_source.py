# Copyright 2023 Nathan Young
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

from ..opcodes import Opcodes


@pytest.mark.parametrize(
    "pin_directions, pin_values, value_from_input_source, expected_pin_values",
    [
        pytest.param(
            0xFFFF_FFFF,
            0xFFFF_0000,
            0x0000_FFFF,
            0xFFFF_0000,
            id="output pins should not be affected",
        ),
        pytest.param(
            0xFFFF_0000,
            0x5555_AAAA,
            0xAAAA_5555,
            0x5555_5555,
            id="input pins should be updated",
        ),
    ],
)
def test_updating_of_pin_values_from_input_source(
    pin_directions, pin_values, value_from_input_source, expected_pin_values
):
    initial_state = State(pin_directions=pin_directions, pin_values=pin_values)

    _, new_state = next(
        emulate(
            [Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
            initial_state=initial_state,
            input_source=lambda _: value_from_input_source,
        )
    )

    assert new_state.pin_values == expected_pin_values


def test_pin_values_follow_input_source():
    input_values_over_time = [0x0000_FFFF, 0xFFFF_0000, 0xFFFF_FFFF]

    pin_values_series = [
        state.pin_values
        for _, state in emulate(
            [Opcodes.nop()],
            stop_when=clock_cycles_reached(len(input_values_over_time)),
            input_source=lambda clock: input_values_over_time[clock],
        )
    ]

    assert pin_values_series == input_values_over_time
