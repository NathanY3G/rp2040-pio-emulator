# Copyright 2023 Aaronjamt
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
from collections import deque
from dataclasses import replace
from pioemu.shift_register import ShiftRegister
from pioemu.state import State
from pioemu.conditions import receive_fifo_full


def push_blocking(state: State) -> State | None:
    if receive_fifo_full(state):
        return None  # Represents a stall

    return replace(
        state,
        receive_fifo=deque([*state.receive_fifo, state.input_shift_register.contents]),
        input_shift_register=ShiftRegister(0, 0),
    )


def push_nonblocking(state: State) -> State | None:
    if receive_fifo_full(state):
        return replace(state, input_shift_register=ShiftRegister(0, 0))

    return push_blocking(state)
