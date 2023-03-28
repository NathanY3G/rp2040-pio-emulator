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

from pioemu import ShiftRegister


# fmt: off
@pytest.mark.parametrize(
    "initial_state, bit_count, data_in, expected_state, expected_shift_result",
    [
        pytest.param(
            ShiftRegister(0xBEEB_0000, 0), 8, 0, ShiftRegister(0xEB00_0000, 8), 0x0000_00BE,
        ),
        pytest.param(
            ShiftRegister(0xFFFF_FFFF, 0), 32, 0, ShiftRegister(0x0000_0000, 32), 0xFFFF_FFFF,
        ),
        pytest.param(
            ShiftRegister(0x8000_0000, 5), 3, 0, ShiftRegister(0x0000_0000, 8), 4
        ),
        pytest.param(
            ShiftRegister(0x5555_AAAA, 4), 3, 14, ShiftRegister(0xAAAD5556, 7), 2
        ),

        # TODO - Test the actual behaviour of the RP2040 silicon
        pytest.param(
            ShiftRegister(0xA0000_0000, 31), 32, 0, ShiftRegister(0x0000_0000, 32), 0xA0000_0000,
        ),
    ],
)
# fmt: on
def test_shift_left(
    initial_state: State, bit_count: int, data_in: int, expected_state: State, expected_shift_result: int
):
    new_state, shift_result = initial_state.shift_left(bit_count, data_in)

    assert new_state.contents == expected_state.contents
    assert new_state.counter == expected_state.counter
    assert shift_result == expected_shift_result


# fmt: off
@pytest.mark.parametrize(
    "initial_state, bit_count, data_in, expected_state, expected_shift_result",
    [
        pytest.param(
            ShiftRegister(0x0000_01FF, 0), 8, 0, ShiftRegister(0x0000_0001, 8), 0x0000_00FF,
        ),
        pytest.param(
            ShiftRegister(0xFFFF_FFFF, 0), 32, 0, ShiftRegister(0x0000_0000, 32), 0xFFFF_FFFF,
        ),
        pytest.param(
            ShiftRegister(0x0000_0004, 5), 3, 0, ShiftRegister(0x0000_0000, 8), 4
        ),
        pytest.param(
            ShiftRegister(0xDEAD_BEEF, 0), 16, 0x0123_CAFE, ShiftRegister(0xCAFE_DEAD, 16), 0x0000_BEEF
        ),

        # TODO - Test the actual behaviour of the RP2040 silicon
        pytest.param(
            ShiftRegister(0x0000_0005, 31), 32, 0, ShiftRegister(0x0000_0000, 32), 5
        ),
    ],
)
# fmt: on
def test_shift_right(
    initial_state: State, bit_count: int, data_in: int, expected_state: State, expected_shift_result: int
):
    new_state, shift_result = initial_state.shift_right(bit_count, data_in)

    assert new_state.contents == expected_state.contents
    assert new_state.counter == expected_state.counter
    assert shift_result == expected_shift_result


@pytest.mark.parametrize(
    "lhs, rhs, expected_result",
    [
        (ShiftRegister(0, 0), ShiftRegister(0, 0), True),
        (ShiftRegister(0, 0), ShiftRegister(0xFFFF_FFFF, 0), False),
        (ShiftRegister(0, 0), ShiftRegister(0, 32), False),
    ],
)
def test_equality_operator(lhs, rhs, expected_result):
    assert (lhs == rhs) == expected_result


def test_printable_representation():
    assert repr(ShiftRegister(42, 0)) == "ShiftRegister(contents=42, counter=0)"
