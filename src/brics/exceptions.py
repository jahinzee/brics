# brics - exception hierarchy definitions.
#
# Author: Jahin Z. <jahinzee>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

__package__ = "brics"

from typing import Optional


class BrainfuckException(Exception):
    pass


class ParsingError(BrainfuckException):
    __slots__ = ("char", "message")

    def __init__(self, char: int, message: str):
        super().__init__(message)
        self.char = char
        self.message = message


class RelexParsingError(BrainfuckException):
    __slots__ = ("line", "message")

    def __init__(self, line: Optional[int], message: str):
        super().__init__(message)
        self.line = line
        self.message = message


class BfRuntimeGracefulExit(BrainfuckException):
    pass
