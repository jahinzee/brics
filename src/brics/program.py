# brics - program data definitions.
#
# Author: Jahin Z. <jahinzee>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

__package__ = "brics"

from brics.exceptions import ParsingError
from brics.instructions import Instruction
from brics.relex import Relex

from typing import final, Optional
from pathlib import Path
from io import TextIOWrapper


@final
class Program:
    """A valid parsed Brainfuck program with pre-computed loop boundary indices."""

    __slots__ = "instructions", "loop_boundaries", "relex", "optimised", "source_file"

    source_file: Path
    instructions: tuple[Instruction, ...]
    loop_boundaries: dict[int, int]
    relex: Relex
    optimised: bool

    # region private

    def _trim_headers(self):
        while self._trim_header_once():
            pass

    def _trim_header_once(self) -> bool:
        result = self._get_first_bounds(self.instructions)
        if result is None:
            return False
        li, ri = result
        if li != 0:
            return False
        self.instructions = self.instructions[ri + 1 :]
        return True

    @staticmethod
    def _make_bounds(instrs: tuple[Optional[Instruction], ...]) -> dict[int, int]:
        """
        Returns a *set* of matching LoopStart and LoopEnd indices from a given sequence of
        instructions

        Raises `ParsingError` if there are unbalanced loops.
        """
        output = {}
        stack = []

        for idx, instr in enumerate(instrs):
            if instr is None:
                break
            if idx is None:
                continue
            match instr:
                case Instruction.BeginLoop:
                    stack.append(idx)
                case Instruction.EndLoop:
                    try:
                        right_idx = stack.pop()
                    except IndexError:
                        raise ParsingError(idx, "Unmatched ] instruction")
                    output[idx] = right_idx
                    output[right_idx] = idx

        if len(stack) != 0:
            idx = stack.pop()
            raise ParsingError(idx, "Unmatched [ instruction")
        return output

    @staticmethod
    def _get_first_bounds(
        instrs: tuple[Optional[Instruction], ...],
    ) -> Optional[tuple[int, int]]:
        """
        Returns the *first* matching LoopStart and LoopEnd indices from a given sequence of
        instructions.x

        The first pair based on the position of LoopStart:

            ···[··[···]····]
               ↑___________↑

        Returns `None` if there are no loop bounds.

        Raises `ParsingError` if there are unbalanced loops.
        """
        output = set()
        stack = []

        for idx, instr in enumerate(instrs):
            if idx == 0 and instr != Instruction.BeginLoop:
                return None
            match instr:
                case Instruction.BeginLoop:
                    stack.append(idx)
                case Instruction.EndLoop:
                    try:
                        output.add((stack.pop(), idx))
                    except IndexError:
                        raise ParsingError(idx, "Unmatched ] instruction")
                    if len(stack) == 0:
                        return (0, idx)

        if len(stack) != 0:
            idx = stack.pop()
            raise ParsingError(idx, "Unmatched [ instruction")
        return None

    # endregion

    def __init__(self, text: TextIOWrapper, relex: Relex, *, optimise: bool = False) -> None:
        """
        Create a valid Brainfuck program from source text, and a Relex object for character to
        instruction conversion.

        If `optimise` is True, applies basic optimisations (trimming comment headers).

        Raises `ParsingError` if there are errors in the source.
        """

        self.instructions = tuple(relex.text_to_instrs(text))
        if optimise:
            self._trim_headers()
        self.optimised = optimise
        self.loop_boundaries = self._make_bounds(self.instructions)
        self.relex = relex
        self.source_file = Path(text.name)
