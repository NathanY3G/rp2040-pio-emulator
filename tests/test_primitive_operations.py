# Copyright 2022 Nathan Young
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
from pioemu import State
from pioemu.primitive_operations import (
    read_from_pin_directions,
    shift_from_osr,
    write_to_null,
)
from pioemu.shift_register import ShiftRegister


def test_read_from_pin_directions():
    pin_directions = read_from_pin_directions(State(pin_directions=0x0000_FFFF))

    assert pin_directions == 0x0000_FFFF


def test_shift_from_osr():
    _, shift_result = shift_from_osr(
        ShiftRegister.shift_right, 3, State(output_shift_register=ShiftRegister(15, 0))
    )

    assert shift_result == 7


def test_write_to_null_drains_data_provider():
    data_source = [1]
    data_supplier = lambda _: data_source.pop()

    _ = write_to_null(data_supplier, State())

    assert len(data_source) == 0


def test_write_to_null_preserves_state():
    initial_state = State()
    data_supplier = lambda _: 1

    new_state = write_to_null(data_supplier, initial_state)

    assert new_state == initial_state
