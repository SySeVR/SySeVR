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


from py2neo import Node, Relationship, Path, Rev
from py2neo.cypher.delete import DeleteStatement
from py2neo.cypher.error import CypherError


def test_deleting_nothing_does_nothing(graph):
    graph.delete()
    assert True


def test_can_delete_node(graph):
    alice = Node("Person", name="Alice")
    graph.create(alice)
    assert alice.exists
    statement = DeleteStatement(graph)
    statement.delete(alice)
    assert repr(statement) == "START _0=node({_0})\nDELETE _0"
    graph.delete(alice)
    assert not alice.exists


def test_can_delete_nodes_and_relationship_rel_first(graph):
    alice = Node("Person", name="Alice")
    bob = Node("Person", name="Bob")
    ab = Relationship(alice, "KNOWS", bob)
    graph.create(alice, bob, ab)
    assert alice.exists
    assert bob.exists
    assert ab.exists
    graph.delete(ab, alice, bob)
    assert not alice.exists
    assert not bob.exists
    assert not ab.exists


def test_can_delete_nodes_and_relationship_nodes_first(graph):
    alice = Node("Person", name="Alice")
    bob = Node("Person", name="Bob")
    ab = Relationship(alice, "KNOWS", bob)
    graph.create(alice, bob, ab)
    assert alice.exists
    assert bob.exists
    assert ab.exists
    graph.delete(alice, bob, ab)
    assert not alice.exists
    assert not bob.exists
    assert not ab.exists


def test_cannot_delete_related_node(graph):
    alice = Node("Person", name="Alice")
    bob = Node("Person", name="Bob")
    ab = Relationship(alice, "KNOWS", bob)
    graph.create(alice, bob, ab)
    assert alice.exists
    assert bob.exists
    assert ab.exists
    try:
        graph.delete(alice)
    except CypherError:
        assert True
    else:
        assert False
    finally:
        graph.delete(alice, bob, ab)


def test_can_delete_path(graph):
    path = Path({}, "LOVES", {}, Rev("HATES"), {}, "KNOWS", {})
    graph.create(path)
    assert path.exists
    graph.delete(path)
    assert not path.exists


def test_cannot_delete_other_types(graph):
    try:
        graph.delete("not a node or a relationship")
    except TypeError:
        assert True
    else:
        assert False
