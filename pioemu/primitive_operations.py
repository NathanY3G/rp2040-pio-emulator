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


def read_from_isr(state):
    """Reads the contents of the input shift register."""

    return state.input_shift_register.contents


def shift_into_isr(data_supplier, shift_method, bit_count, state):
    """Shifts the given data into the input shift register."""

    new_isr, _ = shift_method(
        state.input_shift_register, bit_count, data_supplier(state)
    )

    return replace(state, input_shift_register=new_isr)


def read_from_osr(state):
    """Reads the contents of the output shift register."""

    return state.output_shift_register.contents


def shift_from_osr(shift_method, bit_count, state):
    """Shift the requested number of bits out of the output shift register."""

    new_osr, shift_result = shift_method(state.output_shift_register, bit_count)

    return (
        replace(
            state,
            output_shift_register=new_osr,
        ),
        shift_result,
    )


def read_from_pin_directions(state):
    """Reads the contents of the pin direction register."""

    return state.pin_directions


def read_from_pins(state):
    """Reads the contents of the pin values register."""

    return state.pin_values


def read_from_x(state):
    """Reads the contents of the X scratch register."""

    return state.x_register


def read_from_y(state):
    """Reads the contents of the Y scratch register."""

    return state.y_register


def write_to_isr(data_supplier, state):
    """Copies the given data into the input shift register."""

    return replace(
        state, input_shift_register=ShiftRegister(data_supplier(state) & 0xFFFF_FFFF, 0)
    )


def write_to_osr(data_supplier, state):
    """Copies the given data into the output shift register."""

    return replace(
        state,
        output_shift_register=ShiftRegister(data_supplier(state) & 0xFFFF_FFFF, 0),
    )


def write_to_pin_directions(data_supplier, state):
    """Copies the given data into the pin directions register."""

    return replace(state, pin_directions=data_supplier(state) & 0xFFFF_FFFF)


def write_to_pins(data_supplier, state):
    """Copies the given data into the pin values register."""

    return replace(state, pin_values=data_supplier(state) & 0xFFFF_FFFF)


def write_to_program_counter(data_supplier, state):
    """Copies the given data into the program counter."""

    return replace(state, program_counter=data_supplier(state) & 0x1F)


def write_to_x(data_supplier, state):
    """Copies the given data into the X scratch register."""

    return replace(state, x_register=data_supplier(state) & 0xFFFF_FFFF)


def write_to_y(data_supplier, state):
    """Copies the given data into the Y scratch register."""

    return replace(state, y_register=data_supplier(state) & 0xFFFF_FFFF)


def write_to_null(data_supplier, state):
    """Discards the given data."""

    _ = data_supplier(state)

    return state


def supplies_value(value):
    """Creates a function that returns the specified value when invoked."""

    return lambda _: value
