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
from functools import partial


def emulate_opcodes(opcodes):
    for opcode in opcodes:
        instruction = opcode & 0xE0E0
        data_field = opcode & 0x1F

        if instruction == 0x0:
            yield partial(jmp_always, data_field)
        if instruction == 0x2020:
            yield partial(wait_for_gpio_low, data_field)
        elif instruction == 0x2080:
            yield partial(wait_for_gpio_high, data_field)
        elif instruction == 0xE080:
            yield partial(set_pindirs, data_field)
        elif instruction == 0xE000:
            yield partial(set_pins, data_field)
        elif instruction == 0xE020:
            yield partial(set_x, data_field)
        elif instruction == 0xE040:
            yield partial(set_y, data_field)
        else:
            yield None


def next_instruction(state):
    return replace(state, program_counter=state.program_counter + 1)


def jmp_always(address, state):
    return replace(state, program_counter=address)


def set_pins(data, state):
    return next_instruction(replace(state, pin_values=(state.pin_values | data) & 0x1F))


def set_pindirs(data, state):
    return next_instruction(
        replace(state, pin_directions=(state.pin_directions | data) & 0x1F)
    )


def set_x(data, state):
    return next_instruction(replace(state, x_register=data))


def set_y(data, state):
    return next_instruction(replace(state, y_register=data))


def wait_for_gpio_low(pin_number, state):
    bit_mask = 1 << pin_number

    if not state.pin_values & bit_mask:
        return next_instruction(state)
    else:
        return state


def wait_for_gpio_high(pin_number, state):
    bit_mask = 1 << pin_number

    if state.pin_values & bit_mask:
        return next_instruction(state)
    else:
        return state
