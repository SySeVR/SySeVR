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


from __future__ import unicode_literals

from py2neo import Node, NodePointer, Rel, Rev, Relationship, Path


def test_node_str(graph):
    node = Node("Person", name="Alice")
    assert str(node) == '(:Person {name:"Alice"})'
    graph.create(node)
    assert str(node) == '(n%s:Person {name:"Alice"})' % node._id


def test_node_pointer_str():
    pointer = NodePointer(3456)
    assert str(pointer) == "{3456}"


def test_relationship_str(graph):
    alice = Node("Person", name="Alice")
    bob = Node("Person", name="Bob")
    relationship = Relationship(alice, "KNOWS", bob)
    assert str(relationship) == '(:Person {name:"Alice"})-[:KNOWS]->(:Person {name:"Bob"})'
    graph.create(relationship)
    assert str(relationship) == \
        '(:Person {name:"Alice"})-[r%s:KNOWS]->(:Person {name:"Bob"})' % relationship._id


def test_rel_str(graph):
    alice = Node("Person", name="Alice")
    bob = Node("Person", name="Bob")
    relationship = Relationship(alice, "KNOWS", bob)
    graph.create(relationship)
    rel = relationship.rel
    assert str(rel) == '-[r%s:KNOWS]->' % rel._id


def test_unbound_rel_str():
    rel = Rel("KNOWS", since=1999)
    assert str(rel) == '-[:KNOWS {since:1999}]->'


def test_rev_str(graph):
    alice = Node("Person", name="Alice")
    bob = Node("Person", name="Bob")
    relationship = Relationship(alice, "KNOWS", bob)
    graph.create(relationship)
    rev = -relationship.rel
    assert str(rev) == '<-[r%s:KNOWS]-' % rev._id


def test_unbound_rev_str():
    rev = Rev("KNOWS", since=1999)
    assert str(rev) == '<-[:KNOWS {since:1999}]-'


def test_path_str(graph):
    alice = Node("Person", name="Alice")
    bob = Node("Person", name="Bob")
    path = Path(alice, "KNOWS", bob)
    assert str(path) == '(:Person {name:"Alice"})-[:KNOWS]->(:Person {name:"Bob"})'
    graph.create(path)
    assert str(path) == '(:Person {name:"Alice"})-[:KNOWS]->(:Person {name:"Bob"})'
