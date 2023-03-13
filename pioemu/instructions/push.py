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
from pioemu.state import ShiftRegister
from pioemu.conditions import receive_fifo_not_full

def push_blocking(state):
    state.receive_fifo.push(state.input_shift_register.contents)
    return replace(state, input_shift_register=ShiftRegister(0, 0))

def push_nonblocking(state):
    if receive_fifo_not_full:
        push_blocking(state)
    else:
        return replace(state, input_shift_register=ShiftRegister(0, 0))
