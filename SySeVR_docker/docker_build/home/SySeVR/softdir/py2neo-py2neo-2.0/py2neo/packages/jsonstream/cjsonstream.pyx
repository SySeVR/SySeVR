#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012-2014 Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Incremental JSON parser.
"""


from __future__ import unicode_literals

from builtins import chr as _chr
from itertools import groupby
from string import digits, whitespace


__all__ = ["JSONStream", "assembled", "grouped"]


class AwaitingData(BaseException):
    """ Raised when data is temporarily unavailable.
    """

    def __init__(self, *args, **kwargs):
        super(AwaitingData, self).__init__(*args, **kwargs)


class EndOfStream(BaseException):
    """ Raised when stream is exhausted.
    """

    def __init__(self, *args, **kwargs):
        super(EndOfStream, self).__init__(*args, **kwargs)


class UnexpectedCharacter(ValueError):
    """ Raised when a unexpected character is encountered.
    """

    def __init__(self, *args, **kwargs):
        super(UnexpectedCharacter, self).__init__(*args, **kwargs)


cdef class TextStream:

    cdef list __data
    cdef int __current_line
    cdef int __current_char
    cdef bint __writable
    cdef int __marked_line
    cdef int __marked_char

    def __init__(self):
        self.__data = []
        self.__current_line = 0
        self.__current_char = 0
        self.__writable = True
        self.__marked_line = 0
        self.__marked_char = 0

    cpdef close(self):
        self.__writable = False

    cpdef peek(self):
        cdef str line
        if self.__current_line < len(self.__data):
            line = self.__data[self.__current_line]
            if self.__current_char < len(line):
                return line[self.__current_char]
            else:
                # no more characters on this line, jump to the next
                self.__current_line += 1
                self.__current_char = 0
                if self.__current_line < len(self.__data):
                    return self.__data[self.__current_line][self.__current_char]
        if self.__writable:
            raise AwaitingData()
        else:
            raise EndOfStream()

    cpdef read(self):
        cdef str line
        cdef Py_UCS4 ch
        if self.__current_line < len(self.__data):
            line = self.__data[self.__current_line]
            if self.__current_char < len(line):
                ch = line[self.__current_char]
                self.__current_char += 1
                return ch
            else:
                self.__current_line += 1
                if self.__current_line < len(self.__data):
                    self.__current_char = 1
                    return self.__data[self.__current_line][0]
                else:
                    self.__current_char = 0
        if self.__writable:
            raise AwaitingData()
        else:
            raise EndOfStream()

    cpdef read_any(self, allowed):
        cdef list out = []
        cdef int start = self.__current_char
        cdef str line
        cdef Py_UCS4 ch
        while True:
            if self.__current_line < len(self.__data):
                line = self.__data[self.__current_line]
                if self.__current_char < len(line):
                    ch = self.__data[self.__current_line][self.__current_char]
                    if ch in allowed:
                        # move forward
                        self.__current_char += 1
                    else:
                        # return everything between start and here
                        out.append(line[start:self.__current_char])
                        return "".join(out)
                else:
                    # no more characters on this line
                    out.append(line[start:])
                    self.__current_line += 1
                    self.__current_char = 0
                    start = 0
            elif self.__writable:
                raise AwaitingData()
            else:
                return "".join(out)

    def read_until_any(self, markers):
        cdef list out = []
        cdef int line = self.__current_line
        cdef int start = self.__current_char
        cdef int end
        cdef int pos
        while True:
            if line < len(self.__data):
                try:
                    end = min(pos
                              for pos in [self.__data[line].find(marker, start)
                                          for marker in markers]
                              if pos >= 0)
                except ValueError:  # not found
                    out.append(self.__data[line][start:])
                    line += 1
                    start = 0
                else:
                    # found
                    self.__current_line = line
                    self.__current_char = end + 1
                    out.append(self.__data[line][start:self.__current_char])
                    return "".join(out)
            elif self.__writable:
                raise AwaitingData()
            else:
                raise EndOfStream()

    cpdef peek_after_any(self, markers):
        """
        skips any characters in the marker set and returns a peek of the next
        """
        cdef str line
        cdef Py_UCS4 ch
        while True:
            if self.__current_line < len(self.__data):
                line = self.__data[self.__current_line]
                if self.__current_char < len(line):
                    ch = self.__data[self.__current_line][self.__current_char]
                    if ch in markers:
                        # skip
                        self.__current_char += 1
                    else:
                        # peek
                        return ch
                else:
                    # no more characters on this line
                    self.__current_line += 1
                    self.__current_char = 0
            elif self.__writable:
                raise AwaitingData()
            else:
                raise EndOfStream()

    cpdef write(self, data):
        if not self.__writable:
            raise IOError("Stream is not writable")
        if data:
            # so we can guarantee no line is empty
            self.__data.append(data)

    cpdef mark(self):
        self.__marked_line = self.__current_line
        self.__marked_char = self.__current_char

    cpdef undo(self):
        self.__current_line = self.__marked_line
        self.__current_char = self.__marked_char


cdef class Tokeniser(object):

    cdef TextStream __text

    def __init__(self):
        self.__text = TextStream()

    cpdef close(self):
        self.__text.close()

    cpdef write(self, data):
        """Write raw JSON data to the decoder stream.
        """
        self.__text.write(data)

    cpdef _read_literal(self, literal):
        cdef Py_UCS4 expected
        cdef Py_UCS4 actual
        self.__text.mark()
        try:
            for expected in literal:
                actual = self.__text.read()
                if actual != expected:
                    raise UnexpectedCharacter(actual)
        except AwaitingData:
            self.__text.undo()
            raise
        return literal

    cpdef _read_string(self):
        cdef list src
        cdef list value
        cdef str chunk
        cdef Py_UCS4 ch
        cdef int n, i
        self.__text.mark()
        try:
            src, value = [self._read_literal('"')], []
            while True:
                chunk = self.__text.read_until_any(('"', '\\'))
                src.append(chunk)
                value.append(chunk[:-1])
                if chunk.endswith('\\'):
                    ch = self.__text.read()
                    src.append(ch)
                    if ch in '"/\\':
                        value.append(ch)
                    elif ch == 'b':
                        value.append('\b')
                    elif ch == 'f':
                        value.append('\f')
                    elif ch == 'n':
                        value.append('\n')
                    elif ch == 'r':
                        value.append('\r')
                    elif ch == 't':
                        value.append('\t')
                    elif ch == 'u':
                        n = 0
                        for i in range(4):
                            ch = self.__text.read()
                            src.append(ch)
                            n = 16 * n + int(ch, 16)
                        value.append(_chr(n))
                    else:
                        raise UnexpectedCharacter(ch)
                else:
                    return "".join(src), "".join(value)
        except AwaitingData:
            self.__text.undo()
            raise

    cpdef _read_number(self):
        cdef list src = []
        cdef bint has_fractional_part = False
        cdef bint has_exponent = False
        cdef str ch
        self.__text.mark()
        try:
            # check for sign
            ch = self.__text.read_any("-")
            if ch:
                src.append(ch)
            # read integer part
            src.append(self.__text.read_any(digits))
            # read fractional part
            ch = self.__text.read_any(".")
            if ch:
                has_fractional_part = True
                src.append(ch)
                src.append(self.__text.read_any(digits))
            # read exponent
            ch = self.__text.read_any('Ee')
            if ch:
                has_exponent = True
                src.append(ch)
                ch = self.__text.read_any('+-')
                if ch:
                    src.append(ch)
                src.append(self.__text.read_any(digits))
        except AwaitingData:
            # number potentially incomplete: need to wait for
            # further data or end of stream
            self.__text.undo()
            raise
        str_src = "".join(src)
        if has_fractional_part or has_exponent:
            return str_src, float(str_src)
        else:
            return str_src, int(str_src)

    cpdef read_token(self):
        """ Read token

        """
        cdef Py_UCS4 ch = self.__text.peek_after_any(whitespace)
        if ch in ',:[]{}':
            return self.__text.read(), None
        if ch == '"':
            return self._read_string()
        if ch in '0123456789+-':
            return self._read_number()
        if ch == 't':
            return self._read_literal("true"), True
        if ch == 'f':
            return self._read_literal("false"), False
        if ch == 'n':
            return self._read_literal("null"), None
        raise UnexpectedCharacter(ch)


# Token constants used for expectation management
cdef int VALUE = 0x01
cdef int OPEN_BRACKET = 0x02
cdef int CLOSE_BRACKET = 0x04
cdef int OPEN_BRACE = 0x08
cdef int CLOSE_BRACE = 0x10
cdef int COMMA = 0x20
cdef int COLON = 0x40

cdef int VALUE_OR_OPEN = VALUE | OPEN_BRACKET | OPEN_BRACE
cdef int VALUE_BRACKET_OR_OPEN_BRACE = VALUE | OPEN_BRACKET | CLOSE_BRACKET | OPEN_BRACE
cdef int COMMA_OR_CLOSE_BRACKET = COMMA | CLOSE_BRACKET
cdef int COMMA_OR_CLOSE_BRACE = COMMA | CLOSE_BRACE
cdef int VALUE_OR_CLOSE_BRACE = VALUE | CLOSE_BRACE


cdef class JSONStream(object):
    """ Streaming JSON decoder. This class both expects Unicode input and will
    produce Unicode output.
    """

    cdef Tokeniser tokeniser
    cdef object source
    cdef list path
    cdef int _expectation

    def __init__(self, source):
        self.tokeniser = Tokeniser()
        self.source = iter(source)
        self.path = []
        self._expectation = VALUE | OPEN_BRACKET | OPEN_BRACE

    cpdef _in_array(self):
        return self.path and isinstance(self.path[-1], int)

    cpdef _in_object(self):
        return self.path and not isinstance(self.path[-1], int)

    def __iter__(self):
        cdef str src
        while True:
            try:
                try:
                    self.tokeniser.write(next(self.source))
                except StopIteration:
                    self.tokeniser.close()
                while True:
                    try:
                        src, value = self.tokeniser.read_token()
                        if src == ',':
                            if not self._expectation & COMMA:
                                raise UnexpectedCharacter(",")
                            self._expectation = VALUE_OR_OPEN
                        elif src == ':':
                            if not self._expectation & COLON:
                                raise UnexpectedCharacter(":")
                            self._expectation = VALUE_OR_OPEN
                        elif src == '[':
                            yield tuple(self.path), []
                            if not self._expectation & OPEN_BRACKET:
                                raise UnexpectedCharacter("[")
                            self.path.append(0)
                            self._expectation = VALUE_BRACKET_OR_OPEN_BRACE
                        elif src == ']':
                            if not self._expectation & CLOSE_BRACKET:
                                raise UnexpectedCharacter("]")
                            self.path.pop()
                            if self._in_array():
                                self.path[-1] += 1
                                self._expectation = COMMA_OR_CLOSE_BRACKET
                            elif self._in_object():
                                self.path[-1] = None
                                self._expectation = COMMA_OR_CLOSE_BRACE
                            else:
                                self._expectation = VALUE_OR_OPEN
                        elif src == '{':
                            yield tuple(self.path), {}
                            if not self._expectation & OPEN_BRACE:
                                raise UnexpectedCharacter("{")
                            self.path.append(None)
                            self._expectation = VALUE_OR_CLOSE_BRACE
                        elif src == '}':
                            if not self._expectation & CLOSE_BRACE:
                                raise UnexpectedCharacter("}")
                            self.path.pop()
                            if self._in_array():
                                self.path[-1] += 1
                                self._expectation = COMMA_OR_CLOSE_BRACKET
                            elif self._in_object():
                                self.path[-1] = None
                                self._expectation = COMMA_OR_CLOSE_BRACE
                            else:
                                self._expectation = VALUE_OR_OPEN
                        else:
                            if not self._expectation & VALUE:
                                raise UnexpectedCharacter(src)
                            if self._in_array():
                                # array value
                                yield tuple(self.path), value
                                self.path[-1] += 1
                                self._expectation = COMMA_OR_CLOSE_BRACKET
                            elif self._in_object():
                                if self.path[-1] is None:
                                    # object key (no yield)
                                    self.path[-1] = value
                                    self._expectation = COLON
                                else:
                                    # object value
                                    yield tuple(self.path), value
                                    self.path[-1] = None
                                    self._expectation = COMMA_OR_CLOSE_BRACE
                            else:
                                # simple value
                                yield tuple(self.path), value
                    except AwaitingData:
                        break
            except EndOfStream:
                break


def _merged(obj, key, value):
    """ Returns object with value merged at a position described by iterable
    key. The key describes a navigable path through the object hierarchy with
    integer items describing list indexes and other types of items describing
    dictionary keys.

        >>> obj = None
        >>> obj = _merged(obj, ("drink",), "lemonade")
        >>> obj
        {'drink': 'lemonade'}
        >>> obj = _merged(obj, ("cutlery", 0), "knife")
        >>> obj = _merged(obj, ("cutlery", 1), "fork")
        >>> obj = _merged(obj, ("cutlery", 2), "spoon")
        >>> obj
        {'cutlery': ['knife', 'fork', 'spoon'], 'drink': 'lemonade'}

    """
    if key:
        k = key[0]
        if isinstance(k, int):
            if isinstance(obj, list):
                obj = list(obj)
            else:
                obj = []
            while len(obj) <= k:
                obj.append(None)
        else:
            if isinstance(obj, dict):
                obj = dict(obj)
            else:
                obj = {}
            obj.setdefault(k, None)
        obj[k] = _merged(obj[k], key[1:], value)
        return obj
    else:
        return value


def assembled(iterable):
    """ Returns a JSON-derived value from a set of key-value pairs as produced
    by the JSONStream process. This operates in a similar way to the built-in
    `dict` function. Internally, this uses the `merged` function on each pair
    to build the return value.

        >>> data = [
        ...     (("drink",), "lemonade"),
        ...     (("cutlery", 0), "knife"),
        ...     (("cutlery", 1), "fork"),
        ...     (("cutlery", 2), "spoon"),
        ... ]
        >>> assembled(data)
        {'cutlery': ['knife', 'fork', 'spoon'], 'drink': 'lemonade'}

    :param iterable: key-value pairs to be merged into assembled value
    """
    obj = None
    for key, value in iterable:
        obj = _merged(obj, key, value)
    return obj


def _group(iterable, level):
    for key, value in iterable:
        yield key[level:], value


def grouped(iterable, level=1):
    def _group_key(item):
        key, value = item
        if len(key) >= level:
            return key[0:level]
        else:
            return None
    for key, value in groupby(iterable, _group_key):
        if key is not None:
            yield key, _group(value, level)
