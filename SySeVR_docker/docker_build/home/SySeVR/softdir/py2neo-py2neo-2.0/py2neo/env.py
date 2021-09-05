#!/usr/bin/env python
# -*- encoding: utf-8 -*-

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


import os

from py2neo import ServiceRoot
from py2neo.packages.httpstream.packages.urimagic import URI


__all__ = ["DIST_SCHEME", "DIST_HOST", "NEO4J_HOME", "NEO4J_URI"]


DIST_SCHEME = os.getenv("NEO4J_DIST_SCHEME", "http")
DIST_HOST = os.getenv("NEO4J_DIST_HOST", "dist.neo4j.org")

NEO4J_HOME = os.getenv("NEO4J_HOME", ".")
NEO4J_URI = URI(os.getenv("NEO4J_URI", ServiceRoot.DEFAULT_URI))
