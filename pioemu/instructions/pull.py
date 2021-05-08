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


def pull_blocking(not_used, state):
    if len(state.transmit_fifo) > 0:
        return next_instruction(
            replace(
                state,
                output_shift_register=ShiftRegister(state.transmit_fifo.pop(), 0),
            )
        )
    else:
        return state


def pull_nonblocking(not_used, state):
    if len(state.transmit_fifo) > 0:
        return next_instruction(
            replace(
                state,
                output_shift_register=ShiftRegister(state.transmit_fifo.pop(), 0),
            )
        )
    else:
        return next_instruction(
            replace(state, output_shift_register=ShiftRegister(state.x_register, 0))
        )
