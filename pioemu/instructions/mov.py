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
from pioemu.state import ShiftRegister
from .common import next_instruction


def mov_into_isr(source_value, state):
    """Copy data from source to input shift register"""
    return next_instruction(
        replace(state, input_shift_register=ShiftRegister(source_value, 0))
    )


def mov_into_osr(source_value, state):
    """Copy data from source to output shift register"""
    return next_instruction(
        replace(state, output_shift_register=ShiftRegister(source_value, 0))
    )


def mov_into_pins(source_value, state):
    """Copy data from source to pins"""
    return next_instruction(replace(state, pin_values=source_value))


def mov_into_x(source_value, state):
    """Copy data from source to X"""
    return next_instruction(replace(state, x_register=source_value))


def mov_into_y(source_value, state):
    """Copy data from source to Y"""
    return next_instruction(replace(state, y_register=source_value))
