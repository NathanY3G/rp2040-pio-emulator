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
import pytest

from pioemu import State, clock_cycles_reached, emulate

from .opcodes import Opcodes
from .support import emulate_single_instruction


def test_stop_when_requires_value():
    with pytest.raises(ValueError):
        next(emulate([0x0000], stop_when=None))


def test_emulation_stops_when_unsupported_opcode_is_reached():
    with pytest.raises(StopIteration):
        next(emulate([0xE0E0], stop_when=lambda opcode, _: False))


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


def test_input_source_does_not_impact_output_pins():
    initial_state = State(pin_directions=0xFFFF_0000, pin_values=0)

    _, new_state = next(
        emulate(
            [Opcodes.nop()],
            stop_when=clock_cycles_reached(1),
            initial_state=initial_state,
            input_source=lambda _: 0xFFFF_FFFF,
        )
    )

    assert new_state.pin_values == 0x0000_FFFF
