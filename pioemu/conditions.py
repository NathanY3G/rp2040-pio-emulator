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
def clock_cycles_reached(target_value):
    return lambda state: state.clock >= target_value


def x_register_equals_zero(state):
    return state.x_register == 0


def x_register_not_equal_to_zero(state):
    return state.x_register != 0


def y_register_equals_zero(state):
    return state.y_register == 0


def y_register_not_equal_to_zero(state):
    return state.y_register != 0


def x_register_not_equal_to_y_register(state):
    return state.x_register != state.y_register
