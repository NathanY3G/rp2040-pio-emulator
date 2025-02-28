# Copyright 2021, 2022, 2023, 2025 Nathan Young
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
from dataclasses import dataclass
from enum import auto, Enum
from typing import Callable, Optional
from .state import State


class ProgramCounterAdvance(Enum):
    ALWAYS = auto()
    WHEN_CONDITION_MET = auto()
    WHEN_CONDITION_NOT_MET = auto()
    NEVER = auto()


@dataclass(frozen=True, kw_only=True)
class Instruction:
    opcode: int
    delay_cycles: int
    side_set_value: int


@dataclass(frozen=True, kw_only=True)
class InInstruction(Instruction):
    source: int  # TODO: Use an enumeration instead of an integer?
    bit_count: int


@dataclass(frozen=True, kw_only=True)
class JmpInstruction(Instruction):
    target_address: int
    condition: int  # TODO: Use an enumeration instead of an integer?


@dataclass(frozen=True, kw_only=True)
class OutInstruction(Instruction):
    destination: int  # TODO: Use an enumeration instead of an integer?
    bit_count: int


@dataclass(frozen=True, kw_only=True)
class PullInstruction(Instruction):
    if_empty: bool
    block: bool


@dataclass(frozen=True, kw_only=True)
class PushInstruction(Instruction):
    if_full: bool
    block: bool


@dataclass(frozen=True, kw_only=True)
class WaitInstruction(Instruction):
    source: int  # TODO: Use an enumeration instead of an integer?
    index: int
    polarity: bool


@dataclass(frozen=True)
class Emulation:
    condition: Callable[[State], bool]
    emulate: Callable[[State], State | None]
    program_counter_advance: ProgramCounterAdvance
    instruction: Optional[Instruction] = None
