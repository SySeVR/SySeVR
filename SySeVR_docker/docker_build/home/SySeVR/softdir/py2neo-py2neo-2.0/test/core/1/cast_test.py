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


from py2neo import Node, NodePointer, Rel, Relationship


def test_graph_cast(graph):
    assert graph.cast(None) is None


def test_node_cast():
    alice = Node("Person", "Employee", name="Alice", age=33)
    assert Node.cast() == Node()
    assert Node.cast(None) is None
    assert Node.cast(alice) is alice
    assert Node.cast("Person") == Node("Person")
    assert Node.cast(name="Alice") == Node(name="Alice")
    assert Node.cast("Person", "Employee", name="Alice", age=33) == alice
    assert Node.cast({"name": "Alice"}) == Node(name="Alice")
    assert Node.cast(("Person", "Employee", {"name": "Alice", "age": 33})) == alice
    assert Node.cast(42) == NodePointer(42)
    assert Node.cast(NodePointer(42)) == NodePointer(42)


def test_rel_cast():
    knows = Rel("KNOWS", since=1999)
    assert Rel.cast() == Rel()
    assert Rel.cast(None) is None
    assert Rel.cast(knows) is knows
    assert Rel.cast("KNOWS") == Rel("KNOWS")
    assert Rel.cast(since=1999) == Rel(since=1999)
    assert Rel.cast("KNOWS", since=1999) == Rel("KNOWS", since=1999)
    assert Rel.cast({"since": 1999}) == Rel(since=1999)
    assert Rel.cast(("KNOWS", {"since": 1999})) == knows
    assert Rel.cast(Relationship({}, "KNOWS", {})) == Rel("KNOWS")
