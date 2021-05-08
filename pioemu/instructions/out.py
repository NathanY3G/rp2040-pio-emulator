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
from dataclasses import replace
from .common import next_instruction
import pioemu.shifter as shifter


def out_pindirs(bit_count, state):
    new_osr, shift_result = _shift_right(state.output_shift_register, bit_count)

    return next_instruction(
        replace(state, pin_directions=shift_result, output_shift_register=new_osr,)
    )


def out_pins(bit_count, state):
    new_osr, shift_result = _shift_right(state.output_shift_register, bit_count)

    return next_instruction(
        replace(state, pin_values=shift_result, output_shift_register=new_osr,)
    )


def out_x(bit_count, state):
    new_osr, shift_result = _shift_right(state.output_shift_register, bit_count)

    return next_instruction(
        replace(state, x_register=shift_result, output_shift_register=new_osr,)
    )


def out_y(bit_count, state):
    new_osr, shift_result = _shift_right(state.output_shift_register, bit_count)

    return next_instruction(
        replace(state, y_register=shift_result, output_shift_register=new_osr,)
    )


def _shift_right(shift_register, bit_count):
    if bit_count == 0:
        return shifter.shift_right(shift_register, 32)
    else:
        return shifter.shift_right(shift_register, bit_count)
