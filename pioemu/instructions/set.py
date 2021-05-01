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


def set_pins(data, state):
    return next_instruction(replace(state, pin_values=data))


def set_pindirs(data, state):
    return next_instruction(replace(state, pin_directions=data))


def set_x(data, state):
    return next_instruction(replace(state, x_register=data))


def set_y(data, state):
    return next_instruction(replace(state, y_register=data))
