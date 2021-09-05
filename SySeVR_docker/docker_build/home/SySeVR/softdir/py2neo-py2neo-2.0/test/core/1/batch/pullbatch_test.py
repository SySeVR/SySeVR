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


from py2neo import Node, Relationship
from py2neo.batch import PullBatch


def test_can_pull_node(graph):
    uri = graph.cypher.execute_one("CREATE (a {name:'Alice'}) RETURN a").uri
    alice = Node()
    alice.bind(uri)
    assert alice.properties["name"] is None
    batch = PullBatch(graph)
    batch.append(alice)
    batch.pull()
    assert alice.properties["name"] == "Alice"


def test_can_pull_node_with_label(graph):
    if not graph.supports_node_labels:
        return
    uri = graph.cypher.execute_one("CREATE (a:Person {name:'Alice'}) RETURN a").uri
    alice = Node()
    alice.bind(uri)
    assert "Person" not in alice.labels
    assert alice.properties["name"] is None
    batch = PullBatch(graph)
    batch.append(alice)
    batch.pull()
    assert "Person" in alice.labels
    assert alice.properties["name"] == "Alice"


def test_can_pull_relationship(graph):
    uri = graph.cypher.execute_one("CREATE ()-[ab:KNOWS {since:1999}]->() RETURN ab").uri
    ab = Relationship(None, "", None)
    ab.bind(uri)
    assert ab.type == ""
    assert ab.properties["since"] is None
    batch = PullBatch(graph)
    batch.append(ab)
    batch.pull()
    assert ab.type == "KNOWS"
    assert ab.properties["since"] == 1999


def test_can_pull_rel(graph):
    uri = graph.cypher.execute_one("CREATE ()-[ab:KNOWS {since:1999}]->() RETURN ab").uri
    ab = Relationship(None, "", None).rel
    ab.bind(uri)
    assert ab.type == ""
    assert ab.properties["since"] is None
    batch = PullBatch(graph)
    batch.append(ab)
    batch.pull()
    assert ab.type == "KNOWS"
    assert ab.properties["since"] == 1999


def test_can_pull_path(graph):
    path = graph.cypher.execute_one("CREATE p=()-[:KNOWS]->()-[:KNOWS]->() RETURN p")
    assert path.rels[0].properties["since"] is None
    graph.cypher.run("START ab=rel({ab}) SET ab.since=1999", {"ab": path.rels[0]._id})
    assert path.rels[0].properties["since"] is None
    batch = PullBatch(graph)
    batch.append(path)
    batch.pull()
    assert path.rels[0].properties["since"] == 1999


def test_cannot_pull_none(graph):
    batch = PullBatch(graph)
    try:
        batch.append(None)
    except TypeError:
        assert True
    else:
        assert False
