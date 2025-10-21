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


def update_bits_32(value, new_value, bit_position=0, bit_count=32):
    """Updates an existing value with up to 32 bits from another value."""

    bit_mask = ((1 << bit_count) - 1) << bit_position

    return (
        (value & ~bit_mask) | ((new_value << bit_position) & bit_mask)
    ) & 0xFFFF_FFFF
