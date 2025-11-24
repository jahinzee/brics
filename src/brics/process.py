# brics - process and runtime functionality.
#
# Author: Jahin Z. <jahinzee>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

__package__ = "brics"

from brics.exceptions import BfRuntimeGracefulExit, BfRuntimeError
from brics.instructions import Instruction
from brics.program import Program

from collections.abc import MutableMapping
from typing import final

import sys

# region private


@final
class _ProcessMemory(MutableMapping[int, int]):
    """
    A dictionary-like object that represents a static array of integers for program memory,
    with value and index wrapping.
    """

    __slots__ = "_size", "_cell_size", "_data"

    _size: int
    _cell_size: int
    _data: dict[int, int]

    def __init__(self, size: int, cell_size: int) -> None:
        """
        Creates an object representing a `size`-element long array of integers from
        0 to `cell-size`.
        """
        self._size = size
        self._cell_size = cell_size
        self._data = dict()

    @classmethod
    def standard_bf_memory(cls):
        """
        Creates a standard Brainfuck memory object, corresponding to 30,000 8-bit integers.
        """
        return cls(size=30_000, cell_size=256)

    def __getitem__(self, idx: int) -> int:
        """
        Get the `idx`-th item in memory. Overflows and underflows are wrapped.
        """
        return self._data.get(idx % self._size, 0) % self._cell_size

    def __setitem__(self, idx: int, val: int) -> None:
        """
        Set the `idx`-th item in memory to `val`. Overflows and underflows for `idx` and `val` are
        wrapped.
        """
        self._data.__setitem__(idx % self._size, val % self._cell_size)
        if val == 0:
            self._data.__delitem__(idx % self._size)

    def __delitem__(self, idx: int) -> None:
        """
        Functionally an alias for `self[idx] = 0`.
        """
        self._data.__setitem__(idx % self._size, 0)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


def _input() -> int:
    """
    Return a single character from standard input as an integer.

    Raises `BrainfuckException` (runtime, graceful) if an EOF or NUL is read.
    """
    byte = sys.stdin.read(1)
    if len(byte) != 1:
        raise BfRuntimeGracefulExit()
    return ord(byte)


def _output(val: int):
    """
    Writes a single integer to standard output as an ASCII/Unicode character.
    """
    sys.stdout.write(chr(val))
    LINE_FEED = 0x0A
    if val == LINE_FEED:
        sys.stdout.flush()


# endregion


def run_program(program: Program):
    """
    Begins process execution.

    Raises `BrainfuckException` (runtime) if a runtime error occurs.
    """
    program = program
    program_ptr = 0
    data = _ProcessMemory.standard_bf_memory()
    data_ptr = 0

    while True:
        try:
            instruction = program.instructions[program_ptr]
        except IndexError:
            max_idx = len(program.instructions) - 1
            raise BfRuntimeError(
                program_ptr,
                f"Program pointer out-of-bounds (valid range: 0 – {max_idx})",
            )
        match instruction:
            case Instruction.Next:
                data_ptr += 1
            case Instruction.Previous:
                data_ptr -= 1
            case Instruction.Add:
                data[data_ptr] += 1
            case Instruction.Subtract:
                data[data_ptr] -= 1
            case Instruction.BeginLoop if data[data_ptr] == 0:
                program_ptr = program.get_other_bound(program_ptr)
            case Instruction.EndLoop if data[data_ptr] != 0:
                program_ptr = program.get_other_bound(program_ptr)
            case Instruction.Input:
                data[data_ptr] = _input()
            case Instruction.Output:
                _output(data[data_ptr])
            case None:
                break
        program_ptr += 1
