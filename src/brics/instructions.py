# brics - instruction data definitions.
#
# Author: Jahin Z. <jahinzee>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
from __future__ import annotations

__package__ = "brics"

from typing import final

import enum


@final
class Instruction(enum.Enum):
    """Brainfuck instructions."""

    Next = enum.auto()
    Previous = enum.auto()
    Add = enum.auto()
    Subtract = enum.auto()
    BeginLoop = enum.auto()
    EndLoop = enum.auto()
    Input = enum.auto()
    Output = enum.auto()

    @classmethod
    def from_char(cls, char: str) -> Instruction | None:
        """
        Returns the corresponding Brainfuck instruction that `char` represents.
        Return None if `len(char) > 1`, or `char` is not a valid Brainfuck instruction.
        """
        match char:
            case ">":
                return cls.Next
            case "<":
                return cls.Previous
            case "+":
                return cls.Add
            case "-":
                return cls.Subtract
            case "[":
                return cls.BeginLoop
            case "]":
                return cls.EndLoop
            case ",":
                return cls.Input
            case ".":
                return cls.Output
            case _:
                return None

    def to_char(self) -> str:
        """
        Returns the corresponding standard character of the Brainfuck instruction.
        """
        match self:
            case Instruction.Next:
                return ">"
            case Instruction.Previous:
                return "<"
            case Instruction.Add:
                return "+"
            case Instruction.Subtract:
                return "-"
            case Instruction.BeginLoop:
                return "["
            case Instruction.EndLoop:
                return "]"
            case Instruction.Input:
                return ","
            case Instruction.Output:
                return "."

    @classmethod
    def all_instructions(cls) -> set[Instruction]:
        """Return a set of all instructions."""
        return {i for i in cls}
