#/usr/bin/env python
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


from py2neo.env import DIST_SCHEME, DIST_HOST, NEO4J_HOME, NEO4J_URI


def test_default_dist_scheme():
    assert DIST_SCHEME == "http"


def test_default_dist_host():
    assert DIST_HOST == "dist.neo4j.org"


def test_default_neo4j_home():
    assert NEO4J_HOME == "."


def test_default_neo4j_uri():
    assert NEO4J_URI == "http://localhost:7474/"
