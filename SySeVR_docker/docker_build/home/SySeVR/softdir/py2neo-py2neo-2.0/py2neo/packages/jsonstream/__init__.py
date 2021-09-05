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
JSONStream
"""


__all__ = ["__author__", "__copyright__", "__email__", "__license__",
           "__version__", "AwaitingData", "EndOfStream", "UnexpectedCharacter",
           "JSONStream", "assembled", "grouped"]

__author__ = "Nigel Small"
__copyright__ = "2013, Nigel Small"
__email__ = "nigel@nigelsmall.com"
__license__ = "Apache License, Version 2.0"
__version__ = "0.9.1"


import sys as __sys


if __sys.version_info >= (3,):
    try:
        from .cjsonstream import (
            AwaitingData, EndOfStream, UnexpectedCharacter, TextStream,
            Tokeniser, JSONStream, assembled, grouped
        )
    except ImportError:
        from .pyjsonstream import (
            AwaitingData, EndOfStream, UnexpectedCharacter, TextStream,
            Tokeniser, JSONStream, assembled, grouped
        )
else:
    try:
        from .cjsonstream_2x import (
            AwaitingData, EndOfStream, UnexpectedCharacter, TextStream,
            Tokeniser, JSONStream, assembled, grouped
        )
    except ImportError:
        from .pyjsonstream import (
            AwaitingData, EndOfStream, UnexpectedCharacter, TextStream,
            Tokeniser, JSONStream, assembled, grouped
        )
