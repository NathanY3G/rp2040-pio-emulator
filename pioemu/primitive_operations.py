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
from dataclasses import replace
from .state import ShiftRegister


def copy_data_to_isr(data, state):
    """Copies the given data into the input shift register."""

    return replace(state, input_shift_register=ShiftRegister(data, 0))


def copy_data_to_osr(data, state):
    """Copies the given data into the output shift register."""

    return replace(state, output_shift_register=ShiftRegister(data, 0))


def copy_data_to_pin_directions(data, state):
    """Copies the given data into the pin directions register."""

    return replace(state, pin_directions=data)


def copy_data_to_pins(data, state):
    """Copies the given data into the pin values register."""

    return replace(state, pin_values=data)


def copy_data_to_program_counter(data, state):
    """Copies the given data into the program counter."""

    return replace(state, program_counter=data)


def copy_data_to_x(data, state):
    """Copies the given data into the X scratch register."""

    return replace(state, x_register=data)


def copy_data_to_y(data, state):
    """Copies the given data into the Y scratch register."""

    return replace(state, y_register=data)
