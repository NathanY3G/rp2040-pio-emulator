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
from pioemu import ShiftRegister
from pioemu.shifter import shift_right


# fmt: off
@pytest.mark.parametrize(
    "initial_state, bit_count, expected_state, expected_shift_result",
    [
        pytest.param(
            ShiftRegister(0x0000_01FF, 0), 8, ShiftRegister(0x0000_0001, 8), 0x0000_00FF,
        ),
        pytest.param(
            ShiftRegister(0xFFFF_FFFF, 0), 32, ShiftRegister(0x0000_0000, 32), 0xFFFF_FFFF,
        ),
        pytest.param(
            ShiftRegister(0x0000_0004, 5), 3, ShiftRegister(0x0000_0000, 8), 4
        ),

        # TODO - Test the actual behaviour of the RP2040 silicon
        pytest.param(
            ShiftRegister(0x0000_0005, 31), 32, ShiftRegister(0x0000_0000, 32), 5
        ),
    ],
)
# fmt: on
def test_shift_right(initial_state, bit_count, expected_state, expected_shift_result):
    new_state, shift_result = shift_right(initial_state, bit_count)

    assert new_state == expected_state
    assert shift_result == expected_shift_result
