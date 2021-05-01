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
from .common import next_instruction


def wait_for_gpio_low(pin_number, state):
    bit_mask = 1 << pin_number
    return next_instruction(state) if not state.pin_values & bit_mask else state


def wait_for_gpio_high(pin_number, state):
    bit_mask = 1 << pin_number
    return next_instruction(state) if state.pin_values & bit_mask else state
