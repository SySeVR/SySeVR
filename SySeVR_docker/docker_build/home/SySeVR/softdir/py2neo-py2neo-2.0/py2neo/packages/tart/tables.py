#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011-2014, Nigel Small
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


from __future__ import unicode_literals

import sys

try:
    unicode
except NameError:
    # Python 3
    def ustr(s, encoding="utf-8"):
        if s is None:
            return ""
        elif isinstance(s, str):
            return s
        try:
            return s.decode(encoding)
        except AttributeError:
            return str(s)
else:
    # Python 2
    def ustr(s, encoding="utf-8"):
        if s is None:
            return ""
        elif isinstance(s, str):
            return s.decode(encoding)
        else:
            return unicode(s)

try:
    long
except NameError:
    # Python 3
    is_integer = lambda x: isinstance(x, int)
    is_numeric = lambda x: isinstance(x, (int, float, complex))
else:
    # Python 2
    is_integer = lambda x: isinstance(x, (int, long))
    is_numeric = lambda x: isinstance(x, (int, float, long, complex))


class TextTable(object):

    @classmethod
    def cell(cls, value, size):
        if value == "#" or is_numeric(value):
            text = ustr(value).rjust(size)
        else:
            text = ustr(value).ljust(size)
        return text

    def __init__(self, header, border=False):
        self.__header = list(map(ustr, header))
        self.__rows = []
        self.__widths = list(map(len, self.__header))
        self.__repr = None
        self.border = border

    def __repr__(self):
        if self.__repr is None:
            widths = self.__widths
            if self.border:
                lines = [
                    " " + " | ".join(self.cell(value, widths[i]) for i, value in enumerate(self.__header)) + "\n",
                    "-" + "-+-".join("-" * widths[i] for i, value in enumerate(self.__header)) + "-\n",
                ]
                for row in self.__rows:
                    lines.append(" " + " | ".join(self.cell(value, widths[i]) for i, value in enumerate(row)) + "\n")
            else:
                lines = [
                    " ".join(self.cell(value, widths[i]) for i, value in enumerate(self.__header)) + "\n",
                ]
                for row in self.__rows:
                    lines.append(" ".join(self.cell(value, widths[i]) for i, value in enumerate(row)) + "\n")
            self.__repr = "".join(lines)
            if sys.version_info < (3,):
                self.__repr = self.__repr.encode("utf-8")
        return self.__repr

    def append(self, row):
        row = list(row)
        self.__rows.append(row)
        self.__widths = [max(self.__widths[i], len(ustr(value))) for i, value in enumerate(row)]
        self.__repr = None
