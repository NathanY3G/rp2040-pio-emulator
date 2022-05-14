# Copyright 2021, 2022 Nathan Young
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


def test_pin_values_follow_input_source():
    initial_state = State(pin_values=0)
    pin_values_over_time = [0x0000_FFFF, 0xFFFF_0000, 0xFFFF_FFFF]

    actual_pin_values = [
        state.pin_values
        for _, state in emulate(
            [0x0000],  # jmp 0
            stop_when=clock_cycles_reached(len(pin_values_over_time)),
            initial_state=initial_state,
            input_source=lambda clock: pin_values_over_time[clock],
        )
    ]

    assert actual_pin_values == pin_values_over_time


def test_input_source_does_not_impact_output_pins():
    initial_state = State(pin_directions=0xFFFF_0000, pin_values=0)

    _, new_state = next(
        emulate(
            [0x0000],  # jmp 0
            stop_when=clock_cycles_reached(1),
            initial_state=initial_state,
            input_source=lambda _: 0xFFFF_FFFF,
        )
    )

    assert new_state.pin_values == 0x0000_FFFF
