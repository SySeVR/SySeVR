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


"""
.. note::
   Neobox has been written to work on Linux and may not operate
   correctly - or at all - on other platforms.

Neobox is a command line tool and API for managing multiple Neo4j server
installations (boxes), each running on its own unique port. The command
line tool is installed as part of the py2neo setup script and can be used
as follows::

    $ neobox install my-box community 2.1.5
    Created server instance 'my-box' configured on ports 47470 and 47471

    $ neobox list
    my-box

    $ neobox start my-box
    http://localhost:47476/

    $ neobox stop my-box

    $ neobox drop my-box

    $ neobox remove my-box

All command line features are also available as API calls.
"""


from py2neo.ext.neobox.core import *


__all__ = ["Warehouse", "Box"]
