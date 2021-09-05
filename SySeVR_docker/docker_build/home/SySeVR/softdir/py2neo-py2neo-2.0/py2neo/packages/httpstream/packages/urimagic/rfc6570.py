#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013-2014, Nigel Small
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


"""
An implementation of URI Templates from RFC 6570.
"""


from __future__ import unicode_literals

import re

from .rfc3986 import reserved, percent_encode, Part, URI


__all__ = ["URITemplate"]


class URITemplate(Part):
    """A URI Template is a compact sequence of characters for describing a
    range of Uniform Resource Identifiers through variable expansion.

    This class exposes a full implementation of RFC6570.
    """

    @classmethod
    def __cast(cls, obj):
        if obj is None:
            return cls(None)
        elif isinstance(obj, cls):
            return obj
        else:
            return cls(str(obj))

    class _Expander(object):

        _operators = set("+#./;?&")

        def __init__(self, values):
            self.values = values

        def collect(self, *keys):
            """ Fetch a list of all values matching the keys supplied,
            returning (key, value) pairs for each.
            """
            items = []
            for key in keys:
                if key.endswith("*"):
                    key, explode = key[:-1], True
                else:
                    explode = False
                if ":" in key:
                    key, max_length = key.partition(":")[0::2]
                    max_length = int(max_length)
                else:
                    max_length = None
                value = self.values.get(key)
                if isinstance(value, dict):
                    if not value:
                        items.append((key, None))
                    elif explode:
                        items.extend((key, _) for _ in value.items())
                    else:
                        items.append((key, value))
                elif isinstance(value, (tuple, list)):
                    if explode:
                        items.extend((key, _) for _ in value)
                    else:
                        items.append((key, list(value)))
                elif max_length is not None:
                    items.append((key, value[:max_length]))
                else:
                    items.append((key, value))
            return [(key, value) for key, value in items if value is not None]

        def _expand(self, expression, safe=None, prefix="", separator=",",
                    with_keys=False, trim_empty_equals=False):
            items = self.collect(*expression.split(","))
            encode = lambda x: percent_encode(x, safe=safe)
            for i, (key, value) in enumerate(items):
                if isinstance(value, tuple):
                    items[i] = "=".join(map(encode, value))
                else:
                    if isinstance(value, dict):
                        items[i] = ",".join(",".join(map(encode, item))
                                            for item in value.items())
                    elif isinstance(value, list):
                        items[i] = ",".join(map(encode, value))
                    else:
                        items[i] = encode(value)
                    if with_keys:
                        if items[i] is None or (items[i] == "" and
                                                trim_empty_equals):
                            items[i] = encode(key)
                        else:
                            items[i] = encode(key) + "=" + (items[i] or "")
            out = []
            for i, item in enumerate(items):
                out.append(prefix if i == 0 else separator)
                out.append(item)
            return "".join(out)

        def expand(self, expression):
            """ Dispatch to the correct expansion method.
            """
            if not expression:
                return ""
            if expression[0] in self._operators:
                operator, expression = expression[0], expression[1:]
                if operator == "+":
                    return self._expand(expression, reserved)
                elif operator == "#":
                    return self._expand(expression, reserved, prefix="#")
                elif operator == ".":
                    return self._expand(expression, prefix=".", separator=".")
                elif operator == "/":
                    return self._expand(expression, prefix="/", separator="/")
                elif operator == ";":
                    return self._expand(expression, prefix=";", separator=";",
                                        with_keys=True, trim_empty_equals=True)
                elif operator == "?":
                    return self._expand(expression, prefix="?", separator="&",
                                        with_keys=True)
                elif operator == "&":
                    return self._expand(expression, prefix="&", separator="&",
                                        with_keys=True)
            else:
                return self._expand(expression)

    _tokeniser = re.compile("(\{)([^{}]*)(\})")

    def __init__(self, template):
        super(URITemplate, self).__init__()
        self.__template = template

    def __eq__(self, other):
        other = self.__cast(other)
        return self.__template == other.__template

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.string)

    @property
    def string(self):
        if self.__template is None:
            return None
        return str(self.__template)

    def expand(self, **values):
        """ Expand into a URI using the values supplied
        """
        if self.__template is None:
            return URI(None)
        tokens = self._tokeniser.split(self.__template)
        expander = URITemplate._Expander(values)
        out = []
        while tokens:
            token = tokens.pop(0)
            if token == "{":
                expression = tokens.pop(0)
                tokens.pop(0)
                out.append(expander.expand(expression))
            else:
                out.append(token)
        return URI("".join(out))
