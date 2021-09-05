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
An implementation of URIs and URI Templates from RFC 3986 (URI Generic Syntax)
and RFC 6570 (URI Template) respectively.
"""


from __future__ import unicode_literals


__author__ = "Nigel Small"
__copyright__ = "2013-2014, Nigel Small"
__email__ = "nigel@nigelsmall.com"
__license__ = "Apache License, Version 2.0"
__version__ = "1.2.0"


from .rfc3986 import *
from .rfc6570 import *
