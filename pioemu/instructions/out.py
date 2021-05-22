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


def out_null(shifter, bit_count, state):
    """Shift bits out of the output shift register and discard them"""
    new_osr, _ = shifter(state.output_shift_register, bit_count)

    return replace(state, output_shift_register=new_osr)


def out_pindirs(shifter, bit_count, state):
    """Shift bits out of the output shift register and write those bits to the pin directions"""
    new_osr, shift_result = shifter(state.output_shift_register, bit_count)

    return replace(
        state,
        pin_directions=shift_result,
        output_shift_register=new_osr,
    )


def out_pins(shifter, bit_count, state):
    """Shift bits out of the output shift register and write those bits to the pins"""
    new_osr, shift_result = shifter(state.output_shift_register, bit_count)

    return replace(
        state,
        pin_values=shift_result,
        output_shift_register=new_osr,
    )


def out_x(shifter, bit_count, state):
    """Shift bits out of the output shift register and write those bits to X"""
    new_osr, shift_result = shifter(state.output_shift_register, bit_count)

    return replace(
        state,
        x_register=shift_result,
        output_shift_register=new_osr,
    )


def out_y(shifter, bit_count, state):
    """Shift bits out of the output shift register and write those bits to Y"""
    new_osr, shift_result = shifter(state.output_shift_register, bit_count)

    return replace(
        state,
        y_register=shift_result,
        output_shift_register=new_osr,
    )
