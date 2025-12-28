# brics - process and runtime functionality.
#
# Author: Jahin Z. <jahinzee>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

__package__ = "brics"

from brics.exceptions import BfRuntimeGracefulExit
from brics.instructions import Instruction
from brics.program import Program

import sys

# region private

_MEMORY_SIZE = 30_000


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
    data = [0 for _ in range(_MEMORY_SIZE)]
    data_ptr = 0

    idx_end_of_program = len(program.instructions)

    while program_ptr != idx_end_of_program:
        match program.instructions[program_ptr]:
            case Instruction.Next:
                data_ptr += 1
            case Instruction.Previous:
                data_ptr -= 1
            case Instruction.Add:
                data[data_ptr] += 1
            case Instruction.Subtract:
                data[data_ptr] -= 1
            case Instruction.BeginLoop if data[data_ptr] == 0:
                program_ptr = program.loop_boundaries[program_ptr]
            case Instruction.EndLoop if data[data_ptr] != 0:
                program_ptr = program.loop_boundaries[program_ptr]
            case Instruction.Input:
                data[data_ptr] = _input()
            case Instruction.Output:
                _output(data[data_ptr])

        data_ptr %= _MEMORY_SIZE
        data[data_ptr] %= 256
        program_ptr += 1
