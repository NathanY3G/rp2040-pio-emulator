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
from .state import ShiftRegister


def shift_left(shift_register, bit_count):
    """Shifts the most significant bits out of the shift register by the given
    amount.

    Parameters:
    shift_register (ShiftRegister): The shift register to operate on.
    bit_count (int): The number of bits to shift out.

    Returns:
    (ShiftRegister, int): New representation of the register and the result.
    """

    shift_result = shift_register.contents >> (32 - bit_count)
    new_contents = (shift_register.contents << bit_count) & 0xFFFF_FFFF

    return (
        ShiftRegister(new_contents, min(shift_register.counter + bit_count, 32)),
        shift_result,
    )


def shift_right(shift_register, bit_count):
    """Shifts the least significant bits out of the shift register by the given
    amount.

    Parameters:
    shift_register (ShiftRegister): The shift register to operate on.
    bit_count (int): The number of bits to shift out.

    Returns:
    (ShiftRegister, int): New representation of the register and the result.
    """

    bit_mask = (1 << bit_count) - 1

    shift_result = shift_register.contents & bit_mask
    new_contents = (shift_register.contents >> bit_count) & 0xFFFF_FFFF

    return (
        ShiftRegister(new_contents, min(shift_register.counter + bit_count, 32)),
        shift_result,
    )
