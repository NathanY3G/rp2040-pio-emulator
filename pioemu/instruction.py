# Copyright 2021, 2022, 2023 Nathan Young
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
from typing import Callable
from .state import State


class ProgramCounterAdvance(Enum):
    ALWAYS = auto()
    WHEN_CONDITION_MET = auto()
    WHEN_CONDITION_NOT_MET = auto()
    NEVER = auto()


@dataclass(frozen=True)
class Instruction:
    condition: Callable[[State], bool]
    callable: Callable[[int, State], State]
    program_counter_advance: ProgramCounterAdvance
