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


from py2neo import Graph, Node, NodePointer, Rel, Rev, Path


def test_graph_hashes():
    assert hash(Graph()) == hash(Graph())


def test_node_hashes(graph):
    assert hash(Node()) == hash(Node())
    assert hash(Node(name="Alice")) == hash(Node(name="Alice"))
    assert hash(Node(name="Alice", age=33)) == hash(Node(age=33, name="Alice"))
    assert hash(Node("Person", name="Alice", age=33)) == hash(Node("Person", age=33, name="Alice"))
    node_1 = Node("Person", name="Alice")
    graph.create(node_1)
    node_2 = Node("Person", name="Alice")
    node_2.bind(node_1.uri)
    assert node_1 is not node_2
    assert hash(node_1) == hash(node_2)


def test_node_pointer_hashes():
    assert hash(NodePointer(42)) == hash(NodePointer(42))


def test_rel_and_rev_hashes(graph):
    assert hash(Rel("KNOWS")) == hash(Rel("KNOWS"))
    assert hash(Rel("KNOWS")) == -hash(Rev("KNOWS"))
    assert hash(Rel("KNOWS", well=True, since=1999)) == hash(Rel("KNOWS", since=1999, well=True))
    rel_1 = Node("KNOWS", since=1999)
    graph.create(rel_1)
    rel_2 = Node("KNOWS", since=1999)
    rel_2.bind(rel_1.uri)
    assert rel_1 is not rel_2
    assert hash(rel_1) == hash(rel_2)


def test_path_hashes(graph):
    p1 = Path(Node("Person", name="Alice"), Rel("KNOWS", since=1999), Node("Person", name="Bob"))
    p2 = Path(Node("Person", name="Alice"), Rel("KNOWS", since=1999), Node("Person", name="Bob"))
    assert hash(p1) == hash(p2)
    graph.create(p1)
    assert hash(p1) != hash(p2)
