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
Cypher is the built-in query language for Neo4j.
"""


from py2neo.cypher.create import *
from py2neo.cypher.delete import *
from py2neo.cypher.error.core import *
from py2neo.cypher.lang import *
from py2neo.cypher.core import *


__all__ = ["CypherResource", "CypherTransaction", "RecordListList", "RecordList", "RecordStream",
           "Record", "RecordProducer", "CypherWriter", "cypher_escape", "cypher_repr",
           "CreateStatement", "DeleteStatement"]
