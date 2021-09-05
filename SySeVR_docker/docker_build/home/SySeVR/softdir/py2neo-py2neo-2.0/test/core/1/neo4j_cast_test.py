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


from py2neo import Graph, Node, Relationship


def test_can_cast_node(graph):
    alice, = graph.create({"name": "Alice"})
    casted = Graph.cast(alice)
    assert isinstance(casted, Node)
    assert casted.bound
    assert casted["name"] == "Alice"


def test_can_cast_dict():
    casted = Graph.cast({"name": "Alice"})
    assert isinstance(casted, Node)
    assert not casted.bound
    assert casted["name"] == "Alice"


def test_can_cast_rel(graph):
    a, b, ab = graph.create({}, {}, (0, "KNOWS", 1))
    casted = Graph.cast(ab)
    assert isinstance(casted, Relationship)
    assert casted.bound
    assert casted.start_node == a
    assert casted.type == "KNOWS"
    assert casted.end_node == b


def test_can_cast_3_tuple():
    casted = Graph.cast(("Alice", "KNOWS", "Bob"))
    assert isinstance(casted, Relationship)
    assert not casted.bound
    assert casted.start_node == Node("Alice")
    assert casted.type == "KNOWS"
    assert casted.end_node == Node("Bob")


def test_can_cast_4_tuple():
    casted = Graph.cast(("Alice", "KNOWS", "Bob", {"since": 1999}))
    assert isinstance(casted, Relationship)
    assert not casted.bound
    assert casted.start_node == Node("Alice")
    assert casted.type == "KNOWS"
    assert casted.end_node == Node("Bob")
    assert casted["since"] == 1999
