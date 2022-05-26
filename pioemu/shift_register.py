# Copyright 2021, 2022 Nathan Young
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
class ShiftRegister:
    """Immutable shift register for 32-bit values.

    The value held can be shifted by an arbitrary number of bits in either direction. Instances of
    this class are immutable and therefore new representations of the shift register are returned
    from each of its methods.

    Attributes
    ----------
    contents : int
        Value held within this shift register.
    counter : int
        Total number of bits shifted out of / into this shift register (0-32).
    """

    def __init__(self, contents, counter):
        self._contents = contents
        self._counter = counter

    @property
    def contents(self):
        """Return the value held within this shift register."""
        return self._contents

    @property
    def counter(self):
        """Return the total number of bits shifted out of / into this shift register."""
        return self._counter

    def shift_left(self, bit_count, data_in=0):
        """Shifts the most significant bits out of the shift register.

        Parameters
        ----------
        bit_count : int
            Number of bits to shift into and out of the register.
        data_in : int, optional
            Value to shift into the register's least significant bits.

        Returns
        -------
        (ShiftRegister, int)
            Tuple containing the new representation of this shift register and the result.
        """
        bit_mask = (1 << bit_count) - 1

        new_contents = ((self._contents << bit_count) & 0xFFFF_FFFF) | (
            data_in & bit_mask
        )
        new_counter = min(32, self._counter + bit_count)

        return ShiftRegister(new_contents, new_counter), self._contents >> (
            32 - bit_count
        )

    def shift_right(self, bit_count, data_in=0):
        """Shifts the least significant bits out of the shift register.

        Parameters
        ----------
        bit_count : int
            Number of bits to shift into and out of the register.
        data_in : int, optional
            Value to shift into the register's most significant bits.

        Returns
        -------
        (ShiftRegister, int)
            Tuple containing the new representation of this shift register and the result.
        """
        bit_mask = (1 << bit_count) - 1

        new_contents = (self._contents >> bit_count) | (
            (data_in & bit_mask) << (32 - bit_count)
        )
        new_counter = min(32, self._counter + bit_count)

        return (
            ShiftRegister(new_contents, new_counter),
            self._contents & bit_mask,
        )

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return (self._contents, self._counter) == (other._contents, other._counter)

        return NotImplemented

    def __repr__(self):
        return f"ShiftRegister(contents={self._contents!r}, counter={self._counter!r})"
