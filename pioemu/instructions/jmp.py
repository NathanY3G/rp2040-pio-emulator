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
from ..conditions import x_register_not_equal_to_zero, y_register_not_equal_to_zero


def jmp(condition, address, state):
    if condition(state):
        return replace(state, program_counter=address)
    else:
        return next_instruction(state)


def jmp_when_x_is_non_zero_and_post_decrement(address, state):
    return replace(
        jmp(x_register_not_equal_to_zero, address, state),
        x_register=state.x_register - 1,
    )


def jmp_when_y_is_non_zero_and_post_decrement(address, state):
    return replace(
        jmp(y_register_not_equal_to_zero, address, state),
        y_register=state.y_register - 1,
    )
