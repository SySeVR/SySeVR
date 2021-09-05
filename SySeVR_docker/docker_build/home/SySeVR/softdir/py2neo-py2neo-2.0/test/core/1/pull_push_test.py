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


from py2neo.core import Node, Rel, Rev, Path


def test_can_pull_node(graph):
    if not graph.supports_node_labels:
        return
    local = Node()
    remote = Node("Person", name="Alice")
    graph.create(remote)
    assert local.labels == set()
    assert local.properties == {}
    local.bind(remote.uri)
    local.pull()
    assert local.labels == remote.labels
    assert local.properties == remote.properties


def test_can_pull_node_labels_only(graph):
    if not graph.supports_node_labels:
        return
    local = Node()
    remote = Node("Person")
    graph.create(remote)
    assert local.labels == set()
    local.bind(remote.uri)
    local.labels.pull()
    assert local.labels == remote.labels


def test_can_graph_pull_node(graph):
    if not graph.supports_node_labels:
        return
    local = Node()
    remote = Node("Person", name="Alice")
    graph.create(remote)
    assert local.labels == set()
    assert local.properties == {}
    local.bind(remote.uri)
    graph.pull(local)
    assert local.labels == remote.labels
    assert local.properties == remote.properties


def test_can_push_node(graph):
    if not graph.supports_node_labels:
        return
    local = Node("Person", name="Alice")
    remote = Node()
    graph.create(remote)
    assert remote.labels == set()
    assert remote.properties == {}
    local.bind(remote.uri)
    local.push()
    remote.pull()
    assert local.labels == remote.labels
    assert local.properties == remote.properties


def test_can_push_node_labels_only(graph):
    if not graph.supports_node_labels:
        return
    local = Node("Person")
    remote = Node()
    graph.create(remote)
    assert remote.labels == set()
    local.bind(remote.uri)
    local.labels.push()
    remote.labels.pull()
    assert local.labels == remote.labels


def test_can_graph_push_node(graph):
    if not graph.supports_node_labels:
        return
    local = Node("Person", name="Alice")
    remote = Node()
    graph.create(remote)
    assert remote.labels == set()
    assert remote.properties == {}
    local.bind(remote.uri)
    graph.push(local)
    graph.pull(remote)
    assert local.labels == remote.labels
    assert local.properties == remote.properties


def test_can_push_rel(graph):
    local = Rel("KNOWS", since=1999)
    remote = Rel("KNOWS")
    graph.create({}, {}, (0, remote, 1))
    assert remote.properties == {}
    local.bind(remote.uri)
    local.push()
    remote.pull()
    assert local.properties == remote.properties


def test_can_push_relationship(graph):
    local = Rel("KNOWS", since=1999)
    remote = Rel("KNOWS")
    a, b, ab = graph.create({}, {}, (0, remote, 1))
    assert ab.properties == {}
    local.bind(ab.uri)
    ab.push()
    local.pull()
    assert local.properties == remote.properties


def test_can_pull_path(graph):
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    carol = Node(name="Carol")
    dave = Node(name="Dave")
    path = Path(alice, "LOVES", bob, Rev("HATES"), carol, "KNOWS", dave)
    graph.create(path)
    assert path[0].properties["amount"] is None
    assert path[1].properties["amount"] is None
    assert path[2].properties["since"] is None
    assert path[0].rel.properties["amount"] is None
    assert path[1].rel.properties["amount"] is None
    assert path[2].rel.properties["since"] is None
    graph.cypher.run("""\
    START ab=rel({ab}), bc=rel({bc}), cd=rel({cd})
    SET ab.amount = "lots", bc.amount = "some", cd.since = 1999
    """, {"ab": path[0]._id, "bc": path[1]._id, "cd": path[2]._id})
    path.pull()
    assert path[0].properties["amount"] == "lots"
    assert path[1].properties["amount"] == "some"
    assert path[2].properties["since"] == 1999
    assert path[0].rel.properties["amount"] == "lots"
    assert path[1].rel.properties["amount"] == "some"
    assert path[2].rel.properties["since"] == 1999


def test_can_push_path(graph):
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    carol = Node(name="Carol")
    dave = Node(name="Dave")
    path = Path(alice, "LOVES", bob, Rev("HATES"), carol, "KNOWS", dave)
    graph.create(path)
    if graph.neo4j_version >= (2, 0, 0):
        query = """\
        START ab=rel({ab}), bc=rel({bc}), cd=rel({cd})
        RETURN ab.amount, bc.amount, cd.since
        """
    else:
        query = """\
        START ab=rel({ab}), bc=rel({bc}), cd=rel({cd})
        RETURN ab.amount?, bc.amount?, cd.since?
        """
    params = {"ab": path[0]._id, "bc": path[1]._id, "cd": path[2]._id}
    path[0].properties["amount"] = "lots"
    path[1].properties["amount"] = "some"
    path[2].properties["since"] = 1999
    results = graph.cypher.execute(query, params)
    ab_amount, bc_amount, cd_since = results[0]
    assert ab_amount is None
    assert bc_amount is None
    assert cd_since is None
    path.push()
    results = graph.cypher.execute(query, params)
    ab_amount, bc_amount, cd_since = results[0]
    assert ab_amount == "lots"
    assert bc_amount == "some"
    assert cd_since == 1999
