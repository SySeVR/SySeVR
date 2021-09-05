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


from datetime import date, time, datetime
from decimal import Decimal
from sys import version_info

from py2neo.util import ustr


# Maximum and minimum integers supported up to Java 7.
# Java 8 also supports unsigned long which can extend
# to (2 ** 64 - 1) but Neo4j is not yet on Java 8.
minint = -2 ** 63
maxint = 2 ** 63 - 1


if version_info.major == 2:
    # Python 2
    integer_types = (int, long)
    string_types = (bytearray, bytes, str, unicode)
else:
    # Python 3
    integer_types = (int,)
    string_types = (bytearray, bytes, str)


def cast_property(value):
    """ Cast the supplied property value to something supported by
    Neo4j, raising an error if this is not possible.
    """
    if isinstance(value, (bool, float)):
        pass
    elif isinstance(value, integer_types):
        if minint <= value <= maxint:
            pass
        else:
            raise ValueError("Integer value out of range: %s" % value)
    elif isinstance(value, string_types):
        value = ustr(value)
    elif isinstance(value, (frozenset, list, set, tuple)):
        # check each item and all same type
        list_value = []
        list_type = None
        for item in value:
            item = cast_property(item)
            if list_type is None:
                list_type = type(item)
                if list_type is list:
                    raise ValueError("Lists cannot contain nested collections")
            elif not isinstance(item, list_type):
                raise TypeError("List property items must be of similar types")
            list_value.append(item)
        value = list_value
    elif isinstance(value, (datetime, date, time)):
        value = value.isoformat()
    elif isinstance(value, Decimal):
        # We'll lose some precision here but Neo4j can't
        # handle decimals anyway.
        value = float(value)
    elif isinstance(value, complex):
        value = [value.real, value.imag]
    else:
        raise TypeError("Invalid property type: %s" % type(value))
    return value
