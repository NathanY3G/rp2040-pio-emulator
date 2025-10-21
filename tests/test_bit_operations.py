# Copyright 2025 Nathan Young
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

from pioemu.bit_operations import update_bits_32


@pytest.mark.parametrize(
    "existing_value, new_value, bit_position, bit_count, expected_value",
    [
        pytest.param(0x0000_0000, 0xFFFF_FFFF, 0, 32, 0xFFFF_FFFF),
        pytest.param(0xFFFF_FFFF, 0x0000_0000, 0, 32, 0x0000_0000),
        pytest.param(0x0000_0000, 0xFFFF_FFFF, 0, 1, 0x0000_0001),
        pytest.param(0x0000_0000, 0xFFFF_FFFF, 31, 1, 0x8000_0000),
        pytest.param(0xFFFF_FFFF, 0x0000_0000, 11, 20, 0x8000_07FF),
        pytest.param(0x0000_0000, 0xFFFF_FFFF, 31, 1, 0x8000_0000),
        pytest.param(0xDEAD_BEEF, 0x0000_F00D, 16, 16, 0xF00D_BEEF),
    ],
)
def test_update_bits_32(
    existing_value, new_value, bit_position, bit_count, expected_value
):
    assert (
        update_bits_32(existing_value, new_value, bit_position, bit_count)
        == expected_value
    )
