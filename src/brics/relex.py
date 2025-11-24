# brics - relex data definitions.
#
# Author: Jahin Z. <jahinzee>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

__package__ = "brics"

from brics.exceptions import RelexParsingError
from brics.instructions import Instruction

from typing import final, Iterable, Self
from io import TextIOWrapper
from pathlib import Path

# region private


def _buf_peek(buf: TextIOWrapper, count: int) -> str:
    current_pos = buf.tell()
    output = buf.read(count)
    buf.seek(current_pos)
    return output


# endregion


@final
class Relex:
    """
    A "relex" -- mapping of text to instructions.

    CONSTRUCTOR: Raises `RelexParsingError` if definitions are not exhaustive.
    """

    __slots__ = "name", "instruction_map"

    name: str
    instruction_map: dict[Instruction, str]

    def __init__(self, *, name: str, instruction_map: dict[Instruction, str]) -> None:
        missing = set(Instruction.all_instructions()) - set(instruction_map.keys())
        if len(missing) != 0:
            # fmt: off
            raise RelexParsingError(None, (
                 "Relex definition is inexhaustive, missing instruction(s): "
                f"{', '.join(sorted(f"'{i.to_char()}'" for i in missing))}"))
            # fmt: on
        self.name = name
        self.instruction_map = instruction_map

    @classmethod
    def from_relex_file(cls, file: TextIOWrapper) -> Self:
        """
        Generates a relex object from a relex definition.

        Raises `RelexParsingError` if there are invalid definitions, unknown instruction mappings,
        or definitions are not exhaustive.
        """

        # Remove blank lines and comment lines (starting with #), and split at first space char
        # if possible.
        #
        parsed_lines = (
            (idx, line.strip().partition(" "))
            for idx, line in enumerate(file)
            if not line.strip().startswith("#") and len(line.strip()) != 0
        )

        instr_map = dict[Instruction, str]()

        for idx, (standard_instr, sep, relex_instr) in parsed_lines:
            if len(relex_instr.strip()) == 0:
                # fmt: off
                raise RelexParsingError(idx + 1,
                    f"Missing relex value: '{standard_instr}{sep}{relex_instr}'")
                # fmt: on
            if (instr := Instruction.from_char(standard_instr)) is None:
                # fmt: off
                raise RelexParsingError(idx + 1,
                    f"Attempted to map to unknown instruction key: '{standard_instr}{sep}{relex_instr}'")
                # fmt: on
            instr_map[instr] = relex_instr.strip()

        return cls(name=Path(file.name).stem, instruction_map=instr_map)

    @classmethod
    def standard(cls) -> Self:
        """Returns the standard instruction relex."""
        # fmt: off
        return cls(
            name="[standard]",
            instruction_map={
            Instruction.Previous: "<",
            Instruction.Next: ">",
            Instruction.Add: "+",
            Instruction.Subtract: "-" ,
            Instruction.Input: ",",
            Instruction.Output: ".",
            Instruction.BeginLoop: "[",
            Instruction.EndLoop: "]"})
        # fmt: on

    def text_to_instrs(self, text: TextIOWrapper) -> Iterable[Instruction]:
        """Scans input text and generates instructions (with corresponding indices)."""

        while _buf_peek(text, 1) != "":
            for instr_enum, instr_text in self.instruction_map.items():
                len_instr_text = len(instr_text)
                value = _buf_peek(text, len_instr_text)
                if value == instr_text:
                    yield instr_enum
                    text.read(len_instr_text)
                    break
            else:
                text.read(1)
