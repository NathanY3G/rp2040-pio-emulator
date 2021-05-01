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


def out_pindirs(bit_count, state):
    new_register_value, new_counter_value, shift_result = _shift_output_shift_register(
        state.output_shift_register, state.output_shift_counter, bit_count
    )

    return next_instruction(
        replace(
            state,
            pin_directions=shift_result,
            output_shift_register=new_register_value,
            output_shift_counter=new_counter_value,
        )
    )


def out_pins(bit_count, state):
    new_register_value, new_counter_value, shift_result = _shift_output_shift_register(
        state.output_shift_register, state.output_shift_counter, bit_count
    )

    return next_instruction(
        replace(
            state,
            pin_values=shift_result,
            output_shift_register=new_register_value,
            output_shift_counter=new_counter_value,
        )
    )


def out_x(bit_count, state):
    new_register_value, new_counter_value, shift_result = _shift_output_shift_register(
        state.output_shift_register, state.output_shift_counter, bit_count
    )

    return next_instruction(
        replace(
            state,
            x_register=shift_result,
            output_shift_register=new_register_value,
            output_shift_counter=new_counter_value,
        )
    )


def out_y(bit_count, state):
    new_register_value, new_counter_value, shift_result = _shift_output_shift_register(
        state.output_shift_register, state.output_shift_counter, bit_count
    )

    return next_instruction(
        replace(
            state,
            y_register=shift_result,
            output_shift_register=new_register_value,
            output_shift_counter=new_counter_value,
        )
    )


def _shift_output_shift_register(register_value, counter_value, bit_count):
    if bit_count == 0:
        bit_count = 32

    bit_mask = (1 << bit_count) - 1
    shift_result = register_value & bit_mask

    return (
        register_value >> bit_count,
        counter_value + bit_count,
        shift_result,
    )
